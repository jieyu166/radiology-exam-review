/* =====================================================
   scheduler/exam-resume.js — 續考落點
   移植自 mcq-bank（MIT, Hsiehting Lin 2026）frontend/src/lib/examResume.ts：
   第一個未作答的題目索引；全部答完回 0。
   ===================================================== */

window.RexScheduler = window.RexScheduler || {};
window.RexScheduler.examResume = (function () {
  'use strict';

  /** @param entryIds string[]  @param answers {[id]: chosen} */
  function resumeIndex(entryIds, answers) {
    const a = answers || {};
    const ids = Array.isArray(entryIds) ? entryIds : [];
    const index = ids.findIndex(id => !a[id]);
    return index >= 0 ? index : 0;
  }

  return { resumeIndex };
})();
