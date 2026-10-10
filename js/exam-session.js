/* =====================================================
   exam-session.js — 模擬考 session 純函式狀態機（可持久化到 rex_progress.activeExam）
   組卷：RexScheduler.testBuilder（status OR × 維度 AND、seeded 抽樣）
   續考：RexScheduler.examResume（第一個未作答；全答完回 0）
   逾時：timed 模式倒數歸零 → 記為未作答並前進
   ===================================================== */

const ExamSession = (function () {
  'use strict';

  const EXPIRED = '∅';

  function _S() {
    return (typeof window !== 'undefined' && window.RexScheduler) || null;
  }

  /** Build a new session from index entries + progress + raw filters. */
  function start(input) {
    const S = _S();
    const filters = S.testBuilder.normalizeFilters(input.filters);
    const pool = S.testBuilder.buildPool(input.entries, input.progress, filters);
    const seed = Number.isFinite(input.seed) ? Math.trunc(input.seed) : (input.now % 2147483647);
    const entryIds = S.testBuilder.sample(pool, filters.count, seed);
    return {
      entryIds,
      answers: {},
      elapsed: {},
      index: 0,
      startedAt: input.now,
      filters,
      seed,
      secondsPerQuestion: filters.timed ? Math.max(0, Math.trunc(input.secondsPerQuestion || 0)) : 0,
      poolSize: pool.length,
    };
  }

  function poolSize(entries, progress, filters) {
    const S = _S();
    return S.testBuilder.buildPool(entries, progress, filters).length;
  }

  function answer(session, questionId, chosen, elapsedMs) {
    session.answers[questionId] = chosen || '';
    if (Number.isFinite(elapsedMs)) session.elapsed[questionId] = elapsedMs;
    return session;
  }

  /** Timed mode: countdown reached zero → record as unanswered and advance. */
  function expire(session, questionId) {
    if (session.answers[questionId] === undefined || session.answers[questionId] === '') session.answers[questionId] = EXPIRED;
    return advance(session);
  }

  function advance(session) {
    session.index = Math.min(session.index + 1, session.entryIds.length);
    return session;
  }

  function isFinished(session) {
    return session.index >= session.entryIds.length;
  }

  function currentId(session) {
    return session.entryIds[session.index] || null;
  }

  /** Index to resume at: first question with no answer and not expired; 0 when everything is answered. */
  function resumeIndex(session) {
    const S = _S();
    return S.examResume.resumeIndex(session.entryIds, session.answers);
  }

  /** Drop ids that no longer exist in the published index; returns the removed ids. */
  function pruneMissing(session, knownIds) {
    const known = new Set(knownIds);
    const removed = session.entryIds.filter(id => !known.has(id));
    if (removed.length) {
      session.entryIds = session.entryIds.filter(id => known.has(id));
      session.index = Math.min(session.index, session.entryIds.length);
    }
    return removed;
  }

  /** Answers suitable for scoring: expired / blank entries are omitted (counted as skipped). */
  function scoringAnswers(session) {
    const out = {};
    for (const id of session.entryIds) {
      const value = session.answers[id];
      if (value && value !== EXPIRED) out[id] = value;
    }
    return out;
  }

  function expiredIds(session) {
    return session.entryIds.filter(id => session.answers[id] === EXPIRED);
  }

  return { EXPIRED, start, poolSize, answer, expire, advance, isFinished, currentId, resumeIndex, pruneMissing, scoringAnswers, expiredIds };
})();
