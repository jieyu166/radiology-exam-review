/* =====================================================
   scheduler/queue-mix.js — 今日佇列混排與新卡上限
   移植自 mcq-bank（MIT, Hsiehting Lin 2026）worker/lib/queue-mix.ts：
   learning 永遠優先；有到期卡時每 3 張到期插 1 張新卡；新卡每日預設 20、上限 200。
   ===================================================== */

window.RexScheduler = window.RexScheduler || {};
window.RexScheduler.queueMix = (function () {
  'use strict';

  const DEFAULT_NEW_PER_DAY = 20;
  const NEW_EVERY = 4;
  const MAX_NEW_PER_DAY = 200;

  /** @param s {served, learning, dueReview, newAvailable, newRemaining} → 'learning'|'due'|'new'|null */
  function pickNextKind(s) {
    if (s.learning > 0) return 'learning';
    const canNew = s.newAvailable > 0 && s.newRemaining > 0;
    if (s.dueReview <= 0) return canNew ? 'new' : null;
    if (canNew && (s.served + 1) % NEW_EVERY === 0) return 'new';
    return 'due';
  }

  function remainingNewToday(introducedToday, limit) {
    const cap = Number.isFinite(limit) && limit > 0 ? Math.floor(limit) : 0;
    return Math.max(0, cap - (Number.isFinite(introducedToday) ? introducedToday : 0));
  }

  function parseNewLimit(raw) {
    if (raw === undefined || raw === null || raw === '') return DEFAULT_NEW_PER_DAY;
    const n = Number(raw);
    if (Number.isFinite(n) && n >= 0) return Math.min(MAX_NEW_PER_DAY, Math.floor(n));
    return DEFAULT_NEW_PER_DAY;
  }

  /** Count questions whose first review log inside the day window was rated from state New (0). */
  function introducedToday(reviewLogs, window_) {
    const seen = new Set();
    const first = new Map();
    for (const log of reviewLogs || []) {
      if (!log || log.reviewedAt < window_.dayStart || log.reviewedAt >= window_.dayEnd) continue;
      const prev = first.get(log.questionId);
      if (!prev || log.reviewedAt < prev.reviewedAt) first.set(log.questionId, log);
    }
    for (const [qid, log] of first) if (log.state === 0) seen.add(qid);
    return seen.size;
  }

  return { DEFAULT_NEW_PER_DAY, NEW_EVERY, MAX_NEW_PER_DAY, pickNextKind, remainingNewToday, parseNewLimit, introducedToday };
})();
