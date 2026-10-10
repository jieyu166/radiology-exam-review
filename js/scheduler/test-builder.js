/* =====================================================
   scheduler/test-builder.js — 模擬考組卷：條件正規化、題池、seeded 抽樣
   語意移植自 mcq-bank（MIT, Hsiehting Lin 2026）worker/lib/testBuilder.ts：
   status 之間 OR、維度之間 AND、空陣列 = 不限、count 1–100 預設 20、
   tutor 需 === true、timed 非 === false 即真。
   ===================================================== */

window.RexScheduler = window.RexScheduler || {};
window.RexScheduler.testBuilder = (function () {
  'use strict';

  const STATUSES = ['unseen', 'wrong', 'correct', 'bookmarked'];
  const DEFAULT_COUNT = 20;
  const MAX_COUNT = 100;

  function _strings(list) {
    if (!Array.isArray(list)) return [];
    const out = [];
    for (const item of list) {
      const value = String(item == null ? '' : item).trim();
      if (value && !out.includes(value)) out.push(value);
    }
    return out;
  }

  function _numbers(list) {
    if (!Array.isArray(list)) return [];
    const out = [];
    for (const item of list) {
      const n = Math.trunc(Number(item));
      if (Number.isFinite(n) && !out.includes(n)) out.push(n);
    }
    return out;
  }

  function normalizeFilters(raw) {
    const r = raw || {};
    const count = Math.trunc(Number(r.count));
    return {
      status: _strings(r.status).filter(s => STATUSES.includes(s)),
      years: _numbers(r.years),
      subspecialties: _strings(r.subspecialties),
      concepts: _strings(r.concepts),
      count: Number.isFinite(count) ? Math.min(MAX_COUNT, Math.max(1, count)) : DEFAULT_COUNT,
      tutor: r.tutor === true,
      timed: r.timed !== false,
    };
  }

  /** Question entries may carry one subspecialty (string) or several (list). */
  function _subs(entry) {
    const value = entry.subspecialty;
    if (Array.isArray(value)) return value.map(v => String(v)).filter(Boolean);
    return value ? [String(value)] : [];
  }

  function _years(entry) {
    const years = Array.isArray(entry.years) ? entry.years : (entry.year == null ? [] : [entry.year]);
    return years.map(v => Math.trunc(Number(v)));
  }

  function _matchesStatus(entry, filters, progress, wrongFn) {
    if (!filters.status.length) return true;
    const answer = progress.answers[entry.id];
    for (const status of filters.status) {
      if (status === 'unseen' && !answer) return true;
      if (status === 'wrong' && wrongFn(answer)) return true;
      if (status === 'correct' && answer && answer.correct === true) return true;
      if (status === 'bookmarked' && progress.starred[entry.id] === true) return true;
    }
    return false;
  }

  /** entries: indexes/questions.json entries; progress: DataLoader.getProgress(); returns ids in index order. */
  function buildPool(entries, progress, rawFilters) {
    const filters = normalizeFilters(rawFilters);
    const p = progress || { answers: {}, starred: {} };
    const wc = window.RexScheduler.wrongCriterion;
    const wrongFn = wc ? wc.isWrong : (a => !!a && a.correct === false);
    return (entries || []).filter(entry => {
      if (entry.scorable === false) return false;
      if (filters.years.length && !_years(entry).some(y => filters.years.includes(y))) return false;
      if (filters.subspecialties.length && !_subs(entry).some(s => filters.subspecialties.includes(s))) return false;
      if (filters.concepts.length && !(entry.conceptIds || []).some(c => filters.concepts.includes(c))) return false;
      return _matchesStatus(entry, filters, p, wrongFn);
    }).map(entry => entry.id);
  }

  function seededShuffle(arr, seed) {
    const out = arr.slice();
    let s = (seed >>> 0) || 1;
    for (let i = out.length - 1; i > 0; i--) {
      s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
      const j = s % (i + 1);
      const t = out[i]; out[i] = out[j]; out[j] = t;
    }
    return out;
  }

  /** Deterministic sample of `count` ids from the pool for the given seed. */
  function sample(pool, count, seed) {
    const n = Math.min(Math.max(1, Math.trunc(count) || DEFAULT_COUNT), MAX_COUNT, pool.length);
    return seededShuffle(pool, seed).slice(0, n);
  }

  return { STATUSES, DEFAULT_COUNT, MAX_COUNT, normalizeFilters, buildPool, seededShuffle, sample, subspecialtiesOf: _subs };
})();
