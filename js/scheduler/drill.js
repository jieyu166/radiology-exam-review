/* =====================================================
   scheduler/drill.js — 跨年交錯練習（確定性）
   移植自 mcq-bank（MIT, Hsiehting Lin 2026）worker/lib/drill.ts：
   seededShuffle = LCG(1664525, 1013904223) + Fisher–Yates；
   pickInterleaved：去重、排除 anchor、依年份分桶、各桶洗牌、年份 round-robin。
   ===================================================== */

window.RexScheduler = window.RexScheduler || {};
window.RexScheduler.drill = (function () {
  'use strict';

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

  /** Stable 32-bit hash of a string (for seeds derived from dayKey etc.). */
  function hashSeed(text) {
    let h = 2166136261;
    for (const ch of String(text)) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; }
    return h >>> 0;
  }

  /** hits: [{id, year}] in relevance order. Returns up to n ids interleaved across years. */
  function pickInterleaved(hits, options) {
    const o = options || {};
    const n = Number.isFinite(o.n) && o.n > 0 ? Math.trunc(o.n) : 10;
    const seed = Number.isFinite(o.seed) ? o.seed : 1;
    const seen = new Set();
    const buckets = new Map();
    for (const h of hits || []) {
      if (!h || !h.id || h.id === o.anchor || seen.has(h.id)) continue;
      seen.add(h.id);
      const year = String(h.year == null ? '' : h.year);
      if (!buckets.has(year)) buckets.set(year, []);
      buckets.get(year).push(h.id);
    }
    const years = Array.from(buckets.keys()).sort();
    const queues = years.map((y, i) => seededShuffle(buckets.get(y), seed + i));
    const out = [];
    let progress = true;
    while (out.length < n && progress) {
      progress = false;
      for (const q of queues) {
        if (out.length >= n) break;
        if (q.length) { out.push(q.shift()); progress = true; }
      }
    }
    return out;
  }

  return { seededShuffle, hashSeed, pickInterleaved };
})();
