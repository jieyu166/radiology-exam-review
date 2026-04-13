/* =====================================================
   card-mode.js — 卡片翻轉模式
   ===================================================== */

const CardMode = (function () {
  'use strict';

  let _questions  = [];
  let _index      = 0;
  let _flipped    = false;

  const _els = () => ({
    container:    document.getElementById('card-container'),
    counter:      document.getElementById('card-counter'),
    prev:         document.getElementById('card-prev'),
    next:         document.getElementById('card-next'),
    toggleAnswer: document.getElementById('card-toggle-answer'),
    markChecked:  document.getElementById('card-mark-checked'),
    editPanel:    document.getElementById('card-edit-panel'),
    editForm:     document.getElementById('card-edit-form'),
  });

  /* ── 初始化 ── */
  function init() {
    const e = _els();
    if (!e.prev) return;

    e.prev.addEventListener('click', () => navigate(-1));
    e.next.addEventListener('click', () => navigate(1));
    e.toggleAnswer.addEventListener('click', toggleAnswer);
    e.markChecked.addEventListener('click', markCurrentChecked);

    // 鍵盤
    document.addEventListener('keydown', _handleKey);
  }

  /* ── 載入問題集 ── */
  function load(questions, startIndex) {
    _questions = questions;
    _index     = Math.max(0, Math.min(startIndex || 0, questions.length - 1));
    _flipped   = false;
    _render();
  }

  /* ── 前後導覽 ── */
  function navigate(delta) {
    const newIdx = _index + delta;
    if (newIdx < 0 || newIdx >= _questions.length) return;
    _index   = newIdx;
    _flipped = false;

    // 更新 hash query
    if (window.App) {
      App.updateParams({ q: _index });
    }
    _render();
  }

  /* ── 翻轉 ── */
  function toggleAnswer() {
    _flipped = !_flipped;
    const card = document.querySelector('.flash-card');
    const btn  = _els().toggleAnswer;
    if (card) card.classList.toggle('flipped', _flipped);
    if (btn) btn.textContent = _flipped ? '隱藏答案' : '顯示答案';
  }

  /* ── 標記已確認 ── */
  function markCurrentChecked() {
    if (!_questions.length) return;
    const q = _questions[_index];
    const newVal = !q.checked;
    DataLoader.saveQuestionEdit(q.id, { checked: newVal });
    q.checked = newVal;
    _render();
    Editor.updatePendingBadge();
    showToast(newVal ? '已標記為已確認' : '已取消確認', 'success');
  }

  /* ── 渲染當前卡片 ── */
  function _render() {
    const e = _els();
    if (!e.container) return;

    if (_questions.length === 0) {
      e.container.innerHTML = '<div style="text-align:center;padding:60px;color:var(--text-muted);">沒有符合條件的題目</div>';
      e.counter.textContent = '0 / 0';
      return;
    }

    const q = _questions[_index];
    e.counter.textContent = `${_index + 1} / ${_questions.length}`;

    // 前後按鈕 disabled
    e.prev.disabled = (_index === 0);
    e.next.disabled = (_index === _questions.length - 1);

    // 標記按鈕文字
    const markBtn = e.markChecked;
    if (markBtn) {
      markBtn.innerHTML = q.checked
        ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>已確認`
        : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>標記已確認`;
      markBtn.classList.toggle('btn-success', q.checked);
      markBtn.classList.toggle('btn-outline', !q.checked);
    }

    // 顯示/隱藏答案按鈕
    const toggleBtn = e.toggleAnswer;
    if (toggleBtn) toggleBtn.textContent = _flipped ? '隱藏答案' : '顯示答案';

    e.container.innerHTML = _buildCard(q, _flipped);

    // 圖片燈箱
    e.container.querySelectorAll('.question-images img').forEach(img => {
      img.addEventListener('click', ev => { ev.stopPropagation(); _lightbox(img.src); });
    });

    // 編輯按鈕（在卡片上方顯示）
    if (Editor.isEditMode()) {
      const editBtn = e.container.querySelector('.card-edit-btn');
      if (editBtn) {
        editBtn.addEventListener('click', ev => {
          ev.stopPropagation();
          if (e.editPanel) {
            e.editPanel.hidden = !e.editPanel.hidden;
            if (!e.editPanel.hidden) {
              Editor.renderForm(e.editForm, q, (id, patch) => {
                Object.assign(q, patch);
                _render();
              });
            }
          }
        });
      }
    }
    if (e.editPanel && !Editor.isEditMode()) e.editPanel.hidden = true;
  }

  /* ── 建構卡片 HTML ── */
  function _buildCard(q, flipped) {
    const subBadge  = `<span class="badge badge-sub" data-sub="${_esc(q.subspecialty)}">${_esc(q.subspecialty)}</span>`;
    const yearBadge = `<span class="badge badge-year">${q.year}</span>`;
    const numBadge  = `<span class="badge badge-num">#${q.number}</span>`;
    const unchecked = q.checked ? '' : `<span class="badge-unchecked">未確認</span>`;
    const editBtn = Editor.isEditMode()
      ? `<button class="btn btn-sm btn-outline card-edit-btn" style="margin-left:auto;font-size:.75rem;padding:4px 10px;" onclick="event.stopPropagation()">✏️ 編輯</button>`
      : '';

    const optFront = (q.options || []).map(opt =>
      `<li class="card-option">
        <span class="option-letter">${_esc(opt.letter)}.</span>
        <span>${_esc(opt.text)}</span>
      </li>`
    ).join('');

    const optBack = (q.options || []).map(opt => {
      const isCorrect = opt.letter === q.correctAnswer;
      const cls = isCorrect ? 'correct' : '';
      return `<li class="card-option ${cls}">
        <span class="option-letter">${_esc(opt.letter)}.</span>
        <span>${_esc(opt.text)}</span>
      </li>`;
    }).join('');

    const images = (q.images || []).length > 0
      ? `<div class="question-images">${q.images.map(src =>
          `<img src="${_esc(src)}" alt="題目圖片" loading="lazy" />`
        ).join('')}</div>`
      : '';

    const explanation = q.explanation
      ? `<div class="card-explanation">${_esc(q.explanation)}</div>`
      : '';

    return `
      <div class="flash-card ${q.checked ? '' : 'unchecked'} ${flipped ? 'flipped' : ''}">
        <!-- 正面 -->
        <div class="card-face card-front">
          <div class="card-face-header">
            ${numBadge}${yearBadge}${subBadge}${unchecked}
            ${editBtn || '<span style="margin-left:auto;font-size:.75rem;color:var(--text-muted);">點擊翻轉</span>'}
          </div>
          <p class="card-question-text">${_esc(q.questionText)}</p>
          ${images}
          <ul class="card-options-list">${optFront}</ul>
        </div>
        <!-- 背面 -->
        <div class="card-face card-back">
          <div class="card-face-header">
            ${numBadge}${yearBadge}${subBadge}
            <span class="badge badge-checked">答案：${_esc(q.correctAnswer || '?')}</span>
            ${editBtn}
          </div>
          <p class="card-question-text">${_esc(q.questionText)}</p>
          <ul class="card-options-list">${optBack}</ul>
          ${explanation}
        </div>
      </div>
    `;
  }

  /* ── 鍵盤導覽 ── */
  function _handleKey(e) {
    // 只在卡片模式下生效
    const section = document.getElementById('card-view');
    if (!section || !section.classList.contains('active')) return;
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   navigate(-1);
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown')  navigate(1);
    if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); toggleAnswer(); }
  }

  /* ── 燈箱 ── */
  function _lightbox(src) {
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.innerHTML = `<img src="${_esc(src)}" alt="大圖預覽" />`;
    box.addEventListener('click', () => box.remove());
    document.body.appendChild(box);
  }

  function _esc(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ── 取得目前 index ── */
  function getCurrentIndex() { return _index; }

  return { init, load, navigate, toggleAnswer, markCurrentChecked, getCurrentIndex };
})();
