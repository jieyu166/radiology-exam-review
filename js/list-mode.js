/* =====================================================
   list-mode.js — 列表模式（Accordion）
   ===================================================== */

const ListMode = (function () {
  'use strict';

  let _questions  = [];
  let _sortBy     = 'number';
  let _openId     = null;

  /* ── 初始化 ── */
  function init() {
    const sortSel = document.getElementById('list-sort-select');
    if (sortSel) {
      sortSel.addEventListener('change', function () {
        _sortBy = this.value;
        _render();
      });
    }
  }

  /* ── 載入並渲染 ── */
  function load(questions) {
    _questions = questions;
    _openId    = null;
    _render();
  }

  /* ── 渲染列表 ── */
  function _render() {
    const list    = document.getElementById('accordion-list');
    const countEl = document.getElementById('list-count');
    if (!list) return;

    let qs = _questions.slice();

    // 排序
    if (_sortBy === 'subspecialty') {
      qs.sort((a, b) => (a.subspecialty || '').localeCompare(b.subspecialty || '') || a.number - b.number);
    } else {
      qs.sort((a, b) => a.year - b.year || a.number - b.number);
    }

    if (countEl) countEl.textContent = `共 ${qs.length} 題`;

    if (qs.length === 0) {
      list.innerHTML = '<div style="text-align:center;padding:60px;color:var(--text-muted);">沒有符合條件的題目</div>';
      return;
    }

    list.innerHTML = qs.map(q => _buildItem(q)).join('');

    // 綁定事件
    list.querySelectorAll('.accordion-header').forEach(btn => {
      btn.addEventListener('click', function () {
        const id   = this.dataset.id;
        const item = this.closest('.accordion-item');
        const isOpen = item.classList.contains('open');
        // 關閉所有
        list.querySelectorAll('.accordion-item.open').forEach(el => el.classList.remove('open'));
        // 若之前是關閉的就展開
        if (!isOpen) {
          item.classList.add('open');
          _openId = id;
        } else {
          _openId = null;
        }
      });
    });

    // 標記已確認按鈕
    list.querySelectorAll('.btn-check-toggle').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        const id = this.dataset.id;
        _toggleChecked(id, this);
      });
    });

    // 前往卡片按鈕
    list.querySelectorAll('.btn-goto-card').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        const id  = this.dataset.id;
        const idx = _questions.findIndex(q => q.id === id);
        if (idx !== -1 && window.App) App.navigate('#/card', { q: idx });
      });
    });

    // 編輯按鈕
    list.querySelectorAll('.btn-list-edit').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        const id = this.dataset.id;
        const formEl = document.getElementById('list-edit-form-' + id);
        if (!formEl) return;
        const isHidden = formEl.hidden;
        // 關閉其他編輯表單
        list.querySelectorAll('.list-edit-form').forEach(f => { f.hidden = true; f.innerHTML = ''; });
        if (isHidden) {
          formEl.hidden = false;
          const q = QuestionStore.getQuestionById(id);
          if (q) {
            Editor.renderForm(formEl, q, (savedId, patch) => {
              Object.assign(q, patch);
              _render();
            });
          }
        }
      });
    });

    // 恢復展開狀態
    if (_openId) {
      const hdr = list.querySelector(`.accordion-header[data-id="${_openId}"]`);
      if (hdr) hdr.closest('.accordion-item').classList.add('open');
    }
  }

  /* ── 建構單一 accordion 項目 ── */
  function _buildItem(q) {
    const subBadge  = `<span class="badge badge-sub" data-sub="${_esc(q.subspecialty)}">${_esc(q.subspecialty)}</span>`;
    const yearBadge = `<span class="badge badge-year">${QuestionStore.getQuestionYears(q).join(' / ')}</span>`;
    const checked   = q.checked
      ? `<span class="badge badge-checked">已確認</span>`
      : `<span class="badge-unchecked">未確認</span>`;
    const uncheckedCls = q.checked ? '' : 'unchecked';

    const optionsHtml = (q.options || []).map(opt => {
      const isCorrect = opt.letter === q.correctAnswer;
      return `<li class="list-option ${isCorrect ? 'correct' : ''}">
        <span class="option-letter">${_esc(opt.letter)}.</span>
        <span>${Format.render(opt.text)}</span>
      </li>`;
    }).join('');

    const explanation = q.explanation
      ? `<div class="list-explanation">${Format.render(q.explanation)}</div>`
      : '';

    const conceptLinks = (q.concepts || []).length > 0
      ? `<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:6px;">
          ${q.concepts.map(c => `<a href="#/concept/${_esc(c)}" class="concept-link">${_esc(c)}</a>`).join('')}
        </div>`
      : '';

    const images = (q.images || []).length > 0
      ? `<div class="question-images">${q.images.map(src =>
          `<img src="${_esc(src)}" alt="題目圖片" loading="lazy" />`
        ).join('')}</div>`
      : '';

    return `
      <div class="accordion-item ${uncheckedCls}" id="accordion-${_esc(q.id)}">
        <button class="accordion-header" data-id="${_esc(q.id)}" type="button">
          <div class="accordion-header-left">
            <span class="accordion-q-num">${q.year}-${String(q.number).padStart(3,'0')}</span>
            ${subBadge}
            ${yearBadge}
            ${checked}
          </div>
          <span class="accordion-question">${_esc(_previewText(q.questionText))}</span>
          <svg class="accordion-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <div class="accordion-body">
          <p style="font-size:.9rem;line-height:1.7;margin-bottom:12px;">${Format.render(q.questionText)}</p>
          ${images}
          <ul class="list-options">${optionsHtml}</ul>
          ${explanation}
          ${conceptLinks}
          <div class="list-actions">
            <button class="btn btn-sm btn-outline btn-check-toggle" data-id="${_esc(q.id)}">
              ${q.checked ? '取消確認' : '標記已確認'}
            </button>
            <button class="btn btn-sm btn-outline btn-goto-card" data-id="${_esc(q.id)}">前往卡片</button>
            ${Editor.isEditMode() ? `<button class="btn btn-sm btn-primary btn-list-edit" data-id="${_esc(q.id)}">✏️ 編輯</button>` : ''}
          </div>
          <div class="list-edit-form" id="list-edit-form-${_esc(q.id)}" hidden></div>
        </div>
      </div>
    `;
  }

  /* ── 切換已確認狀態 ── */
  function _toggleChecked(id, btn) {
    const q = QuestionStore.getQuestionById(id);
    if (!q) return;
    const newVal = !q.checked;
    DataLoader.saveQuestionEdit(id, { checked: newVal });
    q.checked = newVal;
    Editor.updatePendingBadge();
    showToast(newVal ? '已標記為已確認' : '已取消確認', 'success');

    // 更新 UI
    const item = document.getElementById('accordion-' + id);
    if (item) {
      item.classList.toggle('unchecked', !newVal);
      // 更新按鈕文字
      if (btn) btn.textContent = newVal ? '取消確認' : '標記已確認';
      // 更新 badge
      const badgeArea = item.querySelector('.accordion-header-left');
      if (badgeArea) {
        const old = badgeArea.querySelector('.badge-checked, .badge-unchecked');
        if (old) {
          old.outerHTML = newVal
            ? `<span class="badge badge-checked">已確認</span>`
            : `<span class="badge-unchecked">未確認</span>`;
        }
      }
    }
  }

  function _previewText(text) {
    const plain = Format.toPlainText(text || '');
    return plain.length > 80 ? plain.slice(0, 80) + '...' : plain;
  }

  function _esc(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  return { init, load };
})();
