/* =====================================================
   data-loader.js — 學習進度（localStorage）與舊編輯匯出
   內容本體由 content-store.js 從 vault 產出的靜態檔載入；
   本模組只負責 rex_progress（schema v3）、rex_session 與 rex_edits_* 匯出。

   schema v3：
     attempts[]  append-only 作答事件（clientId 冪等鍵），answers 由最新事件導出
     bookmarks{} 收藏（updatedAt 新者勝），starred 由 bookmarks 導出
     outbox{}    待同步佇列（attempts / bookmarks / exams）
     sync{}      同步游標與狀態
   ===================================================== */

const DataLoader = (function () {
  'use strict';

  const PROGRESS_KEY = 'rex_progress';
  const SESSION_KEY = 'rex_session';
  const PROGRESS_VERSION = 3;
  const MAX_ATTEMPTS = 5000;
  const MAX_OUTBOX_ATTEMPTS = 300;
  const LETTERS = ['A', 'B', 'C', 'D', 'E'];
  const SOURCES = ['card', 'exam', 'legacy'];

  function _uuid() {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0;
      return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
    });
  }

  function _isObject(value) {
    return !!value && typeof value === 'object' && !Array.isArray(value);
  }

  function _int(value, fallback) {
    return Number.isFinite(value) ? Math.trunc(value) : fallback;
  }

  /* ── attempt 正規化 ── */
  function _normalizeAttempt(raw) {
    if (!_isObject(raw) || typeof raw.questionId !== 'string' || !raw.questionId) return null;
    const chosen = typeof raw.chosen === 'string' && LETTERS.includes(raw.chosen.toUpperCase()) ? raw.chosen.toUpperCase() : null;
    const confidence = [1, 2, 3].includes(raw.confidence) ? raw.confidence : null;
    const elapsedMs = Number.isFinite(raw.elapsedMs) ? Math.min(Math.max(Math.trunc(raw.elapsedMs), 0), 1800000) : null;
    const clientTs = _int(raw.clientTs, Date.now());
    return {
      clientId: typeof raw.clientId === 'string' && raw.clientId ? raw.clientId : _uuid(),
      questionId: raw.questionId,
      chosen,
      isCorrect: raw.isCorrect === true ? true : (raw.isCorrect === false ? false : null),
      source: SOURCES.includes(raw.source) ? raw.source : 'card',
      elapsedMs,
      confidence,
      sourceSha256: typeof raw.sourceSha256 === 'string' ? raw.sourceSha256 : null,
      clientTs,
      serverId: Number.isFinite(raw.serverId) ? raw.serverId : (Number.isFinite(raw.id) ? raw.id : null),
      synced: raw.synced === true || Number.isFinite(raw.serverId) || Number.isFinite(raw.id),
    };
  }

  function _legacyAttempt(id, value) {
    const ts = _int(value && value.ts, 0);
    return _normalizeAttempt({
      clientId: `legacy:${id}:${ts}`,
      questionId: id,
      chosen: value && value.last,
      isCorrect: !!(value && value.correct === true),
      source: 'legacy',
      elapsedMs: null,
      confidence: null,
      sourceSha256: value && value.sourceSha256,
      clientTs: ts,
    });
  }

  function _normalizeExam(item) {
    if (!_isObject(item)) return null;
    const ts = _int(item.ts, _int(item.clientTs, Date.now()));
    return Object.assign({}, item, {
      clientId: typeof item.clientId === 'string' && item.clientId ? item.clientId : `legacy-exam:${ts}`,
      ts,
      sourceSha256ByQuestion: item.sourceSha256ByQuestion || item.questionSourceSha256 || null,
    });
  }

  function _dedupeByClientId(items, normalize) {
    const seen = new Map();
    for (const raw of items || []) {
      const item = normalize(raw);
      if (!item) continue;
      if (!seen.has(item.clientId)) seen.set(item.clientId, item);
    }
    return Array.from(seen.values());
  }

  function _deriveAnswers(attempts) {
    const answers = {};
    const latestTs = {};
    attempts.forEach((attempt, index) => {
      const key = attempt.questionId;
      const rank = attempt.clientTs * 1e6 + index;
      if (latestTs[key] != null && rank < latestTs[key]) return;
      latestTs[key] = rank;
      answers[key] = { last: attempt.chosen, correct: attempt.isCorrect === true, ts: attempt.clientTs, sourceSha256: attempt.sourceSha256, clientId: attempt.clientId };
    });
    return answers;
  }

  function _emptyProgress() {
    return {
      schemaVersion: PROGRESS_VERSION,
      seen: {},
      starred: {},
      bookmarks: {},
      answers: {},
      examHistory: [],
      attempts: [],
      outbox: { attempts: [], bookmarks: [], exams: [] },
      sync: { latestAttemptId: 0, lastSyncAt: null, migratedLegacy: false },
    };
  }

  function _normalizeProgress(raw) {
    const base = _emptyProgress();
    if (!_isObject(raw)) return base;

    let attempts = _dedupeByClientId(Array.isArray(raw.attempts) ? raw.attempts : [], _normalizeAttempt);
    const known = new Set(attempts.map(a => a.clientId));
    // v2（或任何只有 answers 的資料）：確定性轉成 legacy attempts
    if (_isObject(raw.answers)) {
      Object.keys(raw.answers).forEach(id => {
        const value = raw.answers[id];
        if (!_isObject(value) || value.clientId) return; // v3 導出的 answers 帶 clientId，不再轉換
        const attempt = _legacyAttempt(id, value);
        if (attempt && !known.has(attempt.clientId)) { attempts.push(attempt); known.add(attempt.clientId); }
      });
    }
    attempts.sort((a, b) => a.clientTs - b.clientTs);
    if (attempts.length > MAX_ATTEMPTS) attempts = attempts.slice(attempts.length - MAX_ATTEMPTS);

    const bookmarks = {};
    if (_isObject(raw.bookmarks)) {
      Object.keys(raw.bookmarks).forEach(id => {
        const value = raw.bookmarks[id];
        if (!_isObject(value)) return;
        bookmarks[id] = { starred: value.starred === true, updatedAt: _int(value.updatedAt, 0) };
      });
    }
    if (_isObject(raw.starred)) {
      Object.keys(raw.starred).forEach(id => {
        if (raw.starred[id] !== true || bookmarks[id]) return;
        bookmarks[id] = { starred: true, updatedAt: 0 };
      });
    }
    const starred = {};
    Object.keys(bookmarks).forEach(id => { if (bookmarks[id].starred) starred[id] = true; });

    const examHistory = _dedupeByClientId(Array.isArray(raw.examHistory) ? raw.examHistory : [], _normalizeExam)
      .sort((a, b) => (b.ts || 0) - (a.ts || 0));

    const rawOutbox = _isObject(raw.outbox) ? raw.outbox : {};
    const outbox = {
      attempts: _dedupeByClientId(Array.isArray(rawOutbox.attempts) ? rawOutbox.attempts : [], _normalizeAttempt).slice(-MAX_OUTBOX_ATTEMPTS),
      bookmarks: (Array.isArray(rawOutbox.bookmarks) ? rawOutbox.bookmarks : []).filter(item => _isObject(item) && typeof item.questionId === 'string'),
      exams: _dedupeByClientId(Array.isArray(rawOutbox.exams) ? rawOutbox.exams : [], _normalizeExam),
    };
    const rawSync = _isObject(raw.sync) ? raw.sync : {};

    return {
      schemaVersion: PROGRESS_VERSION,
      seen: _isObject(raw.seen) ? raw.seen : {},
      starred,
      bookmarks,
      answers: _deriveAnswers(attempts),
      examHistory,
      attempts,
      outbox,
      sync: {
        latestAttemptId: _int(rawSync.latestAttemptId, 0),
        lastSyncAt: Number.isFinite(rawSync.lastSyncAt) ? rawSync.lastSyncAt : null,
        migratedLegacy: rawSync.migratedLegacy === true,
      },
    };
  }

  function _saveProgress(progress) {
    try {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(_normalizeProgress(progress)));
      return true;
    } catch (e) {
      console.warn('[DataLoader] rex_progress write error', e);
      return false;
    }
  }

  function getProgress() {
    try {
      const raw = localStorage.getItem(PROGRESS_KEY);
      return raw ? _normalizeProgress(JSON.parse(raw)) : _emptyProgress();
    } catch (e) {
      console.warn('[DataLoader] rex_progress parse error', e);
      return _emptyProgress();
    }
  }

  function _pushOutbox(progress, queue, item, key) {
    const list = progress.outbox[queue];
    const index = list.findIndex(existing => existing[key] === item[key]);
    if (index >= 0) list.splice(index, 1);
    list.push(item);
  }

  function markSeen(id) {
    if (!id) return;
    const progress = getProgress();
    progress.seen[id] = Date.now();
    _saveProgress(progress);
  }

  function toggleStar(id) {
    if (!id) return false;
    const progress = getProgress();
    const next = progress.starred[id] !== true;
    const entry = { questionId: id, starred: next, updatedAt: Date.now() };
    progress.bookmarks[id] = { starred: next, updatedAt: entry.updatedAt };
    _pushOutbox(progress, 'bookmarks', entry, 'questionId');
    _saveProgress(progress);
    return next;
  }

  function isStarred(id) {
    return getProgress().starred[id] === true;
  }

  function recordAttempt(raw) {
    const attempt = _normalizeAttempt(raw);
    if (!attempt) return null;
    const progress = getProgress();
    if (progress.attempts.some(existing => existing.clientId === attempt.clientId)) return attempt;
    progress.attempts.push(attempt);
    _pushOutbox(progress, 'attempts', attempt, 'clientId');
    _saveProgress(progress);
    return attempt;
  }

  function recordAnswer(id, result) {
    if (!id || !result) return null;
    return recordAttempt({
      clientId: result.clientId,
      questionId: id,
      chosen: result.chosen || null,
      isCorrect: result.correct === true,
      source: result.source || 'card',
      elapsedMs: Number.isFinite(result.elapsedMs) ? result.elapsedMs : null,
      confidence: result.confidence,
      sourceSha256: result.sourceSha256 || null,
      clientTs: Number.isFinite(result.clientTs) ? result.clientTs : Date.now(),
    });
  }

  function addExamRecord(record) {
    if (!_isObject(record)) return null;
    const progress = getProgress();
    const item = _normalizeExam(Object.assign({ ts: Date.now(), clientId: _uuid(), sourceSha256ByQuestion: null }, record));
    if (progress.examHistory.some(existing => existing.clientId === item.clientId)) return item;
    progress.examHistory = [item].concat(progress.examHistory || []);
    _pushOutbox(progress, 'exams', item, 'clientId');
    _saveProgress(progress);
    return item;
  }

  function getAttempts() {
    return getProgress().attempts;
  }

  function getOutbox() {
    return getProgress().outbox;
  }

  function markSynced(done) {
    const progress = getProgress();
    const ids = {
      attempts: new Set((done && done.attempts) || []),
      bookmarks: new Set((done && done.bookmarks) || []),
      exams: new Set((done && done.exams) || []),
    };
    progress.outbox.attempts = progress.outbox.attempts.filter(item => !ids.attempts.has(item.clientId));
    progress.attempts.forEach(item => { if (ids.attempts.has(item.clientId)) item.synced = true; });
    progress.outbox.bookmarks = progress.outbox.bookmarks.filter(item => !ids.bookmarks.has(item.questionId));
    progress.outbox.exams = progress.outbox.exams.filter(item => !ids.exams.has(item.clientId));
    progress.sync.lastSyncAt = Date.now();
    _saveProgress(progress);
    return progress.outbox;
  }

  function _mergeInto(progress, incoming, enqueue) {
    const stats = { seen: 0, starred: 0, answers: 0, examHistory: 0 };
    const known = new Map(progress.attempts.map(a => [a.clientId, a]));
    for (const attempt of incoming.attempts || []) {
      const item = _normalizeAttempt(attempt);
      if (!item) continue;
      const existing = known.get(item.clientId);
      if (existing) {
        if (existing.serverId == null && item.serverId != null) existing.serverId = item.serverId;
        continue;
      }
      progress.attempts.push(item);
      known.set(item.clientId, item);
      stats.answers++;
      if (enqueue) _pushOutbox(progress, 'attempts', item, 'clientId');
    }
    for (const [id, ts] of Object.entries(incoming.seen || {})) {
      if (!Object.prototype.hasOwnProperty.call(progress.seen, id)) stats.seen++;
      progress.seen[id] = ts;
    }
    for (const [id, value] of Object.entries(incoming.bookmarks || {})) {
      const current = progress.bookmarks[id];
      if (current && current.updatedAt >= (value.updatedAt || 0) && !(value.updatedAt === 0 && current.updatedAt === 0)) continue;
      if (!current || current.starred !== value.starred) stats.starred++;
      progress.bookmarks[id] = { starred: value.starred === true, updatedAt: _int(value.updatedAt, 0) };
      if (enqueue) _pushOutbox(progress, 'bookmarks', { questionId: id, starred: value.starred === true, updatedAt: _int(value.updatedAt, 0) }, 'questionId');
    }
    const knownExams = new Set(progress.examHistory.map(r => r.clientId));
    for (const raw of incoming.examHistory || []) {
      const item = _normalizeExam(raw);
      if (!item || knownExams.has(item.clientId)) continue;
      progress.examHistory.push(item);
      knownExams.add(item.clientId);
      stats.examHistory++;
      if (enqueue) _pushOutbox(progress, 'exams', item, 'clientId');
    }
    return stats;
  }

  function mergeSnapshot(snapshot) {
    if (!_isObject(snapshot)) return null;
    const progress = getProgress();
    const incoming = {
      attempts: snapshot.attempts || [],
      bookmarks: {},
      examHistory: snapshot.exams || snapshot.examHistory || [],
    };
    for (const item of snapshot.bookmarks || []) {
      if (_isObject(item) && typeof item.questionId === 'string') incoming.bookmarks[item.questionId] = { starred: item.starred === true, updatedAt: _int(item.updatedAt, 0) };
    }
    const stats = _mergeInto(progress, incoming, false);
    if (Number.isFinite(snapshot.latestAttemptId)) progress.sync.latestAttemptId = Math.max(progress.sync.latestAttemptId, snapshot.latestAttemptId);
    progress.sync.lastSyncAt = Date.now();
    _saveProgress(progress);
    return stats;
  }

  function setMigratedLegacy(flag) {
    const progress = getProgress();
    progress.sync.migratedLegacy = flag !== false;
    _saveProgress(progress);
  }

  function exportProgress() {
    return { rex_progress: getProgress() };
  }

  function importProgress(obj) {
    const incoming = _normalizeProgress(obj && obj.rex_progress ? obj.rex_progress : obj);
    const progress = getProgress();
    const stats = _mergeInto(progress, incoming, !!getSession());
    _saveProgress(progress);
    return stats;
  }

  function clearProgress() {
    localStorage.removeItem(PROGRESS_KEY);
  }

  /* ── session（Bearer token；只放 localStorage，匯出時不包含） ── */
  function getSession() {
    try {
      const raw = localStorage.getItem(SESSION_KEY);
      const session = raw ? JSON.parse(raw) : null;
      if (!_isObject(session) || typeof session.token !== 'string' || !session.token) return null;
      if (Number.isFinite(session.expiresAt) && session.expiresAt < Date.now()) return null;
      return session;
    } catch (e) {
      return null;
    }
  }

  function setSession(session) {
    try {
      if (!_isObject(session) || !session.token) { localStorage.removeItem(SESSION_KEY); return false; }
      localStorage.setItem(SESSION_KEY, JSON.stringify(session));
      return true;
    } catch (e) {
      console.warn('[DataLoader] rex_session write error', e);
      return false;
    }
  }

  function clearSession() {
    try { localStorage.removeItem(SESSION_KEY); } catch (e) { /* ignore */ }
  }

  /* ── 匯出舊版編輯差異（localStorage 的 rex_edits_*；內容已唯讀，僅供搬遷） ── */
  function exportAllEdits() {
    const result = {};
    const keys = Object.keys(localStorage).filter(k => k.startsWith('rex_edits_'));
    for (const k of keys) {
      try {
        result[k] = JSON.parse(localStorage.getItem(k) || '{}');
      } catch (e) { /* skip */ }
    }
    return result;
  }

  return {
    PROGRESS_VERSION,
    getProgress,
    markSeen,
    toggleStar,
    isStarred,
    recordAnswer,
    recordAttempt,
    addExamRecord,
    getAttempts,
    getOutbox,
    markSynced,
    mergeSnapshot,
    setMigratedLegacy,
    exportProgress,
    importProgress,
    clearProgress,
    getSession,
    setSession,
    clearSession,
    exportAllEdits,
    exportLegacyEdits: exportAllEdits,
  };
})();
