/* =====================================================
   vault-app.js — vault-native review-site application
   ===================================================== */

const VaultApp = (function () {
  'use strict';

  const state = {
    indexes: null,
    year: '',
    sub: '',
    checked: false,
    starred: false,
    wrong: false,
    cardIndex: 0,
    examEntries: [],
    examNotes: [],
    examAnswers: {},
    examIndex: 0,
    routeToken: 0,
  };

  function _esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function _route() {
    const raw = (window.location.hash || '#/card').slice(2);
    const [path, query] = raw.split('?');
    const params = new URLSearchParams(query || '');
    return { path: path || 'card', id: path && path.includes('/') ? decodeURIComponent(path.split('/').slice(1).join('/')) : '', params };
  }

  function _navigate(hash) {
    window.location.hash = hash;
  }

  function _main() {
    return document.getElementById('main-content');
  }

  function _entries(kind) {
    if (!state.indexes) return [];
    const source = kind === 'question' ? state.indexes.questions.entries : state.indexes.concepts.entries;
    return Array.isArray(source) ? source : [];
  }

  function _years(entry) {
    const years = Array.isArray(entry.years) ? entry.years : (entry.year == null ? [] : [entry.year]);
    return years.map(value => String(value));
  }

  function _questionEntries(options) {
    const config = options || {};
    return _entries('question').filter(entry => {
      if (config.scorableOnly && entry.scorable === false) return false;
      if (state.year && !_years(entry).includes(String(state.year))) return false;
      if (state.sub && String(entry.subspecialty || '') !== state.sub) return false;
      if (state.checked && entry.checked !== true) return false;
      const progress = typeof DataLoader !== 'undefined' ? DataLoader.getProgress() : { starred: {}, answers: {} };
      if (state.starred && progress.starred[entry.id] !== true) return false;
      if (state.wrong && (!progress.answers[entry.id] || progress.answers[entry.id].correct !== false)) return false;
      return true;
    });
  }

  function _setActiveNav(path) {
    document.querySelectorAll('.nav-tab, .bottom-tab').forEach(button => {
      const route = (button.dataset.route || '').replace(/^#\//, '');
      const active = path === route || (route === 'exam' && path.startsWith('exam')) || (route === 'concepts' && path.startsWith('concept'));
      button.classList.toggle('active', active);
      button.setAttribute('aria-selected', active ? 'true' : 'false');
    });
  }

  function _populateFilters() {
    const years = [...new Set(_entries('question').flatMap(_years))].sort();
    const yearSelect = document.getElementById('year-select');
    if (yearSelect) yearSelect.innerHTML = '<option value="">全部年份</option>' + years.map(year => `<option value="${_esc(year)}">${_esc(year)} 年</option>`).join('');
    const subs = [...new Set(_entries('question').map(entry => String(entry.subspecialty || '')).filter(Boolean))].sort();
    const pills = document.getElementById('subspecialty-pills');
    if (pills) pills.innerHTML = ['<button class="pill active" data-sub="">全部</button>'].concat(subs.map(sub => `<button class="pill" data-sub="${_esc(sub)}">${_esc(sub)}</button>`)).join('');
    if (yearSelect) yearSelect.value = state.year;
    _bindFilterEvents();
  }

  function _bindFilterEvents() {
    const yearSelect = document.getElementById('year-select');
    if (yearSelect && !yearSelect.dataset.vaultBound) {
      yearSelect.dataset.vaultBound = '1';
      yearSelect.addEventListener('change', () => { state.year = yearSelect.value; state.cardIndex = 0; _renderRoute(); });
    }
    document.querySelectorAll('#subspecialty-pills .pill').forEach(button => {
      if (button.dataset.vaultBound) return;
      button.dataset.vaultBound = '1';
      button.addEventListener('click', () => {
        state.sub = button.dataset.sub || '';
        document.querySelectorAll('#subspecialty-pills .pill').forEach(item => item.classList.toggle('active', item.dataset.sub === state.sub));
        state.cardIndex = 0;
        _renderRoute();
      });
    });
    [['checked-toggle', 'checked'], ['starred-toggle', 'starred'], ['wrong-toggle', 'wrong']].forEach(([id, key]) => {
      const input = document.getElementById(id);
      if (!input || input.dataset.vaultBound) return;
      input.dataset.vaultBound = '1';
      input.addEventListener('change', () => { state[key] = input.checked; state.cardIndex = 0; _renderRoute(); });
    });
  }

  function _hideLegacyEditorControls() {
    ['edit-mode-toggle', 'pending-badge', 'discard-btn'].forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        const row = element.closest('.settings-row') || element;
        row.hidden = true;
      }
    });
    const exportButton = document.getElementById('export-btn');
    if (exportButton) {
      exportButton.textContent = '匯出舊版內容 patch（不套用）';
      exportButton.addEventListener('click', () => _download(DataLoader.exportLegacyEdits(), 'rex-edits-export.json'));
    }
    const settings = document.getElementById('settings-toggle');
    const panel = document.getElementById('settings-panel');
    if (settings && panel && !settings.dataset.vaultBound) {
      settings.dataset.vaultBound = '1';
      settings.addEventListener('click', () => { panel.hidden = !panel.hidden; });
    }
    const progressExport = document.getElementById('progress-export-btn');
    if (progressExport && !progressExport.dataset.vaultBound) {
      progressExport.dataset.vaultBound = '1';
      progressExport.addEventListener('click', () => _download(DataLoader.exportProgress(), 'rex-progress.json'));
    }
    const progressClear = document.getElementById('progress-clear-btn');
    if (progressClear && !progressClear.dataset.vaultBound) {
      progressClear.dataset.vaultBound = '1';
      progressClear.addEventListener('click', () => { if (window.confirm('確定清除學習記錄？')) { DataLoader.clearProgress(); _renderRoute(); } });
    }
    const progressImport = document.getElementById('progress-import-btn');
    const progressFile = document.getElementById('progress-import-file');
    if (progressImport && progressFile && !progressImport.dataset.vaultBound) {
      progressImport.dataset.vaultBound = '1';
      progressImport.addEventListener('click', () => progressFile.click());
      progressFile.addEventListener('change', () => {
        const file = progressFile.files && progressFile.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => { try { DataLoader.importProgress(JSON.parse(reader.result)); _renderRoute(); } catch (error) { console.warn('[VaultApp] progress import failed', error); } };
        reader.readAsText(file);
      });
    }
  }

  function _download(value, filename) {
    const blob = new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob); link.download = filename; link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 0);
  }

  function _shell(title, body) {
    const main = _main();
    if (!main) return null;
    main.innerHTML = `<section class="vault-view-section"><div class="vault-view-header"><h2>${_esc(title)}</h2></div>${body}</section>`;
    return main.querySelector('.vault-view-section');
  }

  function _recordAnswer(result) {
    if (typeof DataLoader !== 'undefined') {
      DataLoader.markSeen(result.id);
      if (result.scorable !== false) DataLoader.recordAnswer(result.id, result);
    }
  }

  async function _renderCard(params) {
    const entries = _questionEntries();
    const qid = params.get('qid');
    if (qid) {
      const found = entries.findIndex(item => item.id === qid);
      if (found >= 0) state.cardIndex = found;
    }
    if (!entries.length) { _shell('卡片模式', '<div class="vault-empty">沒有符合條件的題目</div>'); return; }
    state.cardIndex = Math.max(0, Math.min(state.cardIndex, entries.length - 1));
    const entry = entries[state.cardIndex];
    const section = _shell('卡片模式', `<div class="vault-card-toolbar"><button class="btn btn-outline" id="vault-card-prev">上一題</button><span>${state.cardIndex + 1} / ${entries.length}</span><button class="btn btn-outline" id="vault-card-next">下一題</button></div><div id="vault-card-slot"><div class="vault-loading">載入題目…</div></div>`);
    section.querySelector('#vault-card-prev').disabled = state.cardIndex === 0;
    section.querySelector('#vault-card-next').disabled = state.cardIndex === entries.length - 1;
    section.querySelector('#vault-card-prev').onclick = () => { state.cardIndex--; _renderRoute(); };
    section.querySelector('#vault-card-next').onclick = () => { state.cardIndex++; _renderRoute(); };
    const token = ++state.routeToken;
    try {
      const note = await ContentStore.getQuestion(entry.id);
      if (token !== state.routeToken) return;
      if (!note) throw new Error('找不到 published question ' + entry.id);
      DataLoader.markSeen(entry.id);
      const slot = section.querySelector('#vault-card-slot'); slot.innerHTML = '<div class="vault-question-host"></div>';
      VaultQuestionView.bind(slot.firstElementChild, note, { mode: 'card', onAnswer: _recordAnswer });
    } catch (error) { section.querySelector('#vault-card-slot').innerHTML = `<div class="vault-error">${_esc(error.message || error)}</div>`; }
  }

  function _renderList() {
    const entries = _questionEntries();
    const section = _shell('題目列表', `<div class="vault-list-toolbar"><span>共 ${entries.length} 題</span><input id="vault-search" class="text-input" placeholder="搜尋題號、概念或次專科" /></div><div id="vault-question-list" class="vault-question-list"></div>`);
    const list = section.querySelector('#vault-question-list');
    const draw = query => {
      const needle = String(query || '').toLowerCase();
      const visible = entries.filter(entry => !needle || JSON.stringify(entry).toLowerCase().includes(needle));
      list.innerHTML = visible.map(entry => `<a class="vault-list-item" href="#/card?qid=${encodeURIComponent(entry.id)}"><strong>${_esc(entry.id)}</strong><span>${_esc(entry.subspecialty || '')}</span><span>${_esc(_years(entry).join(' / '))}</span><span>${_esc((entry.conceptIds || []).join(', '))}</span></a>`).join('') || '<div class="vault-empty">沒有符合條件的題目</div>';
    };
    draw('');
    section.querySelector('#vault-search').addEventListener('input', event => draw(event.target.value));
  }

  function _renderConceptList() {
    const concepts = _entries('concept');
    const relations = new Map((_indexEntries('relations')).map(item => [item.conceptId, item.questionIds || []]));
    const section = _shell('概念列表', `<div class="vault-concept-grid">${concepts.map(entry => `<a class="vault-concept-item" href="#/concept/${encodeURIComponent(entry.id)}"><strong>${_esc(entry.name || entry.id)}</strong><span>${_esc(Array.isArray(entry.subspecialty) ? entry.subspecialty.join(', ') : entry.subspecialty || '')}</span><small>相關 ${relations.get(entry.id)?.length || 0} 題</small></a>`).join('')}</div>`);
    return section;
  }

  function _indexEntries(name) {
    return state.indexes && state.indexes[name] && Array.isArray(state.indexes[name].entries) ? state.indexes[name].entries : [];
  }

  async function _renderConcept(id) {
    const section = _shell('概念', '<div class="vault-loading">載入概念…</div>');
    const token = ++state.routeToken;
    try {
      const note = await ContentStore.getConcept(id);
      if (token !== state.routeToken) return;
      if (!note) throw new Error('找不到 published concept ' + id);
      const title = note.record.frontmatter && (note.record.frontmatter.name || note.record.id) || id;
      const relations = _indexEntries('relations').find(item => item.conceptId === id);
      section.innerHTML = `<div class="vault-concept-header"><a href="#/concepts">← 概念列表</a><h2>${_esc(title)}</h2><small>${_esc(id)}</small></div><div class="vault-note-content" id="vault-concept-note"></div><div class="vault-related"><h3>相關題目（${relations ? relations.questionIds.length : 0}）</h3>${relations ? relations.questionIds.map(qid => `<a href="#/card?qid=${encodeURIComponent(qid)}">${_esc(qid)}</a>`).join('、') : '無'}</div>`;
      NoteRenderer.renderTo(section.querySelector('#vault-concept-note'), note.raw, { record: note.record });
    } catch (error) { section.innerHTML = `<div class="vault-error">${_esc(error.message || error)}</div>`; }
  }

  function _renderExamSetup() {
    const count = Math.min(20, _questionEntries().length);
    const section = _shell('模擬考', `<div class="vault-exam-setup"><p>目前篩選後共有 ${_questionEntries().length} 題。</p><label>題數 <input id="vault-exam-count" class="text-input" type="number" min="1" max="${Math.max(1, _questionEntries().length)}" value="${count || 1}" /></label><button id="vault-exam-start" class="btn btn-primary">開始模擬考</button></div>`);
    section.querySelector('#vault-exam-start').onclick = () => {
      const n = Math.max(1, Math.min(Number(section.querySelector('#vault-exam-count').value) || 1, _questionEntries().length));
      state.examEntries = _questionEntries({ scorableOnly: true }).slice(0, n); state.examNotes = []; state.examAnswers = {}; state.examIndex = 0; _navigate('#/exam/active');
    };
  }

  async function _renderExamActive() {
    if (!state.examEntries.length) { _navigate('#/exam'); return; }
    if (state.examIndex >= state.examEntries.length) { _finishExam(); return; }
    const entry = state.examEntries[state.examIndex];
    const section = _shell('模擬考進行', `<div class="vault-card-toolbar"><span>第 ${state.examIndex + 1} / ${state.examEntries.length} 題</span><button class="btn btn-outline" id="vault-exam-end">結束考試</button></div><div id="vault-exam-slot"><div class="vault-loading">載入題目…</div></div><button class="btn btn-primary" id="vault-exam-next">${state.examIndex === state.examEntries.length - 1 ? '交卷' : '下一題'}</button>`);
    section.querySelector('#vault-exam-end').onclick = _finishExam;
    section.querySelector('#vault-exam-next').onclick = () => { state.examIndex++; _renderRoute(); };
    const token = ++state.routeToken;
    try {
      const note = await ContentStore.getQuestion(entry.id);
      if (token !== state.routeToken) return;
      state.examNotes[state.examIndex] = note;
      const slot = section.querySelector('#vault-exam-slot'); slot.innerHTML = '<div class="vault-question-host"></div>';
      VaultQuestionView.bind(slot.firstElementChild, note, { mode: 'exam', onAnswer: result => { state.examAnswers[entry.id] = result.chosen; _recordAnswer(result); } });
    } catch (error) { section.querySelector('#vault-exam-slot').innerHTML = `<div class="vault-error">${_esc(error.message || error)}</div>`; }
  }

  function _finishExam() {
    const records = state.examNotes.filter(Boolean).map(note => note.record);
    const score = VaultQuestionView.scoreAnswers(records, state.examAnswers);
    const sourceSha256ByQuestion = {};
    records.forEach(record => { sourceSha256ByQuestion[record.id] = record.sourceSha256 || null; });
    if (records.length && typeof DataLoader !== 'undefined') DataLoader.addExamRecord(Object.assign({}, score, { sourceSha256ByQuestion }));
    const section = _shell('模擬考結果', `<div class="vault-exam-result"><h3>${score.correct} / ${score.total}（${score.pct}%）</h3><p>答錯 ${score.wrong} 題，未作答 ${score.skipped} 題。</p><button class="btn btn-primary" id="vault-exam-retry">重新開始</button></div>`);
    section.querySelector('#vault-exam-retry').onclick = () => _navigate('#/exam');
  }

  async function _renderRoute() {
    if (!state.indexes) return;
    const current = _route();
    _setActiveNav(current.path);
    const filterBar = document.getElementById('filter-bar');
    if (filterBar) filterBar.hidden = !['card', 'list'].includes(current.path);
    if (current.path === 'card') return _renderCard(current.params);
    if (current.path === 'list') return _renderList();
    if (current.path === 'exam') return _renderExamSetup();
    if (current.path === 'exam/active') return _renderExamActive();
    if (current.path === 'concepts') return _renderConceptList();
    if (current.path.startsWith('concept/')) return _renderConcept(current.id);
    return _navigate('#/card');
  }

  async function init() {
    _hideLegacyEditorControls();
    document.querySelectorAll('.nav-tab, .bottom-tab').forEach(button => {
      if (button.dataset.vaultBound) return;
      button.dataset.vaultBound = '1';
      if (button.dataset.route && button.dataset.route !== '#/settings') button.addEventListener('click', () => _navigate(button.dataset.route));
    });
    try {
      state.indexes = await ContentStore.loadIndexes();
      _populateFilters();
      await _renderRoute();
    } catch (error) {
      const main = _main();
      if (main) main.innerHTML = `<div class="vault-error">無法載入 vault-native publication：${_esc(error.message || error)}</div>`;
    }
  }

  window.addEventListener('hashchange', _renderRoute);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  return { init };
})();
