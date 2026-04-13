/* =====================================================
   app.js — Hash Router + 主應用程式初始化
   ===================================================== */

/* ── 全域 App 物件 ── */
const App = (function () {
  'use strict';

  /* ─── 路由定義 ─── */
  const ROUTES = {
    card:        'card-view',
    list:        'list-view',
    exam:        'exam-setup',
    'exam/active':  'exam-view',
    'exam/result':  'exam-result',
    concept:     'concept-view',
  };

  /* 目前篩選狀態 */
  let _params = {
    year:    '',   // '' = 全部
    sub:     '',   // '' = 全部
    checked: false,
    q:       0,    // 卡片 index
  };

  let _currentRoute = '';
  let _dataReady    = false;

  /* ─── navigate ─── */
  function navigate(hash, paramOverrides) {
    if (paramOverrides) Object.assign(_params, paramOverrides);
    window.location.hash = hash;
  }

  /* ─── updateParams ─── */
  function updateParams(obj) {
    Object.assign(_params, obj);
  }

  /* ─── getParams ─── */
  function getParams() {
    return Object.assign({}, _params);
  }

  /* ─── 解析 hash ─── */
  function _parseHash() {
    const hash = window.location.hash || '#/card';
    const [path, query] = hash.slice(1).split('?');
    const route = path.replace(/^\//, '');

    // query params
    if (query) {
      const p = new URLSearchParams(query);
      if (p.has('year'))    _params.year    = p.get('year');
      if (p.has('sub'))     _params.sub     = p.get('sub');
      if (p.has('checked')) _params.checked = p.get('checked') === '1';
      if (p.has('q'))       _params.q       = parseInt(p.get('q'), 10) || 0;
    }

    return route;
  }

  /* ─── 顯示/隱藏 section ─── */
  function _showSection(sectionId) {
    document.querySelectorAll('.view-section').forEach(s => {
      s.classList.toggle('active', s.id === sectionId);
      s.hidden = (s.id !== sectionId);
    });
  }

  /* ─── 更新導覽列 active ─── */
  function _updateNavActive(route) {
    // 頂部 tabs
    document.querySelectorAll('.nav-tab').forEach(btn => {
      const r = (btn.dataset.route || '').replace('#/', '');
      btn.classList.toggle('active', route === r || (r === 'exam' && route.startsWith('exam')) || (r === 'concepts' && route === 'concept'));
    });
    // 底部 tabs
    document.querySelectorAll('.bottom-tab').forEach(btn => {
      const r = (btn.dataset.route || '').replace('#/', '');
      btn.classList.toggle('active', route === r || (r === 'exam' && route.startsWith('exam')) || (r === 'concepts' && route === 'concept'));
    });
  }

  /* ─── 路由處理 ─── */
  async function _handleRoute() {
    if (!_dataReady) return;  // 資料尚未就緒，先排隊

    let route = _parseHash();

    // 概念頁 /concept/{id} or /concepts (列表)
    let conceptId = null;
    if (route === 'concepts') {
      route = 'concept'; // 使用同一個 section
    } else if (route.startsWith('concept/')) {
      conceptId = route.slice('concept/'.length);
      route = 'concept';
    }

    // 預設路由
    if (!route || !ROUTES[route]) route = 'card';

    _currentRoute = route;
    _updateNavActive(route);

    const sectionId = ROUTES[route];
    _showSection(sectionId);

    // 篩選列：只在 card/list 顯示
    const filterBar = document.getElementById('filter-bar');
    if (filterBar) {
      filterBar.hidden = !['card', 'list'].includes(route);
    }

    // ── 根據路由執行模組 ──
    if (route === 'card') {
      _renderCardView();
    } else if (route === 'list') {
      _renderListView();
    } else if (route === 'exam') {
      // exam setup：不做特別操作，保持 HTML 原樣
    } else if (route === 'exam/active') {
      // exam-mode 自己管理
    } else if (route === 'exam/result') {
      // exam-mode 自己管理
    } else if (route === 'concept') {
      if (conceptId) ConceptCards.renderConcept(conceptId);
      else ConceptCards.renderAll();
    }
  }

  /* ─── 卡片模式渲染 ─── */
  function _renderCardView() {
    const years = _params.year ? [_params.year] : null;
    const subs  = _params.sub  ? [_params.sub]  : null;
    const qs    = QuestionStore.getQuestions({
      years,
      subspecialties: subs,
      checkedOnly: _params.checked,
    });
    CardMode.load(qs, _params.q || 0);
  }

  /* ─── 列表模式渲染 ─── */
  function _renderListView() {
    const years = _params.year ? [_params.year] : null;
    const subs  = _params.sub  ? [_params.sub]  : null;
    const qs    = QuestionStore.getQuestions({
      years,
      subspecialties: subs,
      checkedOnly: _params.checked,
    });
    ListMode.load(qs);
  }

  /* ─── 篩選列事件 ─── */
  function _initFilters() {
    // 年份 select
    const yearSel = document.getElementById('year-select');
    if (yearSel) {
      yearSel.addEventListener('change', function () {
        _params.year = this.value;
        _params.q    = 0;
        _rerenderCurrentView();
      });
    }

    // 次專科 pill
    document.querySelectorAll('#subspecialty-pills .pill').forEach(btn => {
      btn.addEventListener('click', function () {
        document.querySelectorAll('#subspecialty-pills .pill').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        _params.sub = this.dataset.sub;
        _params.q   = 0;
        _rerenderCurrentView();
      });
    });

    // 只顯示已確認 toggle
    const checkedTog = document.getElementById('checked-toggle');
    if (checkedTog) {
      checkedTog.addEventListener('change', function () {
        _params.checked = this.checked;
        _params.q       = 0;
        _rerenderCurrentView();
      });
    }
  }

  /* ─── 重新渲染目前視圖 ─── */
  function _rerenderCurrentView() {
    if (_currentRoute === 'card') _renderCardView();
    else if (_currentRoute === 'list') _renderListView();
  }

  /* ─── 年份 select 填入 ─── */
  async function _populateYearSelect() {
    const sel  = document.getElementById('year-select');
    const cbContainer = document.getElementById('exam-year-checkboxes');

    const years = await QuestionStore.getAllYears();

    if (sel) {
      const opts = years.map(y => `<option value="${y}">${y} 年</option>`).join('');
      sel.innerHTML = '<option value="">全部年份</option>' + opts;
    }

    ExamMode.initYearCheckboxes(years);
  }

  /* ─── 設定面板 ─── */
  function _initSettings() {
    const btn   = document.getElementById('settings-toggle');
    const panel = document.getElementById('settings-panel');
    if (!btn || !panel) return;

    btn.addEventListener('click', () => {
      panel.hidden = !panel.hidden;
      btn.classList.toggle('active', !panel.hidden);
    });

    // 點外部關閉（但編輯模式 toggle 區域不觸發關閉）
    document.addEventListener('click', function (e) {
      if (!panel.hidden && !panel.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
        // 不要在 toggle 剛改變時立刻關閉
        setTimeout(() => {
          panel.hidden = true;
          btn.classList.remove('active');
        }, 50);
      }
    });
  }

  /* ─── nav tab 點擊 ─── */
  function _initNavTabs() {
    document.querySelectorAll('.nav-tab, .bottom-tab').forEach(btn => {
      btn.addEventListener('click', function () {
        const route = this.dataset.route;
        if (route === '#/settings') {
          // 手機底部設定 tab：直接 toggle settings panel
          const panel = document.getElementById('settings-panel');
          const togBtn = document.getElementById('settings-toggle');
          if (panel) {
            panel.hidden = !panel.hidden;
            if (togBtn) togBtn.classList.toggle('active', !panel.hidden);
          }
        } else if (route) {
          navigate(route);
        }
      });
    });
  }

  /* ─── 模擬考次專科 pill 初始化 ─── */
  function _initExamSubPills() {
    document.querySelectorAll('#exam-sub-pills .pill').forEach(btn => {
      btn.addEventListener('click', function () {
        document.querySelectorAll('#exam-sub-pills .pill').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
      });
    });
  }

  /* ─── 編輯模式切換回呼 ─── */
  function onEditModeChange(isEdit) {
    // 重新渲染目前視圖以顯示/隱藏編輯面板
    _rerenderCurrentView();
  }

  /* ─── 初始化 ─── */
  async function _init() {
    // 各模組初始化
    Editor.init();
    CardMode.init();
    ListMode.init();
    ExamMode.init();

    _initSettings();
    _initNavTabs();
    _initFilters();
    _initExamSubPills();

    // 顯示載入中
    const main = document.getElementById('main-content');
    if (main) main.style.opacity = '.5';

    try {
      // 載入所有可用年份
      await DataLoader.loadAllAvailableYears();
      await DataLoader.loadConcepts();
      _dataReady = true;

      await _populateYearSelect();

      if (main) main.style.opacity = '1';
    } catch (err) {
      console.error('[App] 資料載入失敗', err);
      if (main) {
        main.style.opacity = '1';
        main.innerHTML = `<div style="text-align:center;padding:60px;color:var(--danger);">
          <strong>資料載入失敗</strong><br/><small>${err.message || err}</small>
        </div>`;
      }
      return;
    }

    // 初次路由
    await _handleRoute();
  }

  /* ─── hashchange 監聽 ─── */
  window.addEventListener('hashchange', () => {
    // 關閉設定面板
    const panel = document.getElementById('settings-panel');
    if (panel && !panel.hidden) {
      panel.hidden = true;
      const btn = document.getElementById('settings-toggle');
      if (btn) btn.classList.remove('active');
    }
    _handleRoute();
  });

  /* ─── DOM 就緒啟動 ─── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _init);
  } else {
    _init();
  }

  /* ─── 公開介面 ─── */
  return {
    navigate,
    getParams,
    updateParams,
    onEditModeChange,
  };
})();
