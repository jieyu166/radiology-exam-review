/* =====================================================
   format.js — 文字格式化（Markdown-like → HTML）
   支援：**粗體**、*斜體*、[[concept-id|顯示文字]] 概念連結
   ===================================================== */

const Format = (function () {
  'use strict';

  /**
   * 將帶格式的文字轉換為安全的 HTML
   * @param {string} text - 原始文字
   * @returns {string} HTML 字串
   */
  function render(text) {
    if (!text) return '';

    // 先做 HTML escape
    let html = _esc(text);

    // 概念連結：[[concept-id|顯示文字]] 或 [[concept-id]]
    // 自動正規化：空白→橫線、小寫
    html = html.replace(
      /\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]/g,
      function (_, rawId, label) {
        const id = _normalizeConceptId(rawId);
        const display = label || rawId;
        return `<a href="#/concept/${_escAttr(id)}" class="concept-link" title="概念：${_escAttr(display)}">${display}</a>`;
      }
    );

    // 粗體：**text**
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // 斜體：*text*
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // 換行保留
    html = html.replace(/\n/g, '<br>');

    return html;
  }

  /**
   * 在 textarea 游標位置插入格式標記
   */
  function insertFormat(textarea, before, after) {
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = textarea.value.substring(start, end);
    const replacement = before + (selected || '文字') + after;

    textarea.setRangeText(replacement, start, end, 'select');
    textarea.focus();
    // 選取插入的文字（不含標記）
    textarea.selectionStart = start + before.length;
    textarea.selectionEnd = start + before.length + (selected || '文字').length;

    // 觸發 input 事件
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  }

  /**
   * 建立格式工具列 HTML
   * @param {string} targetId - textarea 的 id
   * @returns {string} toolbar HTML
   */
  function toolbar(targetId) {
    return `
      <div class="format-toolbar">
        <button type="button" class="fmt-btn" data-target="${targetId}" data-before="**" data-after="**" title="粗體">
          <strong>B</strong>
        </button>
        <button type="button" class="fmt-btn" data-target="${targetId}" data-before="*" data-after="*" title="斜體">
          <em>I</em>
        </button>
        <button type="button" class="fmt-btn fmt-btn-concept" data-target="${targetId}" title="插入概念連結">
          🔗 概念
        </button>
      </div>
    `;
  }

  /**
   * 綁定工具列按鈕事件（需在 DOM 更新後呼叫）
   */
  function bindToolbar(container) {
    if (!container) return;

    container.querySelectorAll('.fmt-btn').forEach(btn => {
      if (btn.classList.contains('fmt-btn-concept')) {
        btn.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          const targetId = this.dataset.target;
          const textarea = document.getElementById(targetId);
          if (!textarea) return;

          const conceptId = prompt('輸入概念 ID（例如 upj-obstruction）：');
          if (!conceptId) return;
          const label = prompt('顯示文字（留空則用 ID）：', conceptId);
          const tag = label && label !== conceptId
            ? `[[${conceptId}|${label}]]`
            : `[[${conceptId}]]`;
          insertFormat(textarea, tag, '');
        });
      } else {
        btn.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          const targetId = this.dataset.target;
          const textarea = document.getElementById(targetId);
          if (!textarea) return;
          insertFormat(textarea, this.dataset.before, this.dataset.after);
        });
      }
    });
  }

  /**
   * 正規化概念 ID：空白→橫線、小寫、去頭尾空白
   */
  function _normalizeConceptId(raw) {
    return raw.trim().toLowerCase().replace(/\s+/g, '-');
  }

  function _esc(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function _escAttr(str) {
    return _esc(str).replace(/'/g, '&#39;');
  }

  return { render, insertFormat, toolbar, bindToolbar, normalizeId: _normalizeConceptId };
})();
