/* =====================================================
   analytics-view.js — 統計（#/stats）：信心校準、hypercorrection、弱點分群與交錯練習
   計算全部交給 RexScheduler 純函式；本模組只組 view model 與 HTML。
   ===================================================== */

const AnalyticsView = (function () {
  'use strict';

  function _esc(value) {
    return String(value == null ? '' : value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function _S() {
    return (typeof window !== 'undefined' && window.RexScheduler) || null;
  }

  /** Pure view model. entries: question index entries; conceptNames: {id: name}; progress: DataLoader progress. */
  function buildModel(input) {
    const S = _S();
    const entriesById = new Map((input.entries || []).map(e => [e.id, e]));
    const attempts = (input.progress && input.progress.attempts) || [];
    const buckets = S.calibration.calibration(attempts);
    const hyper = S.calibration.hypercorrectionCandidates(attempts, 20).map(a => {
      const e = entriesById.get(a.questionId) || {};
      const subs = Array.isArray(e.subspecialty) ? e.subspecialty : (e.subspecialty ? [e.subspecialty] : []);
      return { questionId: a.questionId, years: e.years || [], subspecialty: subs.join('/'), clientTs: a.clientTs, chosen: a.chosen };
    });
    const wrongIds = S.wrongCriterion.wrongIds(input.progress || {});
    const wrongEntries = wrongIds.map(id => entriesById.get(id)).filter(Boolean);
    const groups = S.weakness.groupByTopic(S.weakness.rowsFromEntries(wrongEntries, input.conceptNames || {}), wrongIds, { min: 2, limit: 12 });
    return { buckets, hyper, wrongCount: wrongIds.length, groups, totalWithConfidence: buckets.reduce((s, b) => s + b.n, 0) };
  }

  /** Build an interleaved drill from a weakness group (n 10, seed from today's dayKey). */
  function drillForGroup(group, entriesById, now, settings) {
    const S = _S();
    const window_ = S.dueWindow.dayWindow(now, { dayStartHour: settings && settings.dayStartHour });
    const hits = group.questionIds.map(id => { const e = entriesById.get(id); return { id, year: e && e.years ? e.years[0] : 0 }; });
    return S.drill.pickInterleaved(hits, { anchor: group.anchor, n: 10, seed: S.drill.hashSeed(window_.dayKey + ':' + group.slug) });
  }

  function _pct(value) {
    return value == null ? '—' : `${Math.round(value * 100)}%`;
  }

  function render(model) {
    const calibrationRows = model.buckets.map(b => `<tr><td>${_esc(b.label)}</td><td>${b.n}</td><td>${b.correct}</td><td>${_pct(b.accuracy)}</td></tr>`).join('');
    const hyperRows = model.hyper.length
      ? model.hyper.map(h => `<li><a href="#/card?qid=${encodeURIComponent(h.questionId)}">${_esc(h.questionId)}</a> <span class="muted">${_esc(h.years.join('/'))} ${_esc(h.subspecialty)}｜選了 ${_esc(h.chosen || '—')}</span></li>`).join('')
      : '<li class="muted">目前沒有「有把握卻答錯」的紀錄。</li>';
    const groupCards = model.groups.length
      ? model.groups.map((g, i) => `<div class="vault-weak-group"><div><strong>${_esc(g.label)}</strong> <span class="muted">${g.size} 題，最近答錯 ${_esc(g.anchor)}</span></div><button type="button" class="btn btn-outline btn-sm" data-drill-group="${i}">練這一群</button></div>`).join('')
      : `<p class="muted">${model.wrongCount ? '最近答錯的題目尚未形成 2 題以上的群組。' : '目前沒有最近答錯的題目。'}</p>`;
    return `
      <section class="vault-stats-block">
        <h3>答前信心校準</h3>
        <p class="muted">只統計在卡片模式／今日複習中按過信心鍵的作答（共 ${model.totalWithConfidence} 筆）。</p>
        <table class="note-table vault-calibration"><thead><tr><th>信心</th><th>作答數</th><th>答對</th><th>正確率</th></tr></thead><tbody>${calibrationRows}</tbody></table>
      </section>
      <section class="vault-stats-block">
        <h3>有把握卻答錯（最近 20 題）</h3>
        <ul class="vault-hyper-list">${hyperRows}</ul>
      </section>
      <section class="vault-stats-block">
        <h3>弱點分群 <span class="muted">（最近答錯 ${model.wrongCount} 題，依次專科與概念分群）</span></h3>
        <div class="vault-weak-groups">${groupCards}</div>
      </section>`;
  }

  return { buildModel, drillForGroup, render };
})();
