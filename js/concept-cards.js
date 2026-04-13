/* =====================================================
   concept-cards.js — 概念卡片檢視
   ===================================================== */

const ConceptCards = (function () {
  'use strict';

  /* ── 渲染單一概念 ── */
  function renderConcept(id) {
    const container = document.getElementById('concept-container');
    if (!container) return;

    DataLoader.loadConcepts().then(concepts => {
      const concept = concepts[id];
      if (!concept) {
        container.innerHTML = `
          <div style="text-align:center;padding:60px;color:var(--text-muted);">
            <p>找不到概念：${_esc(id)}</p>
            <button class="btn btn-outline" onclick="history.back()">返回</button>
          </div>
        `;
        return;
      }
      container.innerHTML = _buildConceptCard(id, concept);
    }).catch(err => {
      container.innerHTML = `<div style="color:var(--danger);">載入失敗：${_esc(String(err))}</div>`;
    });
  }

  /* ── 渲染全部概念 ── */
  function renderAll() {
    const container = document.getElementById('concept-container');
    if (!container) return;

    DataLoader.loadConcepts().then(concepts => {
      const keys = Object.keys(concepts);
      if (keys.length === 0) {
        container.innerHTML = '<div style="text-align:center;padding:60px;color:var(--text-muted);">目前無概念卡片</div>';
        return;
      }
      container.innerHTML = keys.map(k => _buildConceptCard(k, concepts[k])).join('');
    }).catch(err => {
      container.innerHTML = `<div style="color:var(--danger);">載入失敗：${_esc(String(err))}</div>`;
    });
  }

  /* ── 建構卡片 HTML ── */
  function _buildConceptCard(id, concept) {
    const title = concept.title || id;
    const body  = concept.body  || concept.content || '';
    const tags  = (concept.tags || []).map(t =>
      `<span class="badge badge-year">${_esc(t)}</span>`
    ).join(' ');

    return `
      <div class="concept-card" id="concept-${_esc(id)}">
        <div class="concept-title">${_esc(title)}</div>
        ${tags ? `<div style="margin-bottom:10px;">${tags}</div>` : ''}
        <div class="concept-body">${_esc(body)}</div>
      </div>
    `;
  }

  function _esc(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  return { renderConcept, renderAll };
})();
