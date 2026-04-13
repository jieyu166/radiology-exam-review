/* =====================================================
   exam-mode.js — 模擬考模式
   ===================================================== */

const ExamMode = (function () {
  'use strict';

  /* 考試狀態 */
  let _state = {
    questions: [],
    answers:   {},   // id -> 選的字母
    current:   0,
    submitted: false,
  };

  /* ── 初始化 ── */
  function init() {
    /* 考試設定頁 */
    const startBtn = document.getElementById('exam-start-btn');
    if (startBtn) startBtn.addEventListener('click', _startExam);

    /* 考試進行頁 */
    const prevBtn = document.getElementById('exam-prev-btn');
    const nextBtn = document.getElementById('exam-next-btn');
    const endBtn  = document.getElementById('exam-end-btn');
    const gridTog = document.getElementById('exam-grid-toggle');

    if (prevBtn)  prevBtn.addEventListener('click', () => _navigate(-1));
    if (nextBtn)  nextBtn.addEventListener('click', _handleNext);
    if (endBtn)   endBtn.addEventListener('click',  _confirmEnd);
    if (gridTog)  gridTog.addEventListener('click', _toggleGrid);

    /* 結果頁 */
    const retryBtn = document.getElementById('result-retry-btn');
    const listBtn  = document.getElementById('result-list-btn');
    if (retryBtn) retryBtn.addEventListener('click', () => App.navigate('#/exam'));
    if (listBtn)  listBtn.addEventListener('click',  () => App.navigate('#/list'));
  }

  /* ── 初始化年份 checkbox ── */
  function initYearCheckboxes(years) {
    const container = document.getElementById('exam-year-checkboxes');
    if (!container) return;
    container.innerHTML = years.map(y => `
      <label class="checkbox-item">
        <input type="checkbox" value="${y}" checked />
        ${y}年
      </label>
    `).join('');
  }

  /* ── 開始考試 ── */
  function _startExam() {
    // 收集設定
    const yearCbs = document.querySelectorAll('#exam-year-checkboxes input:checked');
    const years   = Array.from(yearCbs).map(cb => cb.value);

    let selectedSub = null;
    const activePill = document.querySelector('#exam-sub-pills .pill.active');
    if (activePill && activePill.dataset.sub) selectedSub = activePill.dataset.sub;

    const countInput    = document.getElementById('exam-count-input');
    const shuffleTog    = document.getElementById('exam-shuffle-toggle');
    const checkedOnlyTog= document.getElementById('exam-checked-only-toggle');

    const count       = parseInt(countInput && countInput.value, 10) || 20;
    const shuffle     = shuffleTog   ? shuffleTog.checked    : true;
    const checkedOnly = checkedOnlyTog ? checkedOnlyTog.checked : false;

    const opts = {
      years:          years.length > 0 ? years : null,
      subspecialties: selectedSub ? [selectedSub] : null,
      checkedOnly,
    };

    let pool;
    if (shuffle) {
      pool = QuestionStore.getRandomQuestions(count, opts);
    } else {
      pool = QuestionStore.getQuestions(opts).slice(0, count);
    }

    if (pool.length === 0) {
      showToast('沒有符合條件的題目', 'danger');
      return;
    }

    _state = { questions: pool, answers: {}, current: 0, submitted: false };
    App.navigate('#/exam/active');
    _renderQuestion();
  }

  /* ── 渲染目前題目 ── */
  function _renderQuestion() {
    const { questions, answers, current, submitted } = _state;
    const q = questions[current];
    if (!q) return;

    // 進度條
    const prog = document.getElementById('exam-progress-bar');
    if (prog) prog.style.width = ((current + 1) / questions.length * 100).toFixed(1) + '%';

    // 題號
    const qnum = document.getElementById('exam-qnum');
    if (qnum) qnum.textContent = `第 ${current + 1} 題 / 共 ${questions.length} 題`;

    // 卡片
    const card = document.getElementById('exam-question-card');
    if (!card) return;

    const selectedAnswer = answers[q.id] || null;

    const optHtml = (q.options || []).map(opt => {
      let cls = '';
      if (submitted) {
        if (opt.letter === q.correctAnswer) cls = 'correct';
        else if (opt.letter === selectedAnswer) cls = 'wrong';
      } else {
        if (opt.letter === selectedAnswer) cls = 'selected';
      }
      const disabled = submitted ? 'disabled' : '';
      return `<li class="exam-option ${cls}" data-letter="${_esc(opt.letter)}" ${disabled}>
        <span class="option-letter">${_esc(opt.letter)}.</span>
        <span>${_esc(opt.text)}</span>
      </li>`;
    }).join('');

    const images = (q.images || []).length > 0
      ? `<div class="question-images">${q.images.map(src =>
          `<img src="${_esc(src)}" alt="題目圖片" loading="lazy" />`
        ).join('')}</div>`
      : '';

    const expCls  = submitted ? 'visible' : '';
    const expHtml = q.explanation
      ? `<div class="exam-explanation ${expCls}">${_esc(q.explanation)}</div>`
      : '';

    const subBadge  = `<span class="badge badge-sub" data-sub="${_esc(q.subspecialty)}">${_esc(q.subspecialty)}</span>`;
    const yearBadge = `<span class="badge badge-year">${q.year}</span>`;

    card.innerHTML = `
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;">${yearBadge}${subBadge}</div>
      <p class="exam-question-text">${_esc(q.questionText)}</p>
      ${images}
      <ul class="exam-options">${optHtml}</ul>
      ${expHtml}
    `;

    // 選項點擊（未 submitted）
    if (!submitted) {
      card.querySelectorAll('.exam-option').forEach(li => {
        li.addEventListener('click', function () {
          const letter = this.dataset.letter;
          _state.answers[q.id] = letter;
          // 更新 UI
          card.querySelectorAll('.exam-option').forEach(el => el.classList.remove('selected'));
          this.classList.add('selected');
          _updateGrid();
        });
      });
    }

    // 圖片燈箱
    card.querySelectorAll('.question-images img').forEach(img => {
      img.addEventListener('click', () => _lightbox(img.src));
    });

    // 按鈕狀態
    const prevBtn = document.getElementById('exam-prev-btn');
    const nextBtn = document.getElementById('exam-next-btn');
    if (prevBtn) prevBtn.disabled = (current === 0);
    if (nextBtn) {
      if (submitted && current === questions.length - 1) {
        nextBtn.textContent = '查看結果';
      } else if (current === questions.length - 1 && !submitted) {
        nextBtn.textContent = '提交答案';
      } else {
        nextBtn.textContent = '下一題';
      }
    }

    _updateGrid();
  }

  /* ── 下一題 / 提交 ── */
  function _handleNext() {
    const { questions, current, submitted } = _state;
    const isLast = current === questions.length - 1;

    if (submitted && isLast) {
      _showResult();
      return;
    }

    if (isLast && !submitted) {
      // 確認提交
      const unanswered = questions.filter(q => !_state.answers[q.id]).length;
      if (unanswered > 0) {
        if (!confirm(`還有 ${unanswered} 題未作答，確定要提交嗎？`)) return;
      }
      _state.submitted = true;
      _renderQuestion();
      return;
    }

    _navigate(1);
  }

  /* ── 導覽 ── */
  function _navigate(delta) {
    const newIdx = _state.current + delta;
    if (newIdx < 0 || newIdx >= _state.questions.length) return;
    _state.current = newIdx;
    _renderQuestion();
  }

  /* ── 結束考試確認 ── */
  function _confirmEnd() {
    if (!confirm('確定要結束考試嗎？')) return;
    if (!_state.submitted) _state.submitted = true;
    _showResult();
  }

  /* ── 切換題目格線 ── */
  function _toggleGrid() {
    const grid = document.getElementById('exam-grid');
    if (!grid) return;
    grid.hidden = !grid.hidden;
  }

  /* ── 更新格線 ── */
  function _updateGrid() {
    const grid = document.getElementById('exam-grid');
    if (!grid) return;
    const { questions, answers, current, submitted } = _state;

    grid.innerHTML = questions.map((q, i) => {
      let cls = '';
      if (submitted) {
        const ans = answers[q.id];
        if (!ans) cls = '';
        else cls = (ans === q.correctAnswer) ? 'correct' : 'wrong';
      } else {
        if (answers[q.id]) cls = 'answered';
      }
      if (i === current) cls += ' current';
      return `<button class="exam-grid-cell ${cls}" data-idx="${i}">${i + 1}</button>`;
    }).join('');

    grid.querySelectorAll('.exam-grid-cell').forEach(cell => {
      cell.addEventListener('click', function () {
        _state.current = parseInt(this.dataset.idx, 10);
        _renderQuestion();
        const g = document.getElementById('exam-grid');
        if (g) g.hidden = true;
      });
    });
  }

  /* ── 顯示結果 ── */
  function _showResult() {
    App.navigate('#/exam/result');
    const { questions, answers } = _state;

    let correct = 0, wrong = 0, skipped = 0;
    const wrongItems = [];

    questions.forEach(q => {
      const ans = answers[q.id];
      if (!ans) { skipped++; wrongItems.push({ q, ans: null }); }
      else if (ans === q.correctAnswer) { correct++; }
      else { wrong++; wrongItems.push({ q, ans }); }
    });

    const total  = questions.length;
    const pct    = total > 0 ? Math.round(correct / total * 100) : 0;

    const scoreEl = document.getElementById('result-score');
    if (scoreEl) scoreEl.textContent = pct + '%';

    const statsEl = document.getElementById('result-stats');
    if (statsEl) {
      statsEl.innerHTML = `
        <div class="result-stat correct">
          <div class="result-stat-num">${correct}</div>
          <div class="result-stat-label">答對</div>
        </div>
        <div class="result-stat wrong">
          <div class="result-stat-num">${wrong}</div>
          <div class="result-stat-label">答錯</div>
        </div>
        <div class="result-stat skipped">
          <div class="result-stat-num">${skipped}</div>
          <div class="result-stat-label">未作答</div>
        </div>
        <div class="result-stat">
          <div class="result-stat-num">${total}</div>
          <div class="result-stat-label">總題數</div>
        </div>
      `;
    }

    const reviewEl = document.getElementById('result-review');
    if (reviewEl) {
      if (wrongItems.length === 0) {
        reviewEl.innerHTML = '<p style="color:var(--success);font-weight:700;text-align:center;padding:20px;">全部答對！太厲害了！</p>';
      } else {
        reviewEl.innerHTML = `
          <h3 style="font-size:.95rem;font-weight:700;margin-bottom:12px;">錯題 / 未作答（${wrongItems.length} 題）</h3>
          ${wrongItems.map(({ q, ans }) => {
            const statusBadge = ans === null
              ? `<span class="badge" style="background:#f1f5f9;color:var(--text-muted);">未作答</span>`
              : `<span class="badge" style="background:#fef2f2;color:var(--danger);">選 ${_esc(ans)}，答案是 ${_esc(q.correctAnswer)}</span>`;
            const exp = q.explanation
              ? `<div class="result-review-body">${_esc(q.explanation)}</div>`
              : '';
            return `
              <div class="result-review-item">
                <div class="result-review-header">
                  <span class="badge badge-year">${q.year}</span>
                  <span class="badge badge-sub" data-sub="${_esc(q.subspecialty)}">${_esc(q.subspecialty)}</span>
                  #${q.number}
                  ${statusBadge}
                </div>
                <div class="result-review-body">${_esc(q.questionText)}</div>
                ${exp}
              </div>
            `;
          }).join('')}
        `;
      }
    }
  }

  /* ── 燈箱 ── */
  function _lightbox(src) {
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.innerHTML = `<img src="${_esc(src)}" alt="大圖預覽" />`;
    box.addEventListener('click', () => box.remove());
    document.body.appendChild(box);
  }

  function _esc(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  return { init, initYearCheckboxes };
})();
