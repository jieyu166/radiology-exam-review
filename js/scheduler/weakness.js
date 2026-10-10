/* =====================================================
   scheduler/weakness.js — 弱點分群（確定性）
   移植自 mcq-bank（MIT, Hsiehting Lin 2026）worker/lib/weakness.ts 的 groupByTopic：
   rows {slug, label, questionId}；order 為最近答錯優先的題號清單；
   群 ≥ min(2)、依 size 遞減再 label、最多 limit(12)、anchor 為排名最小者。
   ===================================================== */

window.RexScheduler = window.RexScheduler || {};
window.RexScheduler.weakness = (function () {
  'use strict';

  function groupByTopic(rows, order, options) {
    const min = options && Number.isFinite(options.min) ? options.min : 2;
    const limit = options && Number.isFinite(options.limit) ? options.limit : 12;
    const rank = new Map();
    (order || []).forEach((id, index) => { if (!rank.has(id)) rank.set(id, index); });
    const groups = new Map();
    for (const r of rows || []) {
      if (!r || !r.slug || !r.questionId) continue;
      let g = groups.get(r.slug);
      if (!g) { g = { slug: r.slug, label: r.label || r.slug, ids: [] }; groups.set(r.slug, g); }
      if (!g.ids.includes(r.questionId)) g.ids.push(r.questionId);
    }
    const rankOf = id => (rank.has(id) ? rank.get(id) : Infinity);
    return Array.from(groups.values())
      .filter(g => g.ids.length >= min)
      .map(g => ({
        slug: g.slug,
        label: g.label,
        size: g.ids.length,
        anchor: g.ids.reduce((best, id) => (rankOf(id) < rankOf(best) ? id : best), g.ids[0]),
        questionIds: g.ids.slice(),
      }))
      .sort((a, b) => b.size - a.size || a.label.localeCompare(b.label))
      .slice(0, limit);
  }

  /** Build rows from currently-wrong question entries: subspecialty first, then each concept id. */
  function rowsFromEntries(entries, conceptNames) {
    const rows = [];
    for (const e of entries || []) {
      const subs = Array.isArray(e.subspecialty) ? e.subspecialty : (e.subspecialty ? [e.subspecialty] : []);
      for (const sub of subs) rows.push({ slug: `sub:${sub}`, label: String(sub), questionId: e.id });
      for (const c of e.conceptIds || []) rows.push({ slug: `concept:${c}`, label: (conceptNames && conceptNames[c]) || c, questionId: e.id });
    }
    return rows;
  }

  return { groupByTopic, rowsFromEntries };
})();
