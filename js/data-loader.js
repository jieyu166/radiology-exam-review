/* =====================================================
   data-loader.js — 資料載入與快取
   ===================================================== */

const DataLoader = (function () {
  'use strict';

  const _cache = new Map();   // year -> questions[]
  let   _index = null;        // index.json 內容
  let   _concepts = null;     // 舊 concepts.json 內容（fallback 用）
  let   _conceptsIndex = null; // concepts-index.json → { slug: {slug,name,nameZh,subspecialty,checked} }
  const _conceptCache = new Map(); // slug -> 單概念完整物件（懶載入快取）
  const SAFE_SLUG = /^[a-z0-9][a-z0-9-]*$/; // audit：slug 會拼進 fetch 路徑，限安全字元

  /* ── 從 localStorage 取得使用者編輯 ── */
  function _getLocalEdits(namespace) {
    try {
      const raw = localStorage.getItem('rex_edits_' + namespace);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      console.warn('[DataLoader] localStorage parse error', e);
      return {};
    }
  }

  /* ── 將使用者編輯合併回問題物件 ── */
  function _mergeEdits(questions, edits) {
    return questions.map(q => {
      const patch = edits[q.id];
      if (!patch) return q;
      return Object.assign({}, q, patch);
    });
  }

  /* ── 載入 index.json ── */
  async function loadIndex() {
    if (_index) return _index;
    const resp = await fetch('data/index.json');
    if (!resp.ok) throw new Error('無法載入 index.json：' + resp.status);
    _index = await resp.json();
    return _index;
  }

  /* ── 載入單一年份 ── */
  async function loadYear(year) {
    const key = String(year);
    if (_cache.has(key)) return _cache.get(key);

    const resp = await fetch('data/' + key + '.json');
    if (!resp.ok) throw new Error('無法載入 ' + key + '.json：' + resp.status);
    const data = await resp.json();

    // 合併 localStorage 中對此年份問題的編輯
    const edits = _getLocalEdits('year_' + key);
    const questions = _mergeEdits(data.questions || [], edits);

    _cache.set(key, questions);
    return questions;
  }

  /* ── 載入 concepts.json ── */
  async function loadConcepts() {
    if (_concepts) return _concepts;
    const resp = await fetch('data/concepts.json');
    if (!resp.ok) throw new Error('無法載入 concepts.json：' + resp.status);
    const data = await resp.json();

    // 合併 localStorage 中的 concept 編輯
    const edits = _getLocalEdits('concepts');
    const concepts = Object.assign({}, data.concepts, edits);

    _concepts = concepts;
    return concepts;
  }

  /* ── 載入概念索引（清單頁用；輕量，不含內文） ── */
  async function loadConceptsIndex() {
    if (_conceptsIndex) return _conceptsIndex;
    const resp = await fetch('data/concepts-index.json');
    if (!resp.ok) throw new Error('無法載入 concepts-index.json：' + resp.status);
    const data = await resp.json();
    const bySlug = {};
    for (const e of (data.concepts || [])) if (e && e.slug) bySlug[e.slug] = e;
    // 合併 localStorage 概念編輯（覆蓋清單顯示欄位）
    const edits = _getLocalEdits('concepts');
    for (const slug of Object.keys(edits)) {
      bySlug[slug] = Object.assign({ slug }, bySlug[slug] || {}, edits[slug]);
    }
    _conceptsIndex = bySlug;
    return bySlug;
  }

  /* ── 懶載入單一概念完整內容（詳情頁用） ── */
  async function loadConcept(slug) {
    if (typeof slug !== 'string' || !SAFE_SLUG.test(slug)) {
      console.warn('[DataLoader] 不合法的概念 slug：', slug);
      return null;
    }
    if (_conceptCache.has(slug)) return _conceptCache.get(slug);

    let base = null;
    try {
      const resp = await fetch('data/concepts/' + slug + '.json');
      if (resp.ok) {
        base = await resp.json();
      } else if (resp.status !== 404) {
        throw new Error('載入概念失敗 ' + slug + '：' + resp.status);
      } else {
        console.warn('[DataLoader] 單概念檔不存在，改用 fallback：', slug);
      }
    } catch (e) {
      console.warn('[DataLoader] 載入單概念檔錯誤，改用 fallback：', slug, e);
    }

    // fallback：舊 concepts.json → 索引最小資訊
    if (!base) {
      try {
        const legacy = await loadConcepts();
        if (legacy && legacy[slug]) base = Object.assign({ slug }, legacy[slug]);
      } catch (e) { /* 舊檔不存在，略過 */ }
    }
    if (!base) {
      try {
        const idx = await loadConceptsIndex();
        if (idx && idx[slug]) base = Object.assign({ slug }, idx[slug]);
      } catch (e) { /* 略過 */ }
    }
    const edits = _getLocalEdits('concepts');
    // 僅存在於 localStorage 的新建概念也要能解析
    if (!base) {
      if (!edits[slug]) return null;
      base = { slug };
    }
    const merged = edits[slug] ? Object.assign({}, base, edits[slug]) : base;
    _conceptCache.set(slug, merged);
    return merged;
  }

  /* ── 取得所有已載入的問題（扁平化） ── */
  function getLoadedQuestions() {
    const all = [];
    for (const qs of _cache.values()) {
      for (const q of qs) all.push(q);
    }
    return all;
  }

  /* ── 儲存概念編輯到 localStorage + 記憶體快取 ── */
  function saveConceptEdit(id, patch) {
    const key = 'rex_edits_concepts';
    let edits;
    try { edits = JSON.parse(localStorage.getItem(key) || '{}'); }
    catch (e) { edits = {}; }
    edits[id] = Object.assign({}, edits[id] || {}, patch);
    localStorage.setItem(key, JSON.stringify(edits));

    // 同步更新記憶體快取（舊 dict、懶載入快取、索引）
    if (_concepts) {
      _concepts[id] = Object.assign({}, _concepts[id] || {}, patch);
    }
    if (_conceptCache.has(id)) {
      _conceptCache.set(id, Object.assign({}, _conceptCache.get(id), patch));
    }
    if (_conceptsIndex && _conceptsIndex[id]) {
      _conceptsIndex[id] = Object.assign({}, _conceptsIndex[id], patch);
    }
  }

  /* ── 儲存單題編輯到 localStorage ── */
  function saveQuestionEdit(id, patch) {
    const year = id.split('-')[0];
    const key  = 'rex_edits_year_' + year;
    const edits = (() => {
      try { return JSON.parse(localStorage.getItem(key) || '{}'); }
      catch (e) { return {}; }
    })();
    edits[id] = Object.assign({}, edits[id] || {}, patch);
    localStorage.setItem(key, JSON.stringify(edits));

    // 同步更新記憶體快取
    if (_cache.has(year)) {
      const qs = _cache.get(year);
      const idx = qs.findIndex(q => q.id === id);
      if (idx !== -1) {
        qs[idx] = Object.assign({}, qs[idx], patch);
      }
    }
  }

  /* ── 放棄所有編輯（清除 localStorage + 快取） ── */
  function discardAllEdits() {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('rex_edits_'));
    keys.forEach(k => localStorage.removeItem(k));
    _cache.clear();
    _concepts = null;
    _index    = null;
    _conceptsIndex = null;
    _conceptCache.clear();
  }

  /* ── 計算待存更改數 ── */
  function countPendingEdits() {
    let count = 0;
    const keys = Object.keys(localStorage).filter(k => k.startsWith('rex_edits_'));
    for (const k of keys) {
      try {
        const obj = JSON.parse(localStorage.getItem(k) || '{}');
        count += Object.keys(obj).length;
      } catch (e) { /* skip */ }
    }
    return count;
  }

  /* ── 匯出編輯差異（patch JSON） ── */
  function exportAllEdits() {
    const result = {};
    const keys = Object.keys(localStorage).filter(k => k.startsWith('rex_edits_'));
    for (const k of keys) {
      try {
        result[k] = JSON.parse(localStorage.getItem(k) || '{}');
      } catch (e) { /* skip */ }
    }
    return result;
  }

  /* ── 載入所有可用年份 ── */
  async function loadAllAvailableYears() {
    const idx = await loadIndex();
    const years = (idx.years || []).map(y => y.year);
    await Promise.all(years.map(y => loadYear(y)));
    return years;
  }

  return {
    loadIndex,
    loadYear,
    loadConcepts,
    loadConceptsIndex,
    loadConcept,
    getLoadedQuestions,
    saveQuestionEdit,
    saveConceptEdit,
    discardAllEdits,
    countPendingEdits,
    exportAllEdits,
    loadAllAvailableYears,
  };
})();
