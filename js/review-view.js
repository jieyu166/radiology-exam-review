/* =====================================================
   review-view.js — 今日複習（#/review）
   佇列計算為純函式（可測）；mount() 負責 DOM：題目卡 → 揭曉 → 四鍵評分 → 下一題。
   評分即：setCard、appendReviewLog、recordAnswer(source 'review') 三者入 outbox。
   ===================================================== */

const ReviewView = (function () {
  'use strict';

  const RATINGS = ['again', 'hard', 'good', 'easy'];
  const LABELS = { again: '重來', hard: '困難', good: '良好', easy: '簡單' };

  function _esc(value) {
    return String(value == null ? '' : value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function _sched() {
    return (typeof window !== 'undefined' && window.RexScheduler) || null;
  }

  /** Pure: compute today's queue from published entries + progress. */
  function buildQueue(input) {
    const S = _sched();
    const now = input.now;
    const settings = input.settings || {};
    const window_ = S.dueWindow.dayWindow(now, { dayStartHour: settings.dayStartHour });
    const cards = input.progress.cards || {};
    const entries = (input.entries || []).filter(e => e.scorable !== false);
    const entryIds = new Set(entries.map(e => e.id));
    const learning = [];
    const due = [];
    for (const id of Object.keys(cards)) {
      const card = cards[id];
      if (!entryIds.has(id)) continue;
      if ((card.state === 1 || card.state === 3) && card.dueAt <= now) learning.push(card);
      else if (card.state === 2 && card.dueAt <= window_.dayEnd) due.push(card);
    }
    learning.sort((a, b) => a.dueAt - b.dueAt);
    due.sort((a, b) => a.dueAt - b.dueAt);
    const fresh = entries.filter(e => !cards[e.id]).map(e => e.id).sort();
    const introduced = S.queueMix.introducedToday(input.progress.reviewLogs || [], window_);
    const newPerDay = S.queueMix.parseNewLimit(settings.newPerDay);
    const newRemaining = S.queueMix.remainingNewToday(introduced, newPerDay);
    return {
      window: window_,
      served: 0,
      learning: learning.map(c => c.questionId),
      due: due.map(c => c.questionId),
      fresh,
      newRemaining,
      newPerDay,
      introducedToday: introduced,
      tomorrowDue: Object.keys(cards).filter(id => entryIds.has(id) && cards[id].state === 2 && cards[id].dueAt > window_.dayEnd && cards[id].dueAt <= window_.dayEnd + S.dueWindow.DAY_MS).length,
    };
  }

  function counts(queue) {
    return { learning: queue.learning.length, due: queue.due.length, newAvailable: queue.fresh.length, newRemaining: queue.newRemaining, introducedToday: queue.introducedToday };
  }

  /** Pure: pop the next question id according to queue-mix rules; null when nothing is left. */
  function takeNext(queue) {
    const S = _sched();
    const kind = S.queueMix.pickNextKind({ served: queue.served, learning: queue.learning.length, dueReview: queue.due.length, newAvailable: queue.fresh.length, newRemaining: queue.newRemaining });
    if (!kind) return null;
    let id = null;
    if (kind === 'learning') id = queue.learning.shift();
    else if (kind === 'due') id = queue.due.shift();
    else { id = queue.fresh.shift(); queue.newRemaining--; }
    queue.served++;
    return { kind, questionId: id };
  }

  /** Re-check a learning card that became due while the user was answering other cards. */
  function refreshLearning(queue, progress, now) {
    const cards = progress.cards || {};
    for (const id of Object.keys(cards)) {
      const c = cards[id];
      if ((c.state === 1 || c.state === 3) && c.dueAt <= now && !queue.learning.includes(id)) queue.learning.push(id);
    }
    queue.learning.sort((a, b) => cards[a].dueAt - cards[b].dueAt);
  }

  /** Apply a rating: card + review log + review attempt, all through DataLoader (outbox-backed). */
  function rate(store, questionId, rating, now, answerResult) {
    const S = _sched();
    const card = store.getCard(questionId);
    const outcome = S.fsrs.rate(card, questionId, now, rating);
    if (!outcome) return null;
    store.setCard(outcome.cardRow);
    const log = store.appendReviewLog(outcome.log);
    if (answerResult && answerResult.scorable !== false) {
      store.recordAnswer(questionId, Object.assign({}, answerResult, { source: 'review', clientTs: now }));
    }
    return { card: outcome.cardRow, log };
  }

  function defaultRating(answerResult) {
    return answerResult && answerResult.correct === true ? 'good' : 'again';
  }

  function ratingBar(card, now, focus) {
    const S = _sched();
    const pv = S.fsrs.preview(card, now);
    return `<div class="vault-rating-bar" role="group" aria-label="評分">${RATINGS.map((r, i) => {
      const label = pv ? S.fsrs.intervalLabel(pv[r].dueAt, now) : '';
      return `<button type="button" class="vault-rating-btn rating-${r}${focus === r ? ' is-default' : ''}" data-rating="${r}" title="按 ${i + 1}"><span class="rating-key">${i + 1}</span>${LABELS[r]}<small>${_esc(label)}</small></button>`;
    }).join('')}</div>`;
  }

  function countsHtml(queue, availableInFilter) {
    const c = counts(queue);
    return `<div class="vault-review-counts"><span>學習中 <strong>${c.learning}</strong></span><span>到期 <strong>${c.due}</strong></span><span>新卡 <strong>${c.newAvailable}</strong></span><span class="muted">今日新卡剩餘 ${c.newRemaining}／${queue.newPerDay}，篩選內可用 ${availableInFilter}</span></div>`;
  }

  /** DOM: mount the review flow into `section` using the app's dependencies. */
  async function mount(section, deps) {
    const S = _sched();
    const store = deps.store;
    const host = section.querySelector('#vault-review-host');
    if (!S || !S.fsrs || !S.fsrs.available()) {
      host.innerHTML = '<div class="vault-empty">排程模組載入失敗（ts-fsrs 未載入），可繼續使用卡片模式。</div>';
      return;
    }
    const progress = store.getProgress();
    const queue = buildQueue({ entries: deps.entries, progress, now: Date.now(), settings: progress.settings });
    const availableInFilter = deps.entries.filter(e => e.scorable !== false).length;
    const countsEl = section.querySelector('#vault-review-counts');
    const keyHandler = { current: null };
    const removeKeys = () => { if (keyHandler.current) { document.removeEventListener('keydown', keyHandler.current); keyHandler.current = null; } };

    async function showNext() {
      removeKeys();
      refreshLearning(queue, store.getProgress(), Date.now());
      countsEl.innerHTML = countsHtml(queue, availableInFilter);
      const next = takeNext(queue);
      if (!next) {
        host.innerHTML = `<div class="vault-review-done"><h3>今日完成</h3><p>明日到期 ${queue.tomorrowDue} 題${queue.fresh.length && queue.newRemaining <= 0 ? '；今日新卡額度已用完，可在設定提高每日新卡上限' : ''}。</p></div>`;
        return;
      }
      host.innerHTML = '<div class="vault-loading">載入題目…</div>';
      let note;
      try { note = await deps.getQuestion(next.questionId); } catch (error) { host.innerHTML = `<div class="vault-error">${_esc(error.message || error)}</div>`; return; }
      if (!note || !section.isConnected) return;
      host.innerHTML = `<div class="vault-review-kind">${{ learning: '學習中', due: '到期複習', new: '新題' }[next.kind]}</div><div class="vault-question-host"></div><div id="vault-rating-slot"></div>`;
      store.markSeen(next.questionId);
      let answerResult = null;
      const bound = deps.questionView.bind(host.querySelector('.vault-question-host'), note, { mode: 'card', onAnswer: result => { answerResult = result; showRating(); } });
      const ratingSlot = host.querySelector('#vault-rating-slot');
      let rated = false;

      function applyRating(rating) {
        if (rated) return;
        rated = true;
        rate(store, next.questionId, rating, Date.now(), answerResult);
        if (typeof deps.afterRate === 'function') deps.afterRate();
        showNext();
      }

      function showRating() {
        const focus = defaultRating(answerResult);
        ratingSlot.innerHTML = ratingBar(store.getCard(next.questionId), Date.now(), focus);
        ratingSlot.querySelectorAll('[data-rating]').forEach(btn => btn.addEventListener('click', () => applyRating(btn.dataset.rating)));
        const focusBtn = ratingSlot.querySelector(`[data-rating="${focus}"]`);
        if (focusBtn) focusBtn.focus();
      }

      keyHandler.current = event => {
        if (!section.isConnected) { removeKeys(); return; }
        if (event.target && /input|textarea|select/i.test(event.target.tagName)) return;
        if (event.key === ' ' && !bound.state.revealed) {
          event.preventDefault();
          bound.state.revealed = true;
          if (!answerResult) answerResult = deps.questionView.buildResult(note, bound.state, { mode: 'card' }, Date.now());
          bound.render();
          showRating();
          return;
        }
        const index = ['1', '2', '3', '4'].indexOf(event.key);
        if (index >= 0 && bound.state.revealed) { event.preventDefault(); applyRating(RATINGS[index]); }
      };
      document.addEventListener('keydown', keyHandler.current);
    }

    await showNext();
  }

  return { RATINGS, LABELS, buildQueue, counts, takeNext, refreshLearning, rate, defaultRating, ratingBar, countsHtml, mount };
})();
