/* =====================================================
   editor.js — 問題編輯表單
   ===================================================== */

const Editor = (function () {
  'use strict';

  let _editMode = false;
  let _currentId = null;
  let _onSave    = null;

  const OPTION_LETTERS = ['A', 'B', 'C', 'D', 'E'];

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

    const optionsHtml = _buildOptionRows(question.options || []);
    const yearsHtml = _buildYearTags(question);

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
        ${Format.toolbar('edit-question-text')}
        <textarea class="edit-textarea" id="edit-question-text" rows="4">${_esc(question.questionText)}</textarea>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">選項</label>
        <div class="edit-options-list" id="edit-options-list">
          ${optionsHtml}
        </div>
        <button class="btn btn-sm btn-outline btn-add-option" id="edit-option-add" type="button">＋ 新增選項</button>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">正確答案（字母）</label>
        <input type="text" class="text-input" id="edit-correct-answer" value="${_esc(question.correctAnswer || '')}" maxlength="1" style="width:80px;text-transform:uppercase;" />
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">出現年份</label>
        <div class="edit-year-primary">主年份：${_esc(question.year)}</div>
        <div class="concept-tags" id="edit-year-tags">${yearsHtml}</div>
        <div style="display:flex;gap:6px;margin-top:8px;">
          <input type="number" class="text-input" id="edit-year-input" placeholder="加入年份（如 2017）" style="flex:1;" />
          <button class="btn btn-sm btn-outline" id="edit-year-add" type="button">新增</button>
        </div>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">解析</label>
        ${Format.toolbar('edit-explanation')}
        <textarea class="edit-textarea" id="edit-explanation" rows="8">${_esc(question.explanation || '')}</textarea>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">關聯概念</label>
        <div class="concept-tags" id="edit-concept-tags">
          ${(question.concepts || []).map(c =>
            `<span class="concept-tag" data-concept="${_esc(c)}">${_esc(c)} <span class="concept-tag-remove" data-concept="${_esc(c)}">×</span></span>`
          ).join('')}
        </div>
        <div style="display:flex;gap:6px;margin-top:8px;">
          <input type="text" class="text-input" id="edit-concept-input" placeholder="輸入概念 ID（如 upj-obstruction）" style="flex:1;" />
          <button class="btn btn-sm btn-outline" id="edit-concept-add" type="button">新增</button>
        </div>
      </div>
      <div class="edit-actions">
        <button class="btn btn-primary" id="edit-save-btn">儲存</button>
        <button class="btn btn-outline" id="edit-cancel-btn">取消</button>
      </div>
    `;

    // 格式工具列
    Format.bindToolbar(container);

    _bindOptionRows(container);
    _bindYearTags(container, question);

    // 概念標籤事件
    _bindConceptTags(container, question);

    container.querySelector('#edit-save-btn').addEventListener('click', _handleSave);
    container.querySelector('#edit-cancel-btn').addEventListener('click', function () {
      container.innerHTML = '';
      const panel = container.closest('.edit-panel');
      if (panel) panel.hidden = true;
    });
  }

  function _buildOptionRows(options) {
    const normalized = options.slice(0, 5);
    while (normalized.length < 3) normalized.push({ letter: OPTION_LETTERS[normalized.length], text: '' });
    return normalized.map((opt, i) => _buildOptionRow(i, opt.text || '')).join('');
  }

  function _buildOptionRow(index, text) {
    const letter = OPTION_LETTERS[index];
    return `
      <div class="option-row" data-option-row>
        <label class="option-row-letter">${letter}</label>
        <textarea class="edit-textarea" data-opt="${index}" rows="2">${_esc(text)}</textarea>
        <button class="btn btn-sm btn-outline btn-remove-option" type="button" aria-label="移除選項 ${letter}">✕</button>
      </div>
    `;
  }

  function _bindOptionRows(container) {
    const list = container.querySelector('#edit-options-list');
    const addBtn = container.querySelector('#edit-option-add');
    if (!list || !addBtn) return;

    const refresh = () => {
      const rows = Array.from(list.querySelectorAll('[data-option-row]'));
      rows.forEach((row, i) => {
        const letter = OPTION_LETTERS[i];
        row.querySelector('.option-row-letter').textContent = letter;
        const textarea = row.querySelector('textarea[data-opt]');
        if (textarea) textarea.dataset.opt = String(i);
        const removeBtn = row.querySelector('.btn-remove-option');
        if (removeBtn) {
          removeBtn.disabled = rows.length <= 3;
          removeBtn.setAttribute('aria-label', '移除選項 ' + letter);
        }
      });
      addBtn.disabled = rows.length >= 5;
    };

    addBtn.addEventListener('click', () => {
      const count = list.querySelectorAll('[data-option-row]').length;
      if (count >= 5) return;
      list.insertAdjacentHTML('beforeend', _buildOptionRow(count, ''));
      refresh();
    });

    list.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-remove-option');
      if (!btn) return;
      const rows = list.querySelectorAll('[data-option-row]');
      if (rows.length <= 3) return;
      btn.closest('[data-option-row]').remove();
      refresh();
    });

    refresh();
  }

  function _buildYearTags(question) {
    const years = QuestionStore.getQuestionYears(question);
    return years.map(y => _yearTagHtml(y, y === parseInt(question.year, 10))).join('');
  }

  function _yearTagHtml(year, locked) {
    const remove = locked ? '' : ` <span class="concept-tag-remove" data-year="${_esc(year)}">×</span>`;
    const lockedAttr = locked ? ' data-locked="1"' : '';
    return `<span class="concept-tag year-tag" data-year="${_esc(year)}"${lockedAttr}>${_esc(year)}${remove}</span>`;
  }

  function _bindYearTags(container, question) {
    const tagsEl = container.querySelector('#edit-year-tags');
    const input = container.querySelector('#edit-year-input');
    const addBtn = container.querySelector('#edit-year-add');
    if (!tagsEl || !input || !addBtn) return;

    const currentYears = () => Array.from(tagsEl.querySelectorAll('.year-tag'))
      .map(el => parseInt(el.dataset.year, 10))
      .filter(Number.isFinite);

    const addYear = () => {
      const val = parseInt(input.value, 10);
      if (!Number.isFinite(val) || val <= 0) {
        showToast('請輸入有效年份', 'warning');
        return;
      }
      if (currentYears().includes(val)) {
        showToast('此年份已存在', 'warning');
        return;
      }
      tagsEl.insertAdjacentHTML('beforeend', _yearTagHtml(val, val === parseInt(question.year, 10)));
      input.value = '';
    };

    addBtn.addEventListener('click', function (e) { e.stopPropagation(); addYear(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); addYear(); }
    });
    tagsEl.addEventListener('click', function (e) {
      const btn = e.target.closest('.concept-tag-remove[data-year]');
      if (!btn) return;
      const tag = btn.closest('.year-tag');
      if (tag && tag.dataset.locked !== '1') tag.remove();
    });
  }

  /* ── 概念標籤管理 ── */
  function _bindConceptTags(container, question) {
    // 移除按鈕
    container.querySelectorAll('.concept-tag-remove').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        const cid = this.dataset.concept;
        question.concepts = (question.concepts || []).filter(c => c !== cid);
        const tag = this.closest('.concept-tag');
        if (tag) tag.remove();
      });
    });

    // 新增按鈕
    const addBtn = container.querySelector('#edit-concept-add');
    const input = container.querySelector('#edit-concept-input');
    if (addBtn && input) {
      const doAdd = () => {
        const val = Format.normalizeId(input.value);
        if (!val) return;
        if (!question.concepts) question.concepts = [];
        if (question.concepts.includes(val)) {
          showToast('此概念已存在', 'warning');
          return;
        }
        question.concepts.push(val);
        const tagsEl = container.querySelector('#edit-concept-tags');
        if (tagsEl) {
          tagsEl.insertAdjacentHTML('beforeend',
            `<span class="concept-tag" data-concept="${_esc(val)}">${_esc(val)} <span class="concept-tag-remove" data-concept="${_esc(val)}">×</span></span>`
          );
          // 綁定新增的移除按鈕
          const newRemove = tagsEl.querySelector(`.concept-tag-remove[data-concept="${val}"]`);
          if (newRemove) {
            newRemove.addEventListener('click', function (e) {
              e.stopPropagation();
              question.concepts = question.concepts.filter(c => c !== val);
              this.closest('.concept-tag').remove();
            });
          }
        }
        input.value = '';
      };
      addBtn.addEventListener('click', function (e) { e.stopPropagation(); doAdd(); });
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); doAdd(); }
      });
    }
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
    const optRows = Array.from(document.querySelectorAll('#edit-options-list [data-option-row]'));
    if (optRows.length > 0) {
      const options = optRows.map((row, i) => {
        const el = row.querySelector('textarea[data-opt]');
        return { letter: OPTION_LETTERS[i], text: el ? el.value : '' };
      });
      patch.options = options;
    }

    if (ansEl && patch.options) {
      const validAnswers = new Set(patch.options.map(opt => opt.letter));
      if (!validAnswers.has(patch.correctAnswer)) {
        showToast('正確答案必須是目前選項中的字母', 'warning');
        return;
      }
    }

    const yearTags = Array.from(document.querySelectorAll('#edit-year-tags .year-tag'));
    if (yearTags.length > 0) {
      const canonicalYear = parseInt(q.year, 10);
      const years = Array.from(new Set([
        canonicalYear,
        ...yearTags.map(el => parseInt(el.dataset.year, 10)).filter(Number.isFinite)
      ])).sort((a, b) => a - b);
      const original = QuestionStore.getQuestionYears(q);
      if (Array.isArray(q.years) || years.join(',') !== original.join(',')) {
        patch.years = years;
      }
    }

    // 概念
    const tagEls = document.querySelectorAll('#edit-concept-tags .concept-tag');
    if (tagEls.length > 0 || q.concepts) {
      patch.concepts = Array.from(tagEls).map(el => el.dataset.concept);
    }

    DataLoader.saveQuestionEdit(_currentId, patch);
    if (patch.years) _ensureYearControls(patch.years);
    _updatePendingBadge();
    showToast('已儲存編輯', 'success');

    if (typeof _onSave === 'function') _onSave(_currentId, patch);
  }

  function _ensureYearControls(years) {
    const cleanYears = Array.from(new Set((years || [])
      .map(y => parseInt(y, 10))
      .filter(Number.isFinite)))
      .sort((a, b) => b - a);

    const sel = document.getElementById('year-select');
    if (sel) {
      const selected = sel.value;
      const existing = new Set(Array.from(sel.options).map(opt => opt.value));
      for (const y of cleanYears) {
        if (!existing.has(String(y))) {
          sel.insertAdjacentHTML('beforeend', `<option value="${_esc(y)}">${_esc(y)} 年</option>`);
        }
      }
      const all = Array.from(sel.options).filter(opt => opt.value);
      all.sort((a, b) => parseInt(b.value, 10) - parseInt(a.value, 10));
      sel.innerHTML = '<option value="">全部年份</option>' + all.map(opt => opt.outerHTML).join('');
      sel.value = selected;
    }

    const cbContainer = document.getElementById('exam-year-checkboxes');
    if (cbContainer) {
      const existing = new Set(Array.from(cbContainer.querySelectorAll('input')).map(input => input.value));
      for (const y of cleanYears) {
        if (!existing.has(String(y))) {
          cbContainer.insertAdjacentHTML('beforeend', `
            <label class="checkbox-item">
              <input type="checkbox" value="${_esc(y)}" checked />
              ${_esc(y)}年
            </label>
          `);
        }
      }
    }
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
