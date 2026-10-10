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
    examElapsed: {},
    drillQueue: null,
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

  function _isWrong(answerEntry) {
    const wc = window.RexScheduler && window.RexScheduler.wrongCriterion;
    return wc ? wc.isWrong(answerEntry) : (!!answerEntry && answerEntry.correct === false);
  }

  function _questionEntries(options) {
    const config = options || {};
    const progress = typeof DataLoader !== 'undefined' ? DataLoader.getProgress() : { starred: {}, answers: {} };
    return _entries('question').filter(entry => {
      if (config.scorableOnly && entry.scorable === false) return false;
      if (state.year && !_years(entry).includes(String(state.year))) return false;
      if (state.sub && String(entry.subspecialty || '') !== state.sub) return false;
      if (state.checked && entry.checked !== true) return false;
      if (state.starred && progress.starred[entry.id] !== true) return false;
      if (state.wrong && !_isWrong(progress.answers[entry.id])) return false;
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

  /* ── 帳號與同步面板 ── */
  function _formatSyncTime(ts) {
    if (!Number.isFinite(ts)) return '尚未同步';
    const d = new Date(ts);
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  }

  function _accountMessage(text, isError) {
    const el = document.getElementById('account-message');
    if (!el) return;
    el.hidden = !text;
    el.textContent = text || '';
    el.classList.toggle('error', !!isError);
  }

  function _refreshAccountPanel() {
    if (typeof SyncClient === 'undefined') return;
    const status = SyncClient.status();
    const loggedOut = document.getElementById('account-logged-out');
    const loggedIn = document.getElementById('account-logged-in');
    if (loggedOut) loggedOut.hidden = status.loggedIn;
    if (loggedIn) loggedIn.hidden = !status.loggedIn;
    const name = document.getElementById('account-username');
    if (name) name.textContent = status.username || '';
    const role = document.getElementById('account-role');
    if (role) role.textContent = status.role === 'admin' ? '（管理者）' : '';
    const invite = document.getElementById('invite-btn');
    if (invite) invite.hidden = status.role !== 'admin';
    const sync = document.getElementById('sync-status');
    if (sync) sync.textContent = status.loggedIn
      ? `同步狀態：待同步 ${status.pending} 筆，上次同步 ${_formatSyncTime(status.lastSyncAt)}`
      : `同步狀態：未登入（本機已記錄，登入後上傳）`;
  }

  async function _afterLoginFlow() {
    try {
      _accountMessage('登入成功，正在同步學習紀錄…');
      const result = await SyncClient.afterLogin();
      _accountMessage(`同步完成：上傳 ${result.uploaded.attempts} 筆作答，合併 ${result.merged.answers} 筆。`);
    } catch (error) {
      _accountMessage(`已登入，但同步失敗：${error.message}`, true);
    }
    _refreshAccountPanel();
    _renderRoute();
  }

  function _bindAccountPanel() {
    if (typeof SyncClient === 'undefined' || typeof AttemptOutbox === 'undefined') return;
    AttemptOutbox.configure({ transport: SyncClient.transport });
    AttemptOutbox.subscribe(_refreshAccountPanel);
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    if (loginForm && !loginForm.dataset.vaultBound) {
      loginForm.dataset.vaultBound = '1';
      loginForm.addEventListener('submit', async event => {
        event.preventDefault();
        const button = document.getElementById('login-btn'); button.disabled = true;
        try {
          await SyncClient.login(document.getElementById('login-username').value, document.getElementById('login-password').value);
          loginForm.reset();
          await _afterLoginFlow();
        } catch (error) {
          _accountMessage(error.status === 423 ? `帳號暫時鎖定，請 ${Math.ceil((error.extra && error.extra.retryAfterSeconds || 900) / 60)} 分鐘後再試` : (error.status === 401 ? '帳號或密碼錯誤' : error.message), true);
        } finally { button.disabled = false; }
      });
      document.getElementById('show-register-btn').addEventListener('click', () => { loginForm.hidden = true; registerForm.hidden = false; _accountMessage(''); });
    }
    if (registerForm && !registerForm.dataset.vaultBound) {
      registerForm.dataset.vaultBound = '1';
      registerForm.addEventListener('submit', async event => {
        event.preventDefault();
        const button = document.getElementById('register-btn'); button.disabled = true;
        try {
          await SyncClient.register(document.getElementById('register-username').value, document.getElementById('register-password').value, document.getElementById('register-invite').value, document.getElementById('register-display').value);
          registerForm.reset();
          await _afterLoginFlow();
        } catch (error) {
          const messages = { invite_invalid: '邀請碼無效、已使用、已撤銷或已過期', username_taken: '帳號已存在', invalid_username: '帳號格式：3–32 字，英數開頭，可含 _ . -', invalid_password: '密碼需 8–128 字' };
          _accountMessage(messages[error.code] || error.message, true);
        } finally { button.disabled = false; }
      });
      document.getElementById('show-login-btn').addEventListener('click', () => { registerForm.hidden = true; loginForm.hidden = false; _accountMessage(''); });
    }
    const syncNow = document.getElementById('sync-now-btn');
    if (syncNow && !syncNow.dataset.vaultBound) {
      syncNow.dataset.vaultBound = '1';
      syncNow.addEventListener('click', async () => {
        syncNow.disabled = true;
        try {
          const pushed = await SyncClient.pushOutbox();
          const merged = await SyncClient.pullSnapshot();
          _accountMessage(`同步完成：送出 ${pushed.sent || 0} 筆，合併 ${merged.answers} 筆。`);
          _renderRoute();
        } catch (error) { _accountMessage(`同步失敗：${error.message}`, true); }
        finally { syncNow.disabled = false; _refreshAccountPanel(); }
      });
    }
    const logout = document.getElementById('logout-btn');
    if (logout && !logout.dataset.vaultBound) {
      logout.dataset.vaultBound = '1';
      logout.addEventListener('click', async () => { await SyncClient.logout(); _accountMessage('已登出；本機學習紀錄保留。'); _refreshAccountPanel(); });
    }
    const invite = document.getElementById('invite-btn');
    if (invite && !invite.dataset.vaultBound) {
      invite.dataset.vaultBound = '1';
      invite.addEventListener('click', async () => {
        const note = window.prompt('邀請碼備註（例如：R2 王醫師）') || '';
        try {
          const created = await SyncClient.createInvite(note);
          const out = document.getElementById('invite-output');
          out.hidden = false;
          out.textContent = `邀請碼（只顯示這一次，14 天內有效）：${created.code}`;
        } catch (error) { _accountMessage(`簽發失敗：${error.message}`, true); }
      });
    }
    _refreshAccountPanel();
    AttemptOutbox.install(window);
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

  function _kickSync() {
    if (typeof AttemptOutbox !== 'undefined') AttemptOutbox.kick();
    _refreshAccountPanel();
  }

  function _recordAnswer(result) {
    if (typeof DataLoader !== 'undefined') {
      DataLoader.markSeen(result.id);
      if (result.scorable !== false) DataLoader.recordAnswer(result.id, result);
      _kickSync();
    }
  }

  async function _renderCard(params) {
    const drill = params.get('drill') === '1' && state.drillQueue ? state.drillQueue : null;
    if (!drill) state.drillQueue = null;
    let entries;
    if (drill) {
      const byId = new Map(_entries('question').map(e => [e.id, e]));
      entries = drill.ids.map(id => byId.get(id)).filter(Boolean);
    } else {
      entries = _questionEntries();
    }
    const qid = params.get('qid');
    if (qid) {
      const found = entries.findIndex(item => item.id === qid);
      if (found >= 0) state.cardIndex = found;
    }
    if (!entries.length) { _shell('卡片模式', '<div class="vault-empty">沒有符合條件的題目</div>'); return; }
    state.cardIndex = Math.max(0, Math.min(state.cardIndex, entries.length - 1));
    const entry = entries[state.cardIndex];
    const banner = drill ? `<div class="vault-drill-banner"><span>${_esc(drill.label)}（${entries.length} 題，跨年交錯）</span><button class="btn btn-outline btn-sm" id="vault-drill-exit">結束練習</button></div>` : '';
    const section = _shell(drill ? '練習' : '卡片模式', `${banner}<div class="vault-card-toolbar"><button class="btn btn-outline" id="vault-card-prev">上一題</button><span>${state.cardIndex + 1} / ${entries.length}</span><button class="btn btn-outline" id="vault-card-next">下一題</button></div><div id="vault-card-slot"><div class="vault-loading">載入題目…</div></div>`);
    if (drill) section.querySelector('#vault-drill-exit').onclick = () => { state.drillQueue = null; state.cardIndex = 0; _navigate('#/card'); };
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
      const relatedIds = relations ? relations.questionIds : [];
      const drillButton = relatedIds.length >= 2 && window.RexScheduler ? `<button class="btn btn-outline btn-sm" id="vault-concept-drill">練這個概念的題（跨年交錯）</button>` : '';
      section.innerHTML = `<div class="vault-concept-header"><a href="#/concepts">← 概念列表</a><h2>${_esc(title)}</h2><small>${_esc(id)}</small></div><div class="vault-note-content" id="vault-concept-note"></div><div class="vault-related"><h3>相關題目（${relatedIds.length}）${drillButton}</h3>${relatedIds.length ? relatedIds.map(qid => `<a href="#/card?qid=${encodeURIComponent(qid)}">${_esc(qid)}</a>`).join('、') : '無'}</div>`;
      NoteRenderer.renderTo(section.querySelector('#vault-concept-note'), note.raw, { record: note.record });
      const drillBtn = section.querySelector('#vault-concept-drill');
      if (drillBtn) drillBtn.onclick = () => {
        const byId = new Map(_entries('question').map(e => [e.id, e]));
        const hits = relatedIds.map(qid => ({ id: qid, year: (byId.get(qid) && byId.get(qid).years || [0])[0] }));
        const S = window.RexScheduler;
        const dayKey = S.dueWindow.dayWindow(Date.now(), { dayStartHour: DataLoader.getSettings().dayStartHour }).dayKey;
        _startDrill(S.drill.pickInterleaved(hits, { n: 10, seed: S.drill.hashSeed(dayKey + ':' + id) }), `概念練習：${title}`);
      };
    } catch (error) { section.innerHTML = `<div class="vault-error">${_esc(error.message || error)}</div>`; }
  }

  async function _renderReview() {
    const section = _shell('今日複習', '<div id="vault-review-counts" class="vault-review-counts"></div><div id="vault-review-host"><div class="vault-loading">計算佇列…</div></div><p class="vault-review-hint">空白鍵揭曉，1–4 評分（重來／困難／良好／簡單），Enter 套用預設評分。</p>');
    if (typeof ReviewView === 'undefined') { section.querySelector('#vault-review-host').innerHTML = '<div class="vault-error">review-view.js 未載入</div>'; return; }
    await ReviewView.mount(section, {
      store: DataLoader,
      entries: _questionEntries({ scorableOnly: true }),
      getQuestion: id => ContentStore.getQuestion(id),
      questionView: VaultQuestionView,
      afterRate: _kickSync,
    });
  }

  function _conceptNames() {
    const names = {};
    _entries('concept').forEach(entry => { names[entry.id] = entry.name || entry.id; });
    return names;
  }

  /** Start a temporary card-mode queue (weakness drill / concept drill). */
  function _startDrill(ids, label) {
    if (!ids || !ids.length) return;
    state.drillQueue = { ids: ids.slice(), label: label || '練習' };
    state.cardIndex = 0;
    _navigate('#/card?drill=1');
  }

  function _renderStats() {
    const section = _shell('統計與弱點', '<div id="vault-stats-host"><div class="vault-loading">計算中…</div></div>');
    if (typeof AnalyticsView === 'undefined' || !window.RexScheduler) { section.querySelector('#vault-stats-host').innerHTML = '<div class="vault-error">analytics-view.js 未載入</div>'; return; }
    const entries = _entries('question');
    const progress = DataLoader.getProgress();
    const model = AnalyticsView.buildModel({ entries, progress, conceptNames: _conceptNames() });
    const host = section.querySelector('#vault-stats-host');
    host.innerHTML = AnalyticsView.render(model);
    const byId = new Map(entries.map(e => [e.id, e]));
    host.querySelectorAll('[data-drill-group]').forEach(button => {
      button.addEventListener('click', () => {
        const group = model.groups[Number(button.dataset.drillGroup)];
        if (!group) return;
        _startDrill(AnalyticsView.drillForGroup(group, byId, Date.now(), progress.settings), `弱點練習：${group.label}`);
      });
    });
  }

  function _bindSchedulerSettings() {
    const fields = { newPerDay: 'setting-new-per-day', dayStartHour: 'setting-day-start', examSecondsPerQuestion: 'setting-exam-seconds' };
    const settings = DataLoader.getSettings();
    Object.keys(fields).forEach(key => {
      const input = document.getElementById(fields[key]);
      if (!input || input.dataset.vaultBound) return;
      input.dataset.vaultBound = '1';
      input.value = settings[key];
      input.addEventListener('change', () => {
        const next = DataLoader.setSettings({ [key]: Number(input.value) });
        input.value = next[key];
        _kickSync();
        if (_route().path === 'review') _renderRoute();
      });
    });
  }

  /* ── 模擬考：組卷條件 → session（持久化於 rex_progress.activeExam）→ 結果 ── */
  const EXAM_STATUS_LABELS = { unseen: '未做過', wrong: '最近答錯', correct: '答對過', bookmarked: '已收藏' };
  const examUi = { filters: { status: [], years: [], subspecialties: [], concepts: [], count: 20, tutor: false, timed: true } };

  function _readExamForm(section) {
    const checked = selector => [...section.querySelectorAll(selector)].filter(el => el.checked).map(el => el.value);
    return {
      status: checked('[data-exam-status]'),
      years: checked('[data-exam-year]').map(Number),
      subspecialties: checked('[data-exam-sub]'),
      concepts: String(section.querySelector('#vault-exam-concepts').value || '').split(/[,\s]+/).filter(Boolean),
      count: Number(section.querySelector('#vault-exam-count').value),
      tutor: section.querySelector('#vault-exam-tutor').checked === true,
      timed: section.querySelector('#vault-exam-timed').checked !== false,
    };
  }

  function _renderExamSetup() {
    if (typeof ExamSession === 'undefined' || !window.RexScheduler) { _shell('模擬考', '<div class="vault-error">exam-session.js 未載入</div>'); return; }
    const entries = _entries('question');
    const progress = DataLoader.getProgress();
    const active = DataLoader.getActiveExam();
    const years = [...new Set(entries.flatMap(_years))].sort();
    const subs = [...new Set(entries.map(e => String(e.subspecialty || '')).filter(Boolean))].sort();
    const f = examUi.filters;
    const pill = (attr, value, label, on) => `<label class="pill-check"><input type="checkbox" ${attr}="1" value="${_esc(value)}" ${on ? 'checked' : ''}/> ${_esc(label)}</label>`;
    const resumeHtml = active && active.entryIds.length
      ? `<div class="vault-exam-resume"><span>有一場未完成的模擬考（${Object.keys(active.answers).length} / ${active.entryIds.length} 題已作答）</span><button class="btn btn-primary btn-sm" id="vault-exam-resume">繼續</button><button class="btn btn-outline btn-sm" id="vault-exam-discard">放棄</button></div>`
      : '';
    const section = _shell('模擬考', `${resumeHtml}<form class="vault-exam-setup" id="vault-exam-form">
      <fieldset><legend>狀態（可複選，彼此為「或」；不選＝不限）</legend><div class="pill-row">${Object.keys(EXAM_STATUS_LABELS).map(s => pill('data-exam-status', s, EXAM_STATUS_LABELS[s], f.status.includes(s))).join('')}</div></fieldset>
      <fieldset><legend>年份（不選＝全部）</legend><div class="pill-row">${years.map(y => pill('data-exam-year', y, y, f.years.includes(Number(y)))).join('')}</div></fieldset>
      <fieldset><legend>次專科（不選＝全部）</legend><div class="pill-row">${subs.map(s => pill('data-exam-sub', s, s, f.subspecialties.includes(s))).join('')}</div></fieldset>
      <label>概念 id（選填，逗號分隔）<input id="vault-exam-concepts" class="text-input" value="${_esc(f.concepts.join(', '))}" placeholder="例：brain-abscess, abpa" /></label>
      <div class="vault-exam-row"><label>題數（1–100）<input id="vault-exam-count" class="text-input" type="number" min="1" max="100" value="${f.count}" /></label>
      <label class="toggle-inline"><input type="checkbox" id="vault-exam-tutor" ${f.tutor ? 'checked' : ''}/> tutor 模式（作答即揭曉）</label>
      <label class="toggle-inline"><input type="checkbox" id="vault-exam-timed" ${f.timed ? 'checked' : ''}/> 計時（每題 ${progress.settings.examSecondsPerQuestion || 0} 秒，可在設定調整）</label></div>
      <p class="vault-exam-pool" id="vault-exam-pool"></p>
      <button type="submit" id="vault-exam-start" class="btn btn-primary">開始模擬考</button>
    </form>`);
    const poolEl = section.querySelector('#vault-exam-pool');
    const refresh = () => {
      examUi.filters = _readExamForm(section);
      const n = ExamSession.poolSize(entries, progress, examUi.filters);
      poolEl.textContent = `符合條件 ${n} 題${n ? `，將抽 ${Math.min(n, Math.max(1, Math.min(100, examUi.filters.count || 20)))} 題` : ''}`;
      section.querySelector('#vault-exam-start').disabled = n === 0;
    };
    section.querySelector('#vault-exam-form').addEventListener('change', refresh);
    section.querySelector('#vault-exam-form').addEventListener('input', refresh);
    refresh();
    section.querySelector('#vault-exam-form').addEventListener('submit', event => {
      event.preventDefault();
      const session = ExamSession.start({ entries, progress, filters: examUi.filters, now: Date.now(), secondsPerQuestion: progress.settings.examSecondsPerQuestion });
      if (!session.entryIds.length) return;
      DataLoader.setActiveExam(session);
      state.examNotes = {};
      _navigate('#/exam/active');
    });
    if (active && active.entryIds.length) {
      section.querySelector('#vault-exam-resume').onclick = () => _navigate('#/exam/active');
      section.querySelector('#vault-exam-discard').onclick = () => { DataLoader.setActiveExam(null); _renderRoute(); };
    }
  }

  function _examCountdownLabel(seconds) {
    return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
  }

  async function _renderExamActive() {
    if (state.examTimer) { clearInterval(state.examTimer); state.examTimer = null; }
    const session = DataLoader.getActiveExam();
    if (!session || !session.entryIds.length) { _navigate('#/exam'); return; }
    const removed = ExamSession.pruneMissing(session, _entries('question').map(e => e.id));
    if (removed.length) { state.examRemoved = (state.examRemoved || []).concat(removed); DataLoader.setActiveExam(session); }
    if (ExamSession.isFinished(session)) { _finishExam(session); return; }
    if (session.index !== ExamSession.resumeIndex(session) && session.answers[ExamSession.currentId(session)] !== undefined) {
      session.index = ExamSession.resumeIndex(session);
      DataLoader.setActiveExam(session);
    }
    const qid = ExamSession.currentId(session);
    const total = session.entryIds.length;
    const timed = session.secondsPerQuestion > 0;
    const section = _shell('模擬考進行', `<div class="vault-card-toolbar"><span>第 ${session.index + 1} / ${total} 題${session.filters.tutor ? '（tutor）' : ''}</span>${timed ? `<span class="vault-exam-clock" id="vault-exam-clock">${_examCountdownLabel(session.secondsPerQuestion)}</span>` : ''}<button class="btn btn-outline" id="vault-exam-end">交卷</button></div><div id="vault-exam-slot"><div class="vault-loading">載入題目…</div></div><button class="btn btn-primary" id="vault-exam-next">${session.index === total - 1 ? '交卷' : '下一題'}</button>`);
    const goNext = () => { ExamSession.advance(session); DataLoader.setActiveExam(session); _renderRoute(); };
    section.querySelector('#vault-exam-end').onclick = () => { session.index = total; DataLoader.setActiveExam(session); _finishExam(session); };
    section.querySelector('#vault-exam-next').onclick = goNext;
    const token = ++state.routeToken;
    try {
      const note = await ContentStore.getQuestion(qid);
      if (token !== state.routeToken) return;
      state.examNotes = state.examNotes || {};
      state.examNotes[qid] = note;
      const slot = section.querySelector('#vault-exam-slot'); slot.innerHTML = '<div class="vault-question-host"></div>';
      DataLoader.markSeen(qid);
      const existing = session.answers[qid];
      const bound = VaultQuestionView.bind(slot.firstElementChild, note, { mode: session.filters.tutor ? 'card' : 'exam', onAnswer: result => { ExamSession.answer(session, qid, result.chosen, result.elapsedMs); DataLoader.setActiveExam(session); } });
      if (existing && existing !== ExamSession.EXPIRED) { bound.state.selected = existing; if (session.filters.tutor) bound.state.revealed = true; bound.render(); }
      if (timed) {
        let remaining = session.secondsPerQuestion;
        const clock = section.querySelector('#vault-exam-clock');
        state.examTimer = setInterval(() => {
          if (!section.isConnected) { clearInterval(state.examTimer); state.examTimer = null; return; }
          remaining -= 1;
          if (clock) clock.textContent = _examCountdownLabel(Math.max(0, remaining));
          if (remaining <= 0) {
            clearInterval(state.examTimer); state.examTimer = null;
            if (!session.answers[qid]) ExamSession.expire(session, qid); else ExamSession.advance(session);
            DataLoader.setActiveExam(session);
            _renderRoute();
          }
        }, 1000);
      }
    } catch (error) { section.querySelector('#vault-exam-slot').innerHTML = `<div class="vault-error">${_esc(error.message || error)}</div>`; }
  }

  async function _finishExam(sessionArg) {
    const session = sessionArg || DataLoader.getActiveExam();
    if (!session) { _navigate('#/exam'); return; }
    if (state.examTimer) { clearInterval(state.examTimer); state.examTimer = null; }
    const section = _shell('模擬考結果', '<div class="vault-loading">計分中…</div>');
    const notes = await Promise.all(session.entryIds.map(id => (state.examNotes && state.examNotes[id]) ? Promise.resolve(state.examNotes[id]) : ContentStore.getQuestion(id).catch(() => null)));
    const records = notes.filter(Boolean).map(note => note.record);
    const answers = ExamSession.scoringAnswers(session);
    const score = VaultQuestionView.scoreAnswers(records, answers);
    const sourceSha256ByQuestion = {};
    const wrongIds = [];
    const submittedAt = Date.now();
    records.forEach(record => {
      sourceSha256ByQuestion[record.id] = record.sourceSha256 || null;
      const chosen = answers[record.id];
      if (!chosen || !VaultQuestionView.isScorable(record.sr)) return;
      const correct = VaultQuestionView.isCorrect(record.sr, chosen);
      if (!correct) wrongIds.push(record.id);
      DataLoader.recordAnswer(record.id, { chosen, correct, scorable: true, source: 'exam', elapsedMs: session.elapsed[record.id], sourceSha256: record.sourceSha256, clientTs: submittedAt });
    });
    if (records.length) { DataLoader.addExamRecord(Object.assign({}, score, { wrongIds, sourceSha256ByQuestion, seed: session.seed, filters: session.filters })); _kickSync(); }
    DataLoader.setActiveExam(null);
    const expired = ExamSession.expiredIds(session);
    const removed = state.examRemoved || [];
    state.examRemoved = [];
    section.innerHTML = `<div class="vault-exam-result"><h3>${score.correct} / ${score.total}（${score.pct}%）</h3><p>答錯 ${score.wrong} 題，未作答 ${score.skipped} 題${expired.length ? `（其中 ${expired.length} 題逾時）` : ''}。</p>${wrongIds.length ? `<p>答錯：${wrongIds.map(id => `<a href="#/card?qid=${encodeURIComponent(id)}">${_esc(id)}</a>`).join('、')}</p>` : ''}${removed.length ? `<p class="muted">已跳過不存在的題目：${removed.map(_esc).join('、')}</p>` : ''}<p class="muted">seed ${session.seed}</p><button class="btn btn-primary" id="vault-exam-retry">再考一次</button></div>`;
    section.querySelector('#vault-exam-retry').onclick = () => _navigate('#/exam');
  }

  async function _renderRoute() {
    if (!state.indexes) return;
    const current = _route();
    _setActiveNav(current.path);
    const filterBar = document.getElementById('filter-bar');
    if (filterBar) filterBar.hidden = !['card', 'list', 'review'].includes(current.path);
    if (current.path === 'card') return _renderCard(current.params);
    if (current.path === 'list') return _renderList();
    if (current.path === 'review') return _renderReview();
    if (current.path === 'stats') return _renderStats();
    if (current.path === 'exam') return _renderExamSetup();
    if (current.path === 'exam/active') return _renderExamActive();
    if (current.path === 'concepts') return _renderConceptList();
    if (current.path.startsWith('concept/')) return _renderConcept(current.id);
    return _navigate('#/card');
  }

  async function init() {
    _hideLegacyEditorControls();
    _bindAccountPanel();
    _bindSchedulerSettings();
    document.querySelectorAll('.nav-tab, .bottom-tab').forEach(button => {
      if (button.dataset.vaultBound) return;
      button.dataset.vaultBound = '1';
      if (button.dataset.route && button.dataset.route !== '#/settings') button.addEventListener('click', () => _navigate(button.dataset.route));
    });
    try {
      state.indexes = await ContentStore.loadIndexes();
      if (typeof NoteRenderer !== 'undefined' && typeof NoteRenderer.setLinkIndexes === 'function') NoteRenderer.setLinkIndexes(state.indexes);
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
