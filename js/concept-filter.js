/* =====================================================
   concept-filter.js — 概念列表的次專科篩選與搜尋（純函式）
   規格：openspec/specs/concept-subspecialty-filter
   - 「全部」＋每個次專科一顆 pill（含數量），空值歸「未分類」
   - 排序：考題次專科固定順序 → 概念專屬值（字母序）→ 未分類最後
   ===================================================== */

const ConceptFilter = (function () {
  'use strict';

  const CANONICAL = ['ABD', 'CV', 'CH', 'NR', 'MSK', 'H&N', 'PED', 'IR', 'Physics', 'Breast', 'US'];
  const UNCATEGORIZED = '__uncategorized__';
  const UNCATEGORIZED_LABEL = '未分類';

  function subsOf(entry) {
    const value = entry && entry.subspecialty;
    const list = Array.isArray(value) ? value : (value ? [value] : []);
    const out = list.map(v => String(v).trim()).filter(Boolean);
    return out.length ? out : [UNCATEGORIZED];
  }

  /** @returns [{key, label, count}] starting with the "All" control */
  function buildPills(entries) {
    const counts = new Map();
    for (const e of entries || []) for (const s of subsOf(e)) counts.set(s, (counts.get(s) || 0) + 1);
    const keys = Array.from(counts.keys());
    const canonical = CANONICAL.filter(k => counts.has(k));
    const extras = keys.filter(k => !CANONICAL.includes(k) && k !== UNCATEGORIZED).sort((a, b) => a.localeCompare(b));
    const ordered = canonical.concat(extras);
    if (counts.has(UNCATEGORIZED)) ordered.push(UNCATEGORIZED);
    return [{ key: '', label: '全部', count: (entries || []).length }].concat(ordered.map(k => ({ key: k, label: k === UNCATEGORIZED ? UNCATEGORIZED_LABEL : k, count: counts.get(k) })));
  }

  function _haystack(entry) {
    const aliases = Array.isArray(entry.aliases) ? entry.aliases : [];
    return [entry.name, entry.id].concat(aliases).filter(Boolean).join(' ').toLowerCase();
  }

  /** Filter by subspecialty key ('' = all) and free-text query (name / id / aliases, case-insensitive, all terms). */
  function filterConcepts(entries, options) {
    const sub = (options && options.sub) || '';
    const terms = String((options && options.query) || '').toLowerCase().split(/\s+/).filter(Boolean);
    return (entries || []).filter(e => {
      if (sub && !subsOf(e).includes(sub)) return false;
      if (terms.length) {
        const hay = _haystack(e);
        if (!terms.every(t => hay.includes(t))) return false;
      }
      return true;
    });
  }

  return { CANONICAL, UNCATEGORIZED, UNCATEGORIZED_LABEL, subsOf, buildPills, filterConcepts };
})();
