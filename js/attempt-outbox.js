/* =====================================================
   attempt-outbox.js — 離線佇列補送
   佇列本身存在 DataLoader 的 rex_progress.outbox（attempts / bookmarks / exams）。
   本模組負責：循序分批送出（每批 ≤ 40，首敗即停）、觸發點（啟動、online、
   回前景、pagehide）、訂閱待送筆數。沒有 session 時完全不送。
   flush 的傳輸函式由呼叫端注入（sync-client.js），以便測試。
   觸發點設計移植自 mcq-bank（MIT, Hsiehting Lin 2026）attemptFlusher.ts。
   ===================================================== */

const AttemptOutbox = (function () {
  'use strict';

  const BATCH = 40;
  const QUEUES = ['attempts', 'bookmarks', 'exams'];
  const KEY_FIELD = { attempts: 'clientId', bookmarks: 'questionId', exams: 'clientId' };

  let running = false;
  let transport = null;
  let store = null;
  const subscribers = new Set();

  function configure(options) {
    if (options && options.transport) transport = options.transport;
    if (options && options.store) store = options.store;
  }

  function _store() {
    if (store) return store;
    if (typeof DataLoader !== 'undefined') return DataLoader;
    return null;
  }

  function pendingCount() {
    const s = _store();
    if (!s) return 0;
    const outbox = s.getOutbox();
    return QUEUES.reduce((sum, name) => sum + ((outbox[name] || []).length), 0);
  }

  function subscribe(fn) {
    subscribers.add(fn);
    return () => subscribers.delete(fn);
  }

  function _notify() {
    const count = pendingCount();
    subscribers.forEach(fn => { try { fn(count); } catch (e) { /* ignore */ } });
  }

  function _chunks(list) {
    const out = [];
    for (let i = 0; i < list.length; i += BATCH) out.push(list.slice(i, i + BATCH));
    return out;
  }

  /**
   * 依佇列順序 attempts → bookmarks → exams 循序送出。
   * transport(queue, items) 回傳 Promise<{accepted: [...keys], invalid: [...keys]}>；
   * 丟出例外視為該批失敗，立即停止這次 flush（保留順序）。
   */
  async function flush() {
    const s = _store();
    if (running || !s || !transport) return { sent: 0, failed: 0, skipped: true };
    if (!s.getSession()) return { sent: 0, failed: 0, skipped: true };
    running = true;
    const result = { sent: 0, failed: 0, invalid: 0, skipped: false };
    try {
      for (const queue of QUEUES) {
        const items = (s.getOutbox()[queue] || []).slice();
        for (const chunk of _chunks(items)) {
          let response;
          try {
            response = await transport(queue, chunk);
          } catch (error) {
            result.failed += chunk.length;
            if (error && error.status === 401) s.clearSession();
            return result;
          }
          const keyField = KEY_FIELD[queue];
          const done = (response && response.accepted) || chunk.map(item => item[keyField]);
          const invalid = (response && response.invalid) || [];
          s.markSynced({ [queue]: done.concat(invalid) });
          result.sent += done.length;
          result.invalid += invalid.length;
          if (invalid.length) console.warn('[AttemptOutbox] dropped invalid items', queue, invalid);
        }
      }
      return result;
    } finally {
      running = false;
      _notify();
    }
  }

  let kickTimer = null;
  /** Debounced flush after a local write (answer, bookmark, exam); a no-op without a session. */
  function kick(delayMs) {
    const s = _store();
    if (!s || !s.getSession()) return;
    if (kickTimer) clearTimeout(kickTimer);
    kickTimer = setTimeout(() => { kickTimer = null; flush().catch(() => {}); }, Number.isFinite(delayMs) ? delayMs : 400);
  }

  let installed = false;
  function install(win) {
    const w = win || (typeof window !== 'undefined' ? window : null);
    if (installed || !w || typeof w.addEventListener !== 'function') return;
    installed = true;
    const kick = () => { flush().catch(() => {}); };
    w.addEventListener('online', kick);
    if (w.document && typeof w.document.addEventListener === 'function') {
      w.document.addEventListener('visibilitychange', () => { if (w.document.visibilityState === 'visible') kick(); });
    }
    w.addEventListener('pagehide', () => { if (pendingCount() > 0) kick(); });
    kick();
  }

  return { BATCH, configure, flush, kick, install, pendingCount, subscribe, _reset: () => { running = false; installed = false; } };
})();
