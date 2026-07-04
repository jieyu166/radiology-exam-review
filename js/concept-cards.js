/* =====================================================
   concept-cards.js — 概念卡片管理
   - 概念列表頁（#/concepts）
   - 單一概念頁（#/concept/{id}）
   - 反向連結（顯示相關題目）
   - 編輯模式：新增/編輯概念
   ===================================================== */

const ConceptCards = (function () {
  'use strict';

  const CANONICAL_SUBSPECIALTIES = ['ABD','CV','CH','NR','MSK','H&N','PED','IR','Physics','Breast','US'];
  const CONCEPT_ONLY_SUBSPECIALTIES = ['GU','GI','PE','Neuro','HN','RP','MRI','GYN'];
  const UNCATEGORIZED_SUBSPECIALTY = '未分類';
  let _conceptSubFilter = '';

  /* ── 渲染概念列表頁 ── */
  async function renderAll() {
    const container = document.getElementById('concept-container');
    if (!container) return;

    const concepts = await DataLoader.loadConceptsIndex();
    const keys = Object.keys(concepts).sort();
    const filterItems = _buildSubspecialtyFilters(concepts, keys);

    // 也收集題目中引用但索引中不存在的概念 ID
    const allQuestions = DataLoader.getLoadedQuestions();
    const relCounts = _buildRelatedCounts(allQuestions);
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
      ${_renderFilterPills(filterItems, keys.length)}
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

    html += _renderConceptGrid(concepts, keys, relCounts);

    container.innerHTML = html;
    _bindFilterPills(container, concepts, keys, relCounts);

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

  function _buildSubspecialtyFilters(concepts, keys) {
    const counts = new Map();
    for (const id of keys) {
      const sub = (concepts[id].subspecialty || '').trim() || UNCATEGORIZED_SUBSPECIALTY;
      counts.set(sub, (counts.get(sub) || 0) + 1);
    }

    const canonical = CANONICAL_SUBSPECIALTIES
      .filter(sub => counts.has(sub))
      .map(sub => ({ value: sub, label: sub, count: counts.get(sub) }));
    const extraSubs = Array.from(counts.keys())
      .filter(sub => sub !== UNCATEGORIZED_SUBSPECIALTY && !CANONICAL_SUBSPECIALTIES.includes(sub));
    const knownExtras = CONCEPT_ONLY_SUBSPECIALTIES.filter(sub => counts.has(sub));
    const otherExtras = extraSubs.filter(sub => !CONCEPT_ONLY_SUBSPECIALTIES.includes(sub));
    const extras = knownExtras.concat(otherExtras)
      .map(sub => ({ value: sub, label: sub, count: counts.get(sub) }));
    const uncategorized = counts.has(UNCATEGORIZED_SUBSPECIALTY)
      ? [{ value: UNCATEGORIZED_SUBSPECIALTY, label: UNCATEGORIZED_SUBSPECIALTY, count: counts.get(UNCATEGORIZED_SUBSPECIALTY) }]
      : [];

    return canonical.concat(extras, uncategorized);
  }

  function _renderFilterPills(filterItems, totalCount) {
    const allActive = _conceptSubFilter === '' ? ' active' : '';
    const items = [
      `<button type="button" class="pill${allActive}" data-sub="">全部 <span>${totalCount}</span></button>`,
      ...filterItems.map(item => {
        const active = _conceptSubFilter === item.value ? ' active' : '';
        return `<button type="button" class="pill${active}" data-sub="${_esc(item.value)}">${_esc(item.label)} <span>${item.count}</span></button>`;
      })
    ];
    return `<div class="pills-row" id="concept-sub-pills" style="margin:-4px 0 16px;">${items.join('')}</div>`;
  }

  function _bindFilterPills(container, concepts, keys, relCounts) {
    container.querySelectorAll('#concept-sub-pills .pill').forEach(btn => {
      btn.addEventListener('click', function () {
        _conceptSubFilter = this.dataset.sub || '';
        _syncFilterPills(container);
        const grid = container.querySelector('.concept-grid');
        if (grid) grid.outerHTML = _renderConceptGrid(concepts, keys, relCounts);
      });
    });
  }

  function _syncFilterPills(container) {
    container.querySelectorAll('#concept-sub-pills .pill').forEach(btn => {
      btn.classList.toggle('active', (btn.dataset.sub || '') === _conceptSubFilter);
    });
  }

  function _renderConceptGrid(concepts, keys, relCounts) {
    const visibleKeys = keys.filter(id => _matchesSubspecialtyFilter(concepts[id]));
    let html = '<div class="concept-grid">';
    for (const id of visibleKeys) {
      html += _renderConceptGridItem(id, concepts[id], relCounts.get(id) || 0);
    }
    html += '</div>';
    return html;
  }

  function _matchesSubspecialtyFilter(concept) {
    if (!_conceptSubFilter) return true;
    const sub = (concept.subspecialty || '').trim();
    if (_conceptSubFilter === UNCATEGORIZED_SUBSPECIALTY) return !sub;
    return sub === _conceptSubFilter;
  }

  function _renderConceptGridItem(id, concept, relCount) {
    const name = concept.name || id;
    const nameZh = concept.nameZh || '';
    const sub = concept.subspecialty || '';
    const checked = concept.checked ? '<span class="badge badge-checked">已確認</span>' : '<span class="badge-unchecked">未確認</span>';

    return `
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

  function _buildRelatedCounts(allQuestions) {
    const counts = new Map();
    for (const q of allQuestions) {
      for (const id of (q.concepts || [])) {
        counts.set(id, (counts.get(id) || 0) + 1);
      }
    }
    return counts;
  }

  /* ── 渲染單一概念頁 ── */
  async function renderConcept(id) {
    const container = document.getElementById('concept-container');
    if (!container) return;

    const concept = await DataLoader.loadConcept(id);

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
          renderConcept(id); // 重新渲染（loadConcept 會合併此 localStorage 編輯）
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
    if (concept.keyPoints && concept.keyPoints.length > 0) {
      html += `<div class="concept-section"><h3>重點</h3><ul>${concept.keyPoints.map(p => `<li>${Format.render(p)}</li>`).join('')}</ul></div>`;
    }
    if (concept.management) {
      html += `<div class="concept-section"><h3>處置</h3><div>${Format.render(concept.management)}</div></div>`;
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
        html += `<li><a href="#/card?qid=${encodeURIComponent(q.id)}" class="concept-link">${_esc(q.id)}</a> — ${_esc((q.questionText || '').substring(0, 60))}…</li>`;
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
    const kpList = (concept.keyPoints || []).join('\n');
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
        <label class="edit-form-label">重點（每行一個）</label>
        <textarea class="edit-textarea" id="cedit-kp" rows="4">${_esc(kpList)}</textarea>
      </div>
      <div class="edit-form-group">
        <label class="edit-form-label">處置</label>
        ${Format.toolbar('cedit-mgmt')}
        <textarea class="edit-textarea" id="cedit-mgmt" rows="3">${_esc(concept.management || '')}</textarea>
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
        keyPoints: document.getElementById('cedit-kp').value.split('\n').map(s => s.trim()).filter(Boolean),
        management: document.getElementById('cedit-mgmt').value,
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
