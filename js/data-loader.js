/* =====================================================
   data-loader.js — 學習進度（localStorage）與舊編輯匯出
   內容本體改由 content-store.js 從 vault 產出的靜態檔載入；
   本模組只負責 rex_progress 讀寫與 rex_edits_* 匯出。
   ===================================================== */

const DataLoader = (function () {
  'use strict';

  const PROGRESS_KEY = 'rex_progress';
  const PROGRESS_VERSION = 2;

  function _emptyProgress() {
    return { schemaVersion: PROGRESS_VERSION, seen: {}, starred: {}, answers: {}, examHistory: [] };
  }

  function _normalizeProgress(raw) {
    const base = _emptyProgress();
    if (!raw || typeof raw !== 'object') return base;
    const answers = raw.answers && typeof raw.answers === 'object' && !Array.isArray(raw.answers) ? raw.answers : {};
    const normalizedAnswers = {};
    Object.keys(answers).forEach(id => {
      const value = answers[id];
      normalizedAnswers[id] = value && typeof value === 'object'
        ? Object.assign({}, value, { sourceSha256: value.sourceSha256 || null })
        : { last: null, correct: false, ts: null, sourceSha256: null };
    });
    const examHistory = Array.isArray(raw.examHistory) ? raw.examHistory.map(item => {
      if (!item || typeof item !== 'object') return item;
      return Object.assign({}, item, {
        sourceSha256ByQuestion: item.sourceSha256ByQuestion || item.questionSourceSha256 || null,
      });
    }) : [];
    return {
      schemaVersion: PROGRESS_VERSION,
      seen: raw.seen && typeof raw.seen === 'object' && !Array.isArray(raw.seen) ? raw.seen : {},
      starred: raw.starred && typeof raw.starred === 'object' && !Array.isArray(raw.starred) ? raw.starred : {},
      answers: normalizedAnswers,
      examHistory,
    };
  }

  function _saveProgress(progress) {
    try {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(_normalizeProgress(progress)));
      return true;
    } catch (e) {
      console.warn('[DataLoader] rex_progress write error', e);
      return false;
    }
  }

  function getProgress() {
    try {
      const raw = localStorage.getItem(PROGRESS_KEY);
      return raw ? _normalizeProgress(JSON.parse(raw)) : _emptyProgress();
    } catch (e) {
      console.warn('[DataLoader] rex_progress parse error', e);
      return _emptyProgress();
    }
  }

  function markSeen(id) {
    if (!id) return;
    const progress = getProgress();
    progress.seen[id] = Date.now();
    _saveProgress(progress);
  }

  function toggleStar(id) {
    if (!id) return false;
    const progress = getProgress();
    const next = progress.starred[id] !== true;
    if (next) progress.starred[id] = true;
    else delete progress.starred[id];
    _saveProgress(progress);
    return next;
  }

  function isStarred(id) {
    return getProgress().starred[id] === true;
  }

  function recordAnswer(id, result) {
    if (!id || !result) return;
    const progress = getProgress();
    progress.answers[id] = {
      last: result.chosen || null,
      correct: result.correct === true,
      ts: Date.now(),
      sourceSha256: result.sourceSha256 || null,
    };
    _saveProgress(progress);
  }

  function addExamRecord(record) {
    if (!record || typeof record !== 'object') return;
    const progress = getProgress();
    const item = Object.assign({ ts: Date.now(), sourceSha256ByQuestion: null }, record);
    progress.examHistory = [item].concat(progress.examHistory || []);
    _saveProgress(progress);
  }

  function exportProgress() {
    return { rex_progress: getProgress() };
  }

  function importProgress(obj) {
    const incoming = _normalizeProgress(obj && obj.rex_progress ? obj.rex_progress : obj);
    const progress = getProgress();
    const stats = { seen: 0, starred: 0, answers: 0, examHistory: 0 };

    for (const [id, ts] of Object.entries(incoming.seen)) {
      if (!Object.prototype.hasOwnProperty.call(progress.seen, id)) stats.seen++;
      progress.seen[id] = ts;
    }
    for (const [id, value] of Object.entries(incoming.starred)) {
      if (value !== true) continue;
      if (progress.starred[id] !== true) stats.starred++;
      progress.starred[id] = true;
    }
    for (const [id, value] of Object.entries(incoming.answers)) {
      if (!Object.prototype.hasOwnProperty.call(progress.answers, id)) stats.answers++;
      progress.answers[id] = value;
    }

    const seenTs = new Set((progress.examHistory || []).map(r => r && r.ts).filter(v => v != null));
    for (const item of incoming.examHistory) {
      if (!item || item.ts == null || seenTs.has(item.ts)) continue;
      progress.examHistory.push(item);
      seenTs.add(item.ts);
      stats.examHistory++;
    }
    progress.examHistory.sort((a, b) => (b.ts || 0) - (a.ts || 0));
    _saveProgress(progress);
    return stats;
  }

  function clearProgress() {
    localStorage.removeItem(PROGRESS_KEY);
  }

  /* ── 匯出舊版編輯差異（localStorage 的 rex_edits_*；內容已唯讀，僅供搬遷） ── */
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

  return {
    getProgress,
    markSeen,
    toggleStar,
    isStarred,
    recordAnswer,
    addExamRecord,
    exportProgress,
    importProgress,
    clearProgress,
    exportAllEdits,
    exportLegacyEdits: exportAllEdits,
  };
})();
