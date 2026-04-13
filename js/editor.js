/* =====================================================
   editor.js — 問題編輯表單
   ===================================================== */

const Editor = (function () {
  'use strict';

  let _editMode = false;
  let _currentId = null;
  let _onSave    = null;

  /* ── 初始化 ── */
  function init() {
    const toggle = document.getElementById('edit-mode-toggle');
    if (!toggle) return;

    toggle.addEventListener('change', function () {
      _editMode = this.checked;
      _updateBanner();
      // 延遲一幀確保 DOM 更新完成後再重新渲染
      requestAnimationFrame(() => {
        if (window.App) App.onEditModeChange(_editMode);
      });
    });

    const discardBtn = document.getElementById('discard-btn');
    if (discardBtn) {
      discardBtn.addEventListener('click', function () {
        if (!confirm('確定要放棄所有編輯嗎？此操作無法復原。')) return;
        DataLoader.discardAllEdits();
        _updatePendingBadge();
        showToast('已放棄所有編輯，重新載入資料中…', 'success');
        setTimeout(() => window.location.reload(), 1200);
      });
    }

    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', _exportJSON);
    }
  }

  /* ── 是否為編輯模式 ── */
  function isEditMode() { return _editMode; }

  /* ── 更新頂部 banner ── */
  function _updateBanner() {
    let banner = document.getElementById('edit-mode-banner');
    if (_editMode) {
      if (!banner) {
        banner = document.createElement('div');
        banner.id = 'edit-mode-banner';
        banner.className = 'edit-mode-banner';
        banner.textContent = '✏️ 編輯模式已開啟 — 所有修改將儲存於瀏覽器';
        const nav = document.getElementById('top-nav');
        if (nav) nav.insertAdjacentElement('afterend', banner);
      }
      banner.hidden = false;
    } else {
      if (banner) banner.hidden = true;
    }
  }

  /* ── 更新待存徽章 ── */
  function _updatePendingBadge() {
    const badge = document.getElementById('pending-badge');
    const countEl = document.getElementById('pending-count');
    const n = DataLoader.countPendingEdits();
    if (badge && countEl) {
      countEl.textContent = n;
      badge.hidden = (n === 0);
    }
  }

  /* ── 渲染編輯表單到指定容器 ── */
  function renderForm(container, question, onSave) {
    if (!container || !question) return;
    _currentId = question.id;
    _onSave    = onSave;

    const subs = ['ABD','CV','CH','NR','MSK','H&N','PED','IR','Physics','Breast','US','Unknown'];
    const subOptions = subs.map(s =>
      `<option value="${s}" ${question.subspecialty === s ? 'selected' : ''}>${s}</option>`
    ).join('');

    const optionsHtml = (question.options || []).map((opt, i) => `
      <div class="edit-form-group">
        <label class="edit-form-label">選項 ${opt.letter}</label>
        <textarea class="edit-textarea" data-opt="${i}" rows="2">${_esc(opt.text)}</textarea>
      </div>
    `).join('');

    container.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
        <strong style="font-size:.9rem;">✏️ 編輯：${_esc(question.id)}</strong>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">次專科</label>
        <select class="select-input" id="edit-subspecialty">${subOptions}</select>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">題目</label>
        <textarea class="edit-textarea" id="edit-question-text" rows="4">${_esc(question.questionText)}</textarea>
      </div>
      ${optionsHtml}
      <div class="edit-form-group">
        <label class="edit-form-label">正確答案（字母）</label>
        <input type="text" class="text-input" id="edit-correct-answer" value="${_esc(question.correctAnswer || '')}" maxlength="1" style="width:80px;text-transform:uppercase;" />
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">解析</label>
        <textarea class="edit-textarea" id="edit-explanation" rows="5">${_esc(question.explanation || '')}</textarea>
      </div>
      <div class="edit-actions">
        <button class="btn btn-primary" id="edit-save-btn">儲存</button>
        <button class="btn btn-outline" id="edit-cancel-btn">取消</button>
      </div>
    `;

    container.querySelector('#edit-save-btn').addEventListener('click', _handleSave);
    container.querySelector('#edit-cancel-btn').addEventListener('click', function () {
      container.innerHTML = '';
      const panel = container.closest('.edit-panel');
      if (panel) panel.hidden = true;
    });
  }

  /* ── 儲存處理 ── */
  function _handleSave() {
    const q = QuestionStore.getQuestionById(_currentId);
    if (!q) return;

    const patch = {};
    const subEl  = document.getElementById('edit-subspecialty');
    const textEl = document.getElementById('edit-question-text');
    const ansEl  = document.getElementById('edit-correct-answer');
    const expEl  = document.getElementById('edit-explanation');

    if (subEl)  patch.subspecialty  = subEl.value;
    if (textEl) patch.questionText  = textEl.value;
    if (ansEl)  patch.correctAnswer = ansEl.value.toUpperCase();
    if (expEl)  patch.explanation   = expEl.value;

    // 選項
    const optTextareas = document.querySelectorAll('.edit-textarea[data-opt]');
    if (optTextareas.length > 0 && q.options) {
      const options = q.options.map((opt, i) => {
        const el = optTextareas[i];
        return el ? Object.assign({}, opt, { text: el.value }) : opt;
      });
      patch.options = options;
    }

    DataLoader.saveQuestionEdit(_currentId, patch);
    _updatePendingBadge();
    showToast('已儲存編輯', 'success');

    if (typeof _onSave === 'function') _onSave(_currentId, patch);
  }

  /* ── 匯出 JSON ── */
  function _exportJSON() {
    const data = DataLoader.exportAllEdits();
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'rex-edits-' + new Date().toISOString().slice(0,10) + '.json';
    a.click();
    URL.revokeObjectURL(url);
    showToast('已匯出 JSON', 'success');
  }

  /* ── 跳脫 HTML ── */
  function _esc(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  return {
    init,
    isEditMode,
    renderForm,
    updatePendingBadge: _updatePendingBadge,
  };
})();

/* ── 全域吐司函式 ── */
function showToast(msg, type, duration) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast' + (type ? ' ' + type : '');
  toast.textContent = msg;
  container.appendChild(toast);
  const t = duration || 2800;
  setTimeout(() => {
    toast.style.animation = 'fadeOut .3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, t);
}
