/* =====================================================
   data-loader.js — 資料載入與快取
   ===================================================== */

const DataLoader = (function () {
  'use strict';

  const _cache = new Map();   // year -> questions[]
  let   _index = null;        // index.json 內容
  let   _concepts = null;     // concepts.json 內容

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

  /* ── 取得所有已載入的問題（扁平化） ── */
  function getLoadedQuestions() {
    const all = [];
    for (const qs of _cache.values()) {
      for (const q of qs) all.push(q);
    }
    return all;
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
    getLoadedQuestions,
    saveQuestionEdit,
    discardAllEdits,
    countPendingEdits,
    exportAllEdits,
    loadAllAvailableYears,
  };
})();
