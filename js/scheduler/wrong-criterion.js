/* =====================================================
   scheduler/wrong-criterion.js — 錯題判準：「最近一次作答答錯」
   answers[<id>] 由最新 attempt 導出（data-loader.js），因此 correct === false 即最近一次答錯。
   全站（篩選、組卷 wrong 狀態、弱點分群）只用這一個定義。
   設計取自 mcq-bank（MIT, Hsiehting Lin 2026）worker/lib/wrong-criterion.ts。
   ===================================================== */

window.RexScheduler = window.RexScheduler || {};
window.RexScheduler.wrongCriterion = (function () {
  'use strict';

  function isWrong(answerEntry) {
    return !!answerEntry && answerEntry.correct === false;
  }

  function isCorrectLatest(answerEntry) {
    return !!answerEntry && answerEntry.correct === true;
  }

  /** Ids currently wrong, newest wrong first. */
  function wrongIds(progress) {
    const answers = (progress && progress.answers) || {};
    return Object.keys(answers)
      .filter(id => isWrong(answers[id]))
      .sort((a, b) => (answers[b].ts || 0) - (answers[a].ts || 0));
  }

  return { isWrong, isCorrectLatest, wrongIds };
})();
