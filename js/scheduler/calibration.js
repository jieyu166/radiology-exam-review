/* =====================================================
   scheduler/calibration.js — 答前信心校準與 hypercorrection 候選
   移植自 mcq-bank（MIT, Hsiehting Lin 2026）worker/lib/calibration.ts。
   confidence：1 猜、2 普通、3 有把握；只統計帶信心值的 attempts。
   ===================================================== */

window.RexScheduler = window.RexScheduler || {};
window.RexScheduler.calibration = (function () {
  'use strict';

  const LEVELS = [1, 2, 3];
  const LABELS = { 1: '猜', 2: '普通', 3: '有把握' };

  /** @returns [{confidence, n, correct, accuracy|null}] for levels 1..3 */
  function calibration(attempts) {
    const buckets = LEVELS.map(level => ({ confidence: level, label: LABELS[level], n: 0, correct: 0, accuracy: null }));
    for (const a of attempts || []) {
      if (!a || !LEVELS.includes(a.confidence)) continue;
      const b = buckets[a.confidence - 1];
      b.n++;
      if (a.isCorrect === true) b.correct++;
    }
    for (const b of buckets) b.accuracy = b.n ? b.correct / b.n : null;
    return buckets;
  }

  /** Most recent attempts rated 有把握 (3) but answered wrong — hypercorrection candidates. */
  function hypercorrectionCandidates(attempts, limit) {
    const max = Number.isFinite(limit) && limit > 0 ? Math.trunc(limit) : 20;
    return (attempts || [])
      .filter(a => a && a.confidence === 3 && a.isCorrect === false)
      .sort((a, b) => (b.clientTs || 0) - (a.clientTs || 0))
      .slice(0, max);
  }

  return { LEVELS, LABELS, calibration, hypercorrectionCandidates };
})();
