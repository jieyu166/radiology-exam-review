/* =====================================================
   scheduler/due-window.js — 學習日界（固定 UTC+8，預設凌晨 4 點）
   移植自 mcq-bank（MIT, Hsiehting Lin 2026）worker/lib/due-window.ts。
   state：0 New、1 Learning、2 Review、3 Relearning（ts-fsrs State）
   ===================================================== */

window.RexScheduler = window.RexScheduler || {};
window.RexScheduler.dueWindow = (function () {
  'use strict';

  const TZ_OFFSET_MS = 8 * 3600 * 1000;
  const DEFAULT_DAY_START_HOUR = 4;
  const DAY_MS = 86400000;

  function clampHour(h) {
    const n = Number(h);
    return Number.isFinite(n) && n >= 0 && n <= 23 ? Math.floor(n) : DEFAULT_DAY_START_HOUR;
  }

  /** @returns {{dayStart:number, dayEnd:number, dayKey:string}} */
  function dayWindow(now, options) {
    const hour = clampHour(options && options.dayStartHour);
    const shift = TZ_OFFSET_MS - hour * 3600000;
    const dayIndex = Math.floor((now + shift) / DAY_MS);
    return {
      dayStart: dayIndex * DAY_MS - shift,
      dayEnd: (dayIndex + 1) * DAY_MS - shift,
      dayKey: new Date(dayIndex * DAY_MS).toISOString().slice(0, 10),
    };
  }

  /** New/no card → true; Learning/Relearning only when due now; Review when due by end of the study day. */
  function isDueToday(card, now, window_) {
    if (!card || card.state === 0) return true;
    if (card.state === 1 || card.state === 3) return card.dueAt <= now;
    return card.dueAt <= window_.dayEnd;
  }

  return { TZ_OFFSET_MS, DEFAULT_DAY_START_HOUR, DAY_MS, clampHour, dayWindow, isDueToday };
})();
