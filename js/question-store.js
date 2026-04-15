/* =====================================================
   question-store.js — 問題篩選與查詢
   ===================================================== */

const QuestionStore = (function () {
  'use strict';

  /* ── 工具：shuffle ── */
  function _shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function getQuestionYears(q) {
    const raw = Array.isArray(q && q.years) && q.years.length > 0 ? q.years : [q && q.year];
    return Array.from(new Set(raw.map(y => parseInt(y, 10)).filter(Number.isFinite))).sort((a, b) => a - b);
  }

  function _dedupeById(questions) {
    const seen = new Set();
    return questions.filter(q => {
      const key = q && q.id;
      if (!key) return true;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  /**
   * 取得篩選後的問題
   * @param {Object} opts
   * @param {string[]|null} opts.years - 年份字串陣列，null 代表全部
   * @param {string[]|null} opts.subspecialties - 次專科陣列，null 或 [] 代表全部
   * @param {boolean} opts.checkedOnly - 只顯示已確認
   */
  function getQuestions({ years = null, subspecialties = null, checkedOnly = false } = {}) {
    let questions = DataLoader.getLoadedQuestions();

    // 年份篩選
    if (years && years.length > 0) {
      const ySet = new Set(years.map(String));
      questions = questions.filter(q => getQuestionYears(q).some(y => ySet.has(String(y))));
    }

    // 次專科篩選
    if (subspecialties && subspecialties.length > 0) {
      const subSet = new Set(subspecialties);
      questions = questions.filter(q => subSet.has(q.subspecialty));
    }

    // 只顯示已確認
    if (checkedOnly) {
      questions = questions.filter(q => q.checked === true);
    }

    return _dedupeById(questions);
  }

  /**
   * 依 id 查找問題
   * @param {string} id
   */
  function getQuestionById(id) {
    return DataLoader.getLoadedQuestions().find(q => q.id === id) || null;
  }

  /**
   * 隨機抽題
   * @param {number} count
   * @param {Object} opts 與 getQuestions 相同
   */
  function getRandomQuestions(count, opts = {}) {
    const pool = getQuestions(opts);
    const shuffled = _shuffle(pool);
    return shuffled.slice(0, Math.min(count, shuffled.length));
  }

  /**
   * 取得所有已載入資料中的次專科（去重）
   */
  function getAllSubspecialties() {
    const all = DataLoader.getLoadedQuestions();
    const set = new Set();
    for (const q of all) {
      if (q.subspecialty) set.add(q.subspecialty);
    }
    return Array.from(set).sort();
  }

  /**
   * 取得所有年份（從 index.json）
   * @returns {Promise<number[]>}
   */
  async function getAllYears() {
    const idx = await DataLoader.loadIndex();
    const set = new Set((idx.years || []).map(y => y.year));
    for (const q of DataLoader.getLoadedQuestions()) {
      getQuestionYears(q).forEach(y => set.add(y));
    }
    return Array.from(set).sort((a, b) => b - a);
  }

  /**
   * 統計各次專科題數
   */
  function countBySubspecialty(questions) {
    const counts = {};
    for (const q of questions) {
      counts[q.subspecialty] = (counts[q.subspecialty] || 0) + 1;
    }
    return counts;
  }

  /**
   * 統計已確認題數
   */
  function countChecked(questions) {
    return questions.filter(q => q.checked).length;
  }

  return {
    getQuestions,
    getQuestionById,
    getRandomQuestions,
    getQuestionYears,
    getAllSubspecialties,
    getAllYears,
    countBySubspecialty,
    countChecked,
  };
})();
