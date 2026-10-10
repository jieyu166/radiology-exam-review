/* =====================================================
   scheduler/fsrs-adapter.js — ts-fsrs 5.4.2（UMD 全域 FSRS）包裝
   cardRow 欄位全為 epoch 毫秒與數字，可直接存 localStorage / D1：
   { questionId, dueAt, stability, difficulty, elapsedDays, scheduledDays,
     learningSteps, reps, lapses, state, lastReviewAt, updatedAt }
   參數沿用 mcq-bank（MIT）：retention 0.9、max 36500、fuzz off、short-term on、
   learning 1m/10m、relearning 10m。FSRS 缺少時 available() 為 false，不丟錯。
   ===================================================== */

window.RexScheduler = window.RexScheduler || {};
window.RexScheduler.fsrs = (function () {
  'use strict';

  const PARAMS = {
    request_retention: 0.9,
    maximum_interval: 36500,
    enable_fuzz: false,
    enable_short_term: true,
    learning_steps: ['1m', '10m'],
    relearning_steps: ['10m'],
  };
  const RATINGS = ['again', 'hard', 'good', 'easy'];
  let scheduler = null;

  function lib() {
    return typeof FSRS !== 'undefined' && FSRS && typeof FSRS.fsrs === 'function' ? FSRS : null;
  }

  function available() {
    return !!lib();
  }

  function _scheduler() {
    const f = lib();
    if (!f) return null;
    if (!scheduler) scheduler = f.fsrs(typeof f.generatorParameters === 'function' ? f.generatorParameters(PARAMS) : PARAMS);
    return scheduler;
  }

  function ratingValue(rating) {
    const f = lib();
    const name = String(rating || '').toLowerCase();
    if (!f || !RATINGS.includes(name)) return null;
    return { again: f.Rating.Again, hard: f.Rating.Hard, good: f.Rating.Good, easy: f.Rating.Easy }[name];
  }

  function ratingName(value) {
    const f = lib();
    if (!f) return null;
    if (value === f.Rating.Again) return 'again';
    if (value === f.Rating.Hard) return 'hard';
    if (value === f.Rating.Good) return 'good';
    if (value === f.Rating.Easy) return 'easy';
    return null;
  }

  function rowToCard(row, now) {
    const f = lib();
    if (!row) return f.createEmptyCard(new Date(now));
    return {
      due: new Date(row.dueAt),
      stability: row.stability,
      difficulty: row.difficulty,
      elapsed_days: row.elapsedDays,
      scheduled_days: row.scheduledDays,
      learning_steps: row.learningSteps || 0,
      reps: row.reps,
      lapses: row.lapses,
      state: row.state,
      last_review: row.lastReviewAt == null ? undefined : new Date(row.lastReviewAt),
    };
  }

  function cardToRow(card, questionId, now) {
    return {
      questionId,
      dueAt: card.due.getTime(),
      stability: card.stability,
      difficulty: card.difficulty,
      elapsedDays: card.elapsed_days,
      scheduledDays: card.scheduled_days,
      learningSteps: card.learning_steps || 0,
      reps: card.reps,
      lapses: card.lapses,
      state: card.state,
      lastReviewAt: card.last_review ? card.last_review.getTime() : null,
      updatedAt: now,
    };
  }

  function createCard(questionId, now) {
    if (!available()) return null;
    return cardToRow(lib().createEmptyCard(new Date(now)), questionId, now);
  }

  /** Apply one grade. Returns {cardRow, log} or null when the library is missing / rating invalid. */
  function rate(row, questionId, now, rating) {
    const s = _scheduler();
    const grade = ratingValue(rating);
    if (!s || grade == null) return null;
    const before = row ? row.state : lib().State.New;
    const { card, log } = s.next(rowToCard(row, now), new Date(now), grade);
    return {
      cardRow: cardToRow(card, questionId, now),
      log: {
        questionId,
        rating: ratingName(grade),
        state: before,
        dueAt: card.due.getTime(),
        stability: log.stability,
        difficulty: log.difficulty,
        elapsedDays: log.elapsed_days,
        lastElapsedDays: log.last_elapsed_days,
        scheduledDays: log.scheduled_days,
        learningSteps: log.learning_steps || 0,
        reviewedAt: now,
      },
    };
  }

  /** Preview the four outcomes without mutating anything: {again, hard, good, easy} → {dueAt, scheduledDays, state}. */
  function preview(row, now) {
    const s = _scheduler();
    if (!s) return null;
    const result = s.repeat(rowToCard(row, now), new Date(now));
    const out = {};
    for (const name of RATINGS) {
      const item = result[ratingValue(name)];
      out[name] = { dueAt: item.card.due.getTime(), scheduledDays: item.card.scheduled_days, state: item.card.state };
    }
    return out;
  }

  function retrievability(row, now) {
    const s = _scheduler();
    if (!s || !row || row.lastReviewAt == null || row.state === lib().State.New) return null;
    try { return s.get_retrievability(rowToCard(row, now), new Date(now), false); } catch (e) { return null; }
  }

  /** Human label for a preview interval: `<1 分`, `10 分`, `3 天`, `1.5 月`. */
  function intervalLabel(dueAt, now) {
    const ms = Math.max(0, dueAt - now);
    const minutes = ms / 60000;
    if (minutes < 1) return '<1 分';
    if (minutes < 60) return `${Math.round(minutes)} 分`;
    const hours = minutes / 60;
    if (hours < 24) return `${Math.round(hours)} 小時`;
    const days = hours / 24;
    if (days < 30) return `${Math.round(days)} 天`;
    const months = days / 30;
    if (months < 12) return `${(Math.round(months * 10) / 10).toString().replace(/\.0$/, '')} 月`;
    return `${(Math.round(days / 365 * 10) / 10).toString().replace(/\.0$/, '')} 年`;
  }

  return { PARAMS, RATINGS, available, createCard, rate, preview, retrievability, intervalLabel, ratingValue, ratingName, _reset: () => { scheduler = null; } };
})();
