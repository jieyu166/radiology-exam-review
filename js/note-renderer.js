/* =====================================================
   note-renderer.js — generic Obsidian Markdown presentation
   ===================================================== */

const NoteRenderer = (function () {
  'use strict';

  function _esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function _publicationBase(options) {
    const configured = options && options.assetBase;
    const value = typeof configured === 'string' ? configured
      : typeof ContentStore !== 'undefined' && typeof ContentStore.getPublicationBase === 'function' ? ContentStore.getPublicationBase()
      : (typeof window !== 'undefined' && window.REX_PUBLICATION_BASE) || 'dist/';
    const base = String(value).replace(/\\/g, '/').replace(/^\/*/, '').replace(/\/*$/, '');
    return base ? base + '/' : '';
  }

  function _safeHref(value) {
    const href = String(value || '').trim();
    if (/^https?:\/\//i.test(href) || href.startsWith('#/')) return href;
    if (/^[A-Za-z0-9._/-]+$/.test(href) && !href.includes('..')) return href;
    return '';
  }

  function _safeAsset(value, options) {
    const asset = String(value || '').trim();
    if (/^https?:\/\//i.test(asset)) return _safeHref(asset);
    if (!asset || asset.startsWith('/') || asset.includes('..') || asset.includes('\\')) return '';
    return _publicationBase(options) + asset;
  }

  function _embedMap(record) {
    const map = {};
    for (const embed of (record && record.embeds) || []) {
      if (embed && embed.target && embed.resolvedPath) map[embed.target] = embed.resolvedPath;
    }
    return map;
  }

  function _inline(raw, options, embeds, footnotes) {
    let text = _esc(raw);
    const placeholders = [];
    const hold = html => {
      const key = `\u0000${placeholders.length}\u0000`;
      placeholders.push(html);
      return key;
    };

    text = text.replace(/!\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]/g, (_, target, label) => {
      const path = embeds[target.trim()];
      if (!path) return `<span class="note-unresolved-embed">${_esc(label || target)}</span>`;
      const src = _safeAsset(path, options);
      if (!src) return `<span class="note-unresolved-embed">${_esc(label || target)}</span>`;
      return hold(`<img class="note-image" src="${_esc(src)}" alt="${_esc(label || target)}" loading="lazy" />`);
    });
    text = text.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, (_, alt, src) => {
      const safe = _safeAsset(src, options);
      return safe ? hold(`<img class="note-image" src="${_esc(safe)}" alt="${_esc(alt)}" loading="lazy" />`) : _esc(alt);
    });
    text = text.replace(/\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]/g, (_, target, label) => {
      const id = String(target || '').trim().toLowerCase().replace(/\s+/g, '-');
      const display = label || target;
      return `<a class="note-wikilink" href="#/concept/${_esc(id)}">${_esc(display)}</a>`;
    });
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
      const safe = _safeHref(href);
      return safe ? `<a href="${_esc(safe)}" rel="noreferrer">${_esc(label)}</a>` : _esc(label);
    });
    text = text.replace(/\[\^([^\]]+)\]/g, (_, id) => {
      const key = String(id).trim();
      return hold(`<sup class="note-footnote-ref" id="note-ref-${_esc(key)}">[${_esc(key)}]</sup>`);
    });
    text = text.replace(/\$\$([^$]+)\$\$/g, (_, value) => hold(`<code class="note-math note-math-block">${_esc(value)}</code>`));
    text = text.replace(/\$([^$]+)\$/g, (_, value) => hold(`<code class="note-math">${_esc(value)}</code>`));
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
    for (let i = 0; i < placeholders.length; i++) text = text.replace(`\u0000${i}\u0000`, placeholders[i]);
    return text;
  }

  function _isTable(lines, index) {
    return lines[index] && lines[index].trim().startsWith('|') && lines[index + 1] && /^\s*\|?\s*:?-{2,}/.test(lines[index + 1]);
  }

  function _table(lines, index, options, embeds, footnotes) {
    const rows = [];
    let cursor = index;
    while (cursor < lines.length && lines[cursor].trim().startsWith('|')) {
      const cells = lines[cursor].trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(cell => cell.trim());
      if (!/^\s*:?-{2,}/.test(cells[0] || '') || cursor === index) rows.push(cells);
      cursor++;
    }
    if (rows.length === 0) return { html: '', next: index + 1 };
    const head = rows[0].map(cell => `<th>${_inline(cell, options, embeds, footnotes)}</th>`).join('');
    const body = rows.slice(1).map(row => `<tr>${row.map(cell => `<td>${_inline(cell, options, embeds, footnotes)}</td>`).join('')}</tr>`).join('');
    return { html: `<table class="note-table"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`, next: cursor };
  }

  function _stripFrontmatter(raw) {
    const lines = String(raw || '').split(/\r?\n/);
    if (lines[0] && lines[0].trim() === '---') {
      const end = lines.findIndex((line, index) => index > 0 && line.trim() === '---');
      if (end >= 0) return lines.slice(end + 1);
    }
    return lines;
  }

  function _hideObsidianQueries(source) {
    const lines = source.slice();
    const emptyHeadings = new Set();
    for (let index = 0; index < lines.length; index++) {
      const opening = /^ {0,3}(`{3,}|~{3,})(.*)$/.exec(lines[index]);
      if (!opening) continue;
      const closing = new RegExp('^ {0,3}' + opening[1][0] + '{' + opening[1].length + ',}\\s*$');
      let end = index + 1;
      while (end < lines.length && !closing.test(lines[end])) end++;
      // An incomplete fence can contain real prose; retain the fallback display.
      if (end === lines.length) break;
      if (/^dataview(?:js)?$/i.test(opening[2].trim())) {
        let previous = index - 1;
        while (previous >= 0 && !lines[previous].trim()) previous--;
        if (previous >= 0 && /^ {0,3}#{1,6}\s+(?:考題|相關考題|相關題目)\s*#*\s*$/.test(lines[previous])) {
          emptyHeadings.add(previous);
        }
        for (let row = index; row <= end; row++) lines[row] = '';
      }
      index = end;
    }
    for (const index of emptyHeadings) {
      let next = index + 1;
      while (next < lines.length && !lines[next].trim()) next++;
      const current = /^\s*(#+)/.exec(lines[index]);
      const heading = next < lines.length && /^ {0,3}(#{1,6})\s+/.exec(lines[next]);
      if (next === lines.length || (heading && heading[1].length <= current[1].length)) lines[index] = '';
    }
    return lines;
  }

  function renderDocument(raw, options) {
    const config = options || {};
    const lines = _hideObsidianQueries(_stripFrontmatter(raw));
    const record = config.record || {};
    const embeds = _embedMap(record);
    const warnings = [];
    const footnotes = {};
    const html = [];
    let index = 0;
    while (index < lines.length) {
      const line = lines[index];
      const stripped = line.trim();
      if (!stripped) { index++; continue; }

      const heading = /^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$/.exec(line);
      if (heading) {
        html.push(`<h${heading[1].length}>${_inline(heading[2], config, embeds, footnotes)}</h${heading[1].length}>`);
        index++; continue;
      }

      const callout = /^\s*>\s*\[!([^\]]+)\]([+-]?)\s*(.*)$/.exec(line);
      if (/^\s*>/.test(line)) {
        const body = [];
        let cursor = callout ? index + 1 : index;
        while (cursor < lines.length && /^\s*>/.test(lines[cursor])) {
          body.push(lines[cursor].replace(/^\s*>\s?/, ''));
          cursor++;
        }
        const nested = renderDocument(body.join('\n'), Object.assign({}, config, { _nested: true }));
        warnings.push(...nested.warnings.map(warning => Object.assign({}, warning, { line: warning.line + index + (callout ? 1 : 0) })));
        if (!callout) {
          html.push(`<blockquote class="note-quote">${nested.html}</blockquote>`);
        } else {
          const title = _inline(callout[3] || callout[1], config, embeds, footnotes);
          const attributes = `class="note-callout" data-callout="${_esc(callout[1].toLowerCase())}"`;
          html.push(callout[2]
            ? `<details ${attributes}${callout[2] === '+' ? ' open' : ''}><summary>${title}</summary><div>${nested.html}</div></details>`
            : `<aside ${attributes}><strong>${title}</strong><div>${nested.html}</div></aside>`);
        }
        index = cursor; continue;
      }

      if (/^\s*```/.test(line)) {
        const start = index;
        let cursor = index + 1;
        while (cursor < lines.length && !/^\s*```/.test(lines[cursor])) cursor++;
        if (cursor < lines.length) cursor++;
        const block = lines.slice(start, cursor).join('\n');
        warnings.push({ code: 'degraded_fenced_code', line: start + 1, message: 'fenced code is shown as a non-content degraded block' });
        html.push(`<div class="note-degraded" data-warning="non-content"><pre>${_esc(block)}</pre><small>渲染提示：此區塊以原文顯示</small></div>`);
        index = cursor; continue;
      }

      if (_isTable(lines, index)) {
        const table = _table(lines, index, config, embeds, footnotes);
        html.push(table.html); index = table.next; continue;
      }

      const unordered = /^\s*[-*+]\s+(.+)$/.exec(line);
      const ordered = /^\s*\d+[.)]\s+(.+)$/.exec(line);
      if (unordered || ordered) {
        const tag = unordered ? 'ul' : 'ol';
        const items = [];
        let cursor = index;
        while (cursor < lines.length) {
          const match = (unordered ? /^\s*[-*+]\s+(.+)$/ : /^\s*\d+[.)]\s+(.+)$/).exec(lines[cursor]);
          if (!match) break;
          items.push(`<li>${_inline(match[1], config, embeds, footnotes)}</li>`); cursor++;
        }
        html.push(`<${tag} class="note-list">${items.join('')}</${tag}>`); index = cursor; continue;
      }

      const footnote = /^\s*\[\^([^\]]+)\]:\s*(.*)$/.exec(line);
      if (footnote) {
        footnotes[footnote[1]] = footnote[2];
        html.push(`<div class="note-footnote" id="note-footnote-${_esc(footnote[1])}"><sup>[${_esc(footnote[1])}]</sup> ${_inline(footnote[2], config, embeds, footnotes)}</div>`);
        index++; continue;
      }

      if (/^\s*==.+==\s*$/.test(line) || /<\/?(?:iframe|script|style|span)\b/i.test(line)) {
        warnings.push({ code: 'degraded_unknown_safe_block', line: index + 1, message: 'unknown source block is shown as a non-content degraded block' });
        html.push(`<div class="note-degraded" data-warning="non-content"><pre>${_esc(line)}</pre><small>渲染提示：未知 Markdown 區塊以原文顯示</small></div>`);
        index++; continue;
      }

      const paragraph = [line];
      let cursor = index + 1;
      while (cursor < lines.length && lines[cursor].trim() && !/^\s{0,3}#{1,6}\s+/.test(lines[cursor]) && !/^\s*(?:[-*+]\s+|\d+[.)]\s+|>|```)/.test(lines[cursor]) && !_isTable(lines, cursor)) {
        paragraph.push(lines[cursor]); cursor++;
      }
      html.push(`<p>${_inline(paragraph.join('\n'), config, embeds, footnotes).replace(/\n/g, '<br />')}</p>`);
      index = cursor;
    }
    const warningHtml = warnings.length && !config._nested ? `<div class="note-render-warnings" aria-live="polite">渲染提示：${warnings.length} 個非內容區塊以原文顯示</div>` : '';
    if (!config._nested && typeof config.onWarning === 'function') warnings.forEach(config.onWarning);
    return { html: warningHtml + html.join('\n'), warnings };
  }

  function render(raw, options) {
    return renderDocument(raw, options).html;
  }

  function renderTo(container, raw, options) {
    if (!container) return { html: '', warnings: [] };
    const result = renderDocument(raw, options);
    container.innerHTML = result.html;
    return result;
  }

  return { render, renderDocument, renderTo };
})();
