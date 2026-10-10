/* =====================================================
   sync-client.js — rex-api 客戶端（Bearer token）
   登入／註冊／登出／me、outbox 傳輸、snapshot 下載與首次登入的 legacy 上傳。
   401 一律清除本機 session、保留 outbox。
   ===================================================== */

const SyncClient = (function () {
  'use strict';

  const QUEUE_PATH = { attempts: '/sync/attempts', cards: '/sync/cards', reviewLogs: '/sync/review-logs', bookmarks: '/sync/bookmarks', exams: '/sync/exams', settings: '/sync/settings' };
  const KEY_FIELD = { attempts: 'clientId', cards: 'questionId', reviewLogs: 'clientId', bookmarks: 'questionId', exams: 'clientId', settings: 'updatedAt' };
  const BATCH = 40;
  let _base = null;
  let _fetch = null;
  let _store = null;

  function configure(options) {
    if (options && typeof options.base === 'string') _base = options.base.replace(/\/+$/, '');
    if (options && typeof options.fetch === 'function') _fetch = options.fetch;
    if (options && options.store) _store = options.store;
  }

  function base() {
    if (_base) return _base;
    if (typeof window !== 'undefined' && typeof window.REX_API_BASE === 'string') return window.REX_API_BASE.replace(/\/+$/, '');
    return '';
  }

  function store() {
    return _store || (typeof DataLoader !== 'undefined' ? DataLoader : null);
  }

  function doFetch(url, init) {
    const impl = _fetch || (typeof fetch === 'function' ? fetch : null);
    if (!impl) throw new Error('fetch unavailable');
    return impl(url, init);
  }

  class ApiError extends Error {
    constructor(status, code, message, extra) { super(message || code || `HTTP ${status}`); this.status = status; this.code = code; this.extra = extra || null; }
  }

  async function request(method, path, options) {
    const opts = options || {};
    const headers = { Accept: 'application/json' };
    if (opts.body !== undefined) headers['Content-Type'] = 'application/json';
    if (opts.auth !== false) {
      const session = store() && store().getSession();
      if (session) headers.Authorization = `Bearer ${session.token}`;
      else if (opts.auth === true) throw new ApiError(401, 'no_session', '請先登入');
    }
    let response;
    try {
      response = await doFetch(base() + path, { method, headers, body: opts.body === undefined ? undefined : JSON.stringify(opts.body) });
    } catch (error) {
      throw new ApiError(0, 'network', '無法連線到同步伺服器');
    }
    let data = null;
    try { data = await response.json(); } catch (e) { data = null; }
    if (response.status === 401 && opts.auth !== false) {
      if (store()) store().clearSession();
      throw new ApiError(401, (data && data.error) || 'unauthorized', '登入已失效，請重新登入');
    }
    if (!response.ok) throw new ApiError(response.status, data && data.error, data && data.message, data);
    return data;
  }

  function _saveSession(data) {
    const session = { token: data.token, expiresAt: data.expiresAt, username: data.user && data.user.username, displayName: data.user && data.user.displayName, role: data.user && data.user.role };
    store().setSession(session);
    return session;
  }

  async function login(username, password) {
    const data = await request('POST', '/auth/login', { body: { username, password }, auth: false });
    return _saveSession(data);
  }

  async function register(username, password, inviteCode, displayName) {
    const data = await request('POST', '/auth/register', { body: { username, password, inviteCode, displayName }, auth: false });
    return _saveSession(data);
  }

  async function logout() {
    try { await request('POST', '/auth/logout', { auth: true }); } catch (e) { /* session may already be gone */ }
    if (store()) store().clearSession();
  }

  function me() {
    return request('GET', '/auth/me', { auth: true });
  }

  /** AttemptOutbox transport: posts one batch, resolves {accepted, invalid}; invalid items are dropped after a retry without them. */
  async function transport(queue, items) {
    const path = QUEUE_PATH[queue];
    const keyField = KEY_FIELD[queue];
    if (!path) throw new Error('unknown queue ' + queue);
    try {
      const data = await request('POST', path, { body: { items }, auth: true });
      return { accepted: data.acceptedIds || items.map(item => item[keyField]), invalid: [] };
    } catch (error) {
      if (error.status !== 400 || !error.extra || !Array.isArray(error.extra.errors)) throw error;
      const badIndexes = new Set(error.extra.errors.map(e => e.index));
      const invalid = items.filter((_, index) => badIndexes.has(index)).map(item => item[keyField]);
      const valid = items.filter((_, index) => !badIndexes.has(index));
      console.warn('[SyncClient] invalid items dropped', queue, error.extra.errors);
      if (!valid.length) return { accepted: [], invalid };
      const data = await request('POST', path, { body: { items: valid }, auth: true });
      return { accepted: data.acceptedIds || valid.map(item => item[keyField]), invalid };
    }
  }

  async function pushOutbox() {
    if (typeof AttemptOutbox === 'undefined') return { sent: 0, failed: 0, skipped: true };
    return AttemptOutbox.flush();
  }

  async function pullSnapshot() {
    const s = store();
    const sync = s.getProgress().sync;
    const snapshot = await request('GET', `/sync/snapshot?sinceAttemptId=${encodeURIComponent(sync.latestAttemptId || 0)}&sinceReviewLogId=${encodeURIComponent(sync.latestReviewLogId || 0)}`, { auth: true });
    return s.mergeSnapshot(snapshot);
  }

  /** Upload every local attempt/exam/bookmark not yet known to the server (first login or imported data), in batches of 40. */
  async function uploadUnsynced() {
    const s = store();
    const progress = s.getProgress();
    const result = { attempts: 0, exams: 0, bookmarks: 0 };
    const attempts = progress.attempts.filter(a => a.serverId == null && a.synced !== true);
    for (let i = 0; i < attempts.length; i += BATCH) {
      const chunk = attempts.slice(i, i + BATCH);
      const data = await request('POST', QUEUE_PATH.attempts, { body: { items: chunk }, auth: true });
      result.attempts += data.accepted || 0;
      s.markSynced({ attempts: chunk.map(a => a.clientId) });
    }
    const exams = progress.examHistory;
    for (let i = 0; i < exams.length; i += BATCH) {
      const chunk = exams.slice(i, i + BATCH);
      const data = await request('POST', QUEUE_PATH.exams, { body: { items: chunk }, auth: true });
      result.exams += data.accepted || 0;
      s.markSynced({ exams: chunk.map(e => e.clientId) });
    }
    const bookmarks = Object.keys(progress.bookmarks).map(id => ({ questionId: id, starred: progress.bookmarks[id].starred === true, updatedAt: progress.bookmarks[id].updatedAt || 0 }));
    for (let i = 0; i < bookmarks.length; i += BATCH) {
      const chunk = bookmarks.slice(i, i + BATCH);
      const data = await request('POST', QUEUE_PATH.bookmarks, { body: { items: chunk }, auth: true });
      result.bookmarks += data.accepted || 0;
      s.markSynced({ bookmarks: chunk.map(b => b.questionId) });
    }
    result.cards = 0;
    const cards = Object.values(progress.cards || {});
    for (let i = 0; i < cards.length; i += BATCH) {
      const chunk = cards.slice(i, i + BATCH);
      const data = await request('POST', QUEUE_PATH.cards, { body: { items: chunk }, auth: true });
      result.cards += data.accepted || 0;
      s.markSynced({ cards: chunk.map(c => c.questionId) });
    }
    result.reviewLogs = 0;
    const logs = (progress.reviewLogs || []).filter(l => l.serverId == null);
    for (let i = 0; i < logs.length; i += BATCH) {
      const chunk = logs.slice(i, i + BATCH);
      const data = await request('POST', QUEUE_PATH.reviewLogs, { body: { items: chunk }, auth: true });
      result.reviewLogs += data.accepted || 0;
      s.markSynced({ reviewLogs: chunk.map(l => l.clientId) });
    }
    if (progress.settings && progress.settings.updatedAt > 0) {
      await request('POST', QUEUE_PATH.settings, { body: { items: [progress.settings] }, auth: true });
      s.markSynced({ settings: true });
    }
    return result;
  }

  /** First login on a device: push everything local (including v2 legacy events) then pull the server snapshot. */
  async function afterLogin() {
    const s = store();
    const uploaded = await uploadUnsynced();
    const merged = await pullSnapshot();
    s.setMigratedLegacy(true);
    return { uploaded, merged };
  }

  function status() {
    const s = store();
    const session = s ? s.getSession() : null;
    const progress = s ? s.getProgress() : null;
    const outbox = progress ? progress.outbox : { attempts: [], bookmarks: [], exams: [] };
    return {
      loggedIn: !!session,
      username: session ? session.username : null,
      role: session ? session.role : null,
      pending: outbox.attempts.length + outbox.bookmarks.length + outbox.exams.length,
      lastSyncAt: progress ? progress.sync.lastSyncAt : null,
    };
  }

  async function createInvite(note) {
    return request('POST', '/admin/invites', { body: { note: note || '' }, auth: true });
  }

  return { configure, request, login, register, logout, me, transport, pushOutbox, pullSnapshot, uploadUnsynced, afterLogin, status, createInvite, ApiError, BATCH };
})();
