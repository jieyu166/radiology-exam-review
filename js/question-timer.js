/* =====================================================
   question-timer.js — 單題計時純函式狀態機
   只累計頁面可見的區間；超過 10 分鐘視為 outlier（顯示 10:00+）。
   時間一律由呼叫端傳入（now），便於測試。
   移植自 mcq-bank（MIT, Hsiehting Lin 2026）frontend/src/lib/questionTimer.ts。
   ===================================================== */

const QuestionTimer = (function () {
  'use strict';

  const MAX_QUESTION_MS = 10 * 60 * 1000;

  function startTimer(now) {
    return { accumulatedMs: 0, runningSince: now };
  }

  function stop(state, now) {
    if (!state || state.runningSince == null) return state || { accumulatedMs: 0, runningSince: null };
    return { accumulatedMs: state.accumulatedMs + Math.max(0, now - state.runningSince), runningSince: null };
  }

  function start(state, now) {
    if (!state) return startTimer(now);
    if (state.runningSince != null) return state;
    return { accumulatedMs: state.accumulatedMs, runningSince: now };
  }

  function read(state, now) {
    if (!state) return { elapsedMs: 0, outlier: false };
    const raw = state.accumulatedMs + (state.runningSince != null ? Math.max(0, now - state.runningSince) : 0);
    return { elapsedMs: Math.min(raw, MAX_QUESTION_MS), outlier: raw > MAX_QUESTION_MS };
  }

  function formatElapsed(ms, outlier) {
    const total = Math.max(0, Math.floor((Number.isFinite(ms) ? ms : 0) / 1000));
    const minutes = Math.floor(total / 60);
    const seconds = String(total % 60).padStart(2, '0');
    return `${minutes}:${seconds}${outlier ? '+' : ''}`;
  }

  return {
    MAX_QUESTION_MS,
    startTimer,
    hide: stop,
    pause: stop,
    show: start,
    resume: start,
    read,
    formatElapsed,
  };
})();
