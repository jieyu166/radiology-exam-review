/* =====================================================
   format.js - safe Markdown-like rendering and toolbar
   Supports: **bold**, *italic*, [[concept|label]], ![alt](data/images/...)
   ===================================================== */

const Format = (function () {
  'use strict';

  function render(text) {
    if (!text) return '';

    let html = _esc(text);

    html = html.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, function (match, alt, src) {
      const cleanSrc = _safeImageSrc(src);
      if (!cleanSrc) return match;
      return `<img class="inline-image" src="${_escAttr(cleanSrc)}" alt="${_escAttr(alt || '')}" loading="lazy" />`;
    });

    html = html.replace(/\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]/g, function (_, rawId, label) {
      const id = _normalizeConceptId(rawId);
      const display = label || rawId;
      return `<a href="#/concept/${_escAttr(id)}" class="concept-link" title="concept: ${_escAttr(display)}">${display}</a>`;
    });

    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/\n/g, '<br>');

    return html;
  }

  function toPlainText(text) {
    if (!text) return '';
    return String(text)
      .replace(/!\[[^\]]*\]\([^)]+\)/g, '')
      .replace(/\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]/g, function (_, rawId, label) { return label || rawId; })
      .replace(/\*\*(.+?)\*\*/g, '$1')
      .replace(/\*(.+?)\*/g, '$1')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function insertFormat(textarea, before, after) {
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = textarea.value.substring(start, end);
    const fallback = 'text';
    const replacement = before + (selected || fallback) + after;

    textarea.setRangeText(replacement, start, end, 'select');
    textarea.focus();
    textarea.selectionStart = start + before.length;
    textarea.selectionEnd = start + before.length + (selected || fallback).length;
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function toolbar(targetId) {
    return `
      <div class="format-toolbar">
        <button type="button" class="fmt-btn" data-target="${targetId}" data-before="**" data-after="**" title="Bold">
          <strong>B</strong>
        </button>
        <button type="button" class="fmt-btn" data-target="${targetId}" data-before="*" data-after="*" title="Italic">
          <em>I</em>
        </button>
        <button type="button" class="fmt-btn fmt-btn-concept" data-target="${targetId}" title="Insert concept link">
          [[ concept ]]
        </button>
      </div>
    `;
  }

  function bindToolbar(container) {
    if (!container) return;

    container.querySelectorAll('.fmt-btn').forEach(btn => {
      if (btn.classList.contains('fmt-btn-concept')) {
        btn.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          const textarea = document.getElementById(this.dataset.target);
          if (!textarea) return;

          const conceptId = prompt('Concept ID, e.g. upj-obstruction');
          if (!conceptId) return;
          const label = prompt('Display label (optional)', conceptId);
          const tag = label && label !== conceptId
            ? `[[${conceptId}|${label}]]`
            : `[[${conceptId}]]`;
          insertFormat(textarea, tag, '');
        });
      } else {
        btn.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          const textarea = document.getElementById(this.dataset.target);
          if (!textarea) return;
          insertFormat(textarea, this.dataset.before, this.dataset.after);
        });
      }
    });
  }

  function _normalizeConceptId(raw) {
    return String(raw || '').trim().toLowerCase().replace(/\s+/g, '-');
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

  function _safeImageSrc(src) {
    const value = String(src || '').trim().replace(/\\/g, '/');
    if (!value) return '';
    if (/^(?:https?:|data:|javascript:)/i.test(value)) return '';
    if (value.includes('"') || value.includes("'") || value.includes('<') || value.includes('>')) return '';
    if (value.startsWith('data/images/')) return value;
    return '';
  }

  return {
    render,
    toPlainText,
    insertFormat,
    toolbar,
    bindToolbar,
    normalizeId: _normalizeConceptId,
  };
})();
