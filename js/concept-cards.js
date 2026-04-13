/* =====================================================
   concept-cards.js — 概念卡片管理
   - 概念列表頁（#/concepts）
   - 單一概念頁（#/concept/{id}）
   - 反向連結（顯示相關題目）
   - 編輯模式：新增/編輯概念
   ===================================================== */

const ConceptCards = (function () {
  'use strict';

  /* ── 渲染概念列表頁 ── */
  async function renderAll() {
    const container = document.getElementById('concept-container');
    if (!container) return;

    const concepts = await DataLoader.loadConcepts();
    const keys = Object.keys(concepts).sort();

    // 也收集題目中引用但 concepts.json 中不存在的概念 ID
    const allQuestions = DataLoader.getLoadedQuestions();
    const referenced = new Set();
    for (const q of allQuestions) {
      for (const c of (q.concepts || [])) referenced.add(c);
    }
    const missing = [...referenced].filter(c => !concepts[c]).sort();

    let html = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
        <h2 style="margin:0;font-size:1.2rem;">概念列表（${keys.length} 個）</h2>
        ${Editor.isEditMode() ? '<button class="btn btn-primary btn-sm" id="concept-add-btn">＋ 新增概念</button>' : ''}
      </div>
    `;

    if (missing.length > 0) {
      html += `<div style="margin-bottom:16px;padding:12px;background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;">
        <strong style="color:#c2410c;">待建立的概念（題目中引用但尚未建立）：</strong>
        <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:6px;">
          ${missing.map(c => `<a href="#/concept/${_esc(c)}" class="concept-link">${_esc(c)}</a>`).join('')}
        </div>
      </div>`;
    }

    if (keys.length === 0 && missing.length === 0) {
      html += '<div style="text-align:center;padding:60px;color:var(--text-muted);">目前無概念卡片。在題目編輯中新增概念連結後，可在此管理。</div>';
    }

    html += '<div class="concept-grid">';
    for (const id of keys) {
      const c = concepts[id];
      const name = c.name || id;
      const nameZh = c.nameZh || '';
      const sub = c.subspecialty || '';
      const checked = c.checked ? '<span class="badge badge-checked">已確認</span>' : '<span class="badge-unchecked">未確認</span>';
      const relCount = allQuestions.filter(q => (q.concepts || []).includes(id)).length;

      html += `
        <a href="#/concept/${_esc(id)}" class="concept-grid-item">
          <div class="concept-grid-title">${_esc(name)}</div>
          ${nameZh ? `<div style="font-size:.8rem;color:var(--text-muted);">${_esc(nameZh)}</div>` : ''}
          <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;">
            ${sub ? `<span class="badge badge-sub" data-sub="${_esc(sub)}">${_esc(sub)}</span>` : ''}
            ${checked}
            <span class="badge badge-year">相關 ${relCount} 題</span>
          </div>
        </a>
      `;
    }
    html += '</div>';

    container.innerHTML = html;

    // 新增概念按鈕
    const addBtn = container.querySelector('#concept-add-btn');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        const id = prompt('輸入概念 ID（英文、用橫線分隔，如 upj-obstruction）：');
        if (!id) return;
        const normalized = Format.normalizeId(id);
        window.location.hash = '#/concept/' + normalized;
      });
    }
  }

  /* ── 渲染單一概念頁 ── */
  async function renderConcept(id) {
    const container = document.getElementById('concept-container');
    if (!container) return;

    const concepts = await DataLoader.loadConcepts();
    const concept = concepts[id];

    // 反向連結：找所有引用此概念的題目
    const allQuestions = DataLoader.getLoadedQuestions();
    const related = allQuestions.filter(q => (q.concepts || []).includes(id));

    if (!concept) {
      // 概念不存在，提供建立選項
      let html = `
        <div style="padding:40px;text-align:center;">
          <h2 style="margin-bottom:8px;">${_esc(id)}</h2>
          <p style="color:var(--text-muted);margin-bottom:16px;">此概念尚未建立</p>
      `;
      if (related.length > 0) {
        html += `<p style="margin-bottom:16px;">有 ${related.length} 題引用此概念</p>`;
      }
      if (Editor.isEditMode()) {
        html += `<button class="btn btn-primary" id="concept-create-btn">建立此概念</button>`;
      }
      html += `<div style="margin-top:12px;"><button class="btn btn-outline" onclick="history.back()">返回</button>
        <a href="#/concepts" class="btn btn-outline" style="margin-left:8px;">概念列表</a></div></div>`;
      container.innerHTML = html;

      const createBtn = container.querySelector('#concept-create-btn');
      if (createBtn) {
        createBtn.addEventListener('click', function () {
          // 建立空概念
          const newConcept = {
            name: id,
            nameZh: '',
            subspecialty: '',
            definition: '',
            imagingFindings: '',
            differentialDiagnosis: [],
            externalLinks: [],
            checked: false,
          };
          DataLoader.saveConceptEdit(id, newConcept);
          concepts[id] = newConcept;
          renderConcept(id); // 重新渲染
          showToast('概念已建立', 'success');
        });
      }
      return;
    }

    // 正常渲染
    const checked = concept.checked ? '<span class="badge badge-checked">已確認</span>' : '<span class="badge-unchecked">未確認</span>';
    const subBadge = concept.subspecialty ? `<span class="badge badge-sub" data-sub="${_esc(concept.subspecialty)}">${_esc(concept.subspecialty)}</span>` : '';

    let html = `
      <div style="margin-bottom:12px;"><a href="#/concepts" style="color:var(--primary);font-size:.85rem;">← 概念列表</a></div>
      <div class="concept-card">
        <div class="concept-header">
          <h2 class="concept-title">${_esc(concept.name || id)}</h2>
          ${concept.nameZh ? `<div style="font-size:.95rem;color:var(--text-muted);margin-top:2px;">${_esc(concept.nameZh)}</div>` : ''}
          <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">${subBadge}${checked}</div>
        </div>
    `;

    if (concept.definition) {
      html += `<div class="concept-section"><h3>定義</h3><div>${Format.render(concept.definition)}</div></div>`;
    }
    if (concept.imagingFindings) {
      html += `<div class="concept-section"><h3>影像特徵</h3><div>${Format.render(concept.imagingFindings)}</div></div>`;
    }
    if (concept.differentialDiagnosis && concept.differentialDiagnosis.length > 0) {
      html += `<div class="concept-section"><h3>鑑別診斷</h3><ul>${concept.differentialDiagnosis.map(d => `<li>${_esc(d)}</li>`).join('')}</ul></div>`;
    }
    if (concept.externalLinks && concept.externalLinks.length > 0) {
      html += `<div class="concept-section"><h3>外部連結</h3><ul>${concept.externalLinks.map(l =>
        `<li><a href="${_esc(l.url)}" target="_blank" rel="noopener">${_esc(l.label || l.url)}</a></li>`
      ).join('')}</ul></div>`;
    }

    // 反向連結
    if (related.length > 0) {
      html += `<div class="concept-section"><h3>相關題目（${related.length}）</h3><ul>`;
      for (const q of related) {
        const idx = allQuestions.indexOf(q);
        html += `<li><a href="#/card?q=${idx}" class="concept-link">${_esc(q.id)}</a> — ${_esc((q.questionText || '').substring(0, 60))}…</li>`;
      }
      html += '</ul></div>';
    }

    // 編輯按鈕
    if (Editor.isEditMode()) {
      html += `<div style="margin-top:16px;"><button class="btn btn-primary" id="concept-edit-toggle">✏️ 編輯此概念</button></div>`;
      html += `<div id="concept-edit-area" hidden style="margin-top:16px;"></div>`;
    }

    html += '</div>';
    container.innerHTML = html;

    // 編輯事件
    const editToggle = container.querySelector('#concept-edit-toggle');
    if (editToggle) {
      editToggle.addEventListener('click', function () {
        const area = container.querySelector('#concept-edit-area');
        if (!area) return;
        area.hidden = !area.hidden;
        if (!area.hidden) {
          _renderConceptEditForm(area, id, concept);
        }
      });
    }
  }

  /* ── 概念編輯表單 ── */
  function _renderConceptEditForm(container, id, concept) {
    const subs = ['ABD','CV','CH','NR','MSK','H&N','PED','IR','Physics','Breast','US',''];
    const subOpts = subs.map(s =>
      `<option value="${s}" ${concept.subspecialty === s ? 'selected' : ''}>${s || '（無）'}</option>`
    ).join('');

    const ddList = (concept.differentialDiagnosis || []).join('\n');
    const linksList = (concept.externalLinks || []).map(l => `${l.label || ''}|${l.url || ''}`).join('\n');

    container.innerHTML = `
      <div class="edit-form-group">
        <label class="edit-form-label">名稱（英文）</label>
        <input type="text" class="text-input" id="cedit-name" value="${_esc(concept.name || id)}" />
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">名稱（中文）</label>
        <input type="text" class="text-input" id="cedit-nameZh" value="${_esc(concept.nameZh || '')}" />
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">次專科</label>
        <select class="select-input" id="cedit-sub">${subOpts}</select>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">定義</label>
        ${Format.toolbar('cedit-definition')}
        <textarea class="edit-textarea" id="cedit-definition" rows="5">${_esc(concept.definition || '')}</textarea>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">影像特徵</label>
        ${Format.toolbar('cedit-imaging')}
        <textarea class="edit-textarea" id="cedit-imaging" rows="5">${_esc(concept.imagingFindings || '')}</textarea>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">鑑別診斷（每行一個）</label>
        <textarea class="edit-textarea" id="cedit-dd" rows="3">${_esc(ddList)}</textarea>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">外部連結（每行：名稱|URL）</label>
        <textarea class="edit-textarea" id="cedit-links" rows="3" placeholder="Radiopaedia|https://radiopaedia.org/...">${_esc(linksList)}</textarea>
      </div>
      <div class="edit-form-group">
        <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
          <input type="checkbox" id="cedit-checked" ${concept.checked ? 'checked' : ''} />
          <span class="edit-form-label" style="margin:0;">已確認</span>
        </label>
      </div>
      <div class="edit-actions">
        <button class="btn btn-primary" id="cedit-save">儲存</button>
        <button class="btn btn-outline" id="cedit-cancel">取消</button>
      </div>
    `;

    Format.bindToolbar(container);

    container.querySelector('#cedit-save').addEventListener('click', function () {
      const patch = {
        name: document.getElementById('cedit-name').value,
        nameZh: document.getElementById('cedit-nameZh').value,
        subspecialty: document.getElementById('cedit-sub').value,
        definition: document.getElementById('cedit-definition').value,
        imagingFindings: document.getElementById('cedit-imaging').value,
        differentialDiagnosis: document.getElementById('cedit-dd').value.split('\n').map(s => s.trim()).filter(Boolean),
        externalLinks: document.getElementById('cedit-links').value.split('\n').map(line => {
          const parts = line.split('|');
          return parts.length >= 2 ? { label: parts[0].trim(), url: parts.slice(1).join('|').trim() } : null;
        }).filter(Boolean),
        checked: document.getElementById('cedit-checked').checked,
      };
      DataLoader.saveConceptEdit(id, patch);
      Object.assign(concept, patch);
      showToast('概念已儲存', 'success');
      Editor.updatePendingBadge();
      renderConcept(id);
    });

    container.querySelector('#cedit-cancel').addEventListener('click', function () {
      container.hidden = true;
      container.innerHTML = '';
    });
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
