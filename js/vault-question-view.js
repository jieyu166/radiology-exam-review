/* =====================================================
   vault-question-view.js — question card/exam projection view
   ===================================================== */

const VaultQuestionView = (function () {
  'use strict';

  function _esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function _lines(raw) {
    return String(raw || '').split(/\r?\n/);
  }

  function _sliceLines(raw, range) {
    const lines = _lines(raw);
    return lines.slice(Math.max(0, (range.startLine || 1) - 1), range.endLine || lines.length).join('\n');
  }

  function _acceptedAnswers(sr) {
    if (Array.isArray(sr.acceptedAnswers)) return [...new Set(sr.acceptedAnswers.map(value => String(value).toUpperCase()))].sort();
    if (sr.correctAnswer) return [String(sr.correctAnswer).toUpperCase()];
    return [];
  }

  function _chosenAnswers(chosen) {
    if (Array.isArray(chosen)) return [...new Set(chosen.map(value => String(value).toUpperCase()))].sort();
    if (chosen == null || chosen === '') return [];
    return [String(chosen).toUpperCase()];
  }

  function _isScorable(sr) {
    return sr.scorable !== false && sr.answerStatus !== 'unresolved' && sr.answerStatus !== 'no_valid_answer' && (sr.answerMode || 'single') !== 'none';
  }

  function _isCorrect(sr, chosen) {
    if (!_isScorable(sr)) return false;
    const accepted = _acceptedAnswers(sr);
    const selected = _chosenAnswers(chosen);
    const mode = sr.answerMode || (accepted.length > 1 ? 'all' : 'single');
    if (mode === 'any' || mode === 'single') return selected.length === 1 && accepted.includes(selected[0]);
    if (mode === 'all') return selected.length === accepted.length && selected.every(value => accepted.includes(value));
    return false;
  }

  function _optionParts(raw, sr) {
    const lines = _lines(raw);
    const frontLines = lines.slice(Math.max(0, sr.front.startLine - 1), sr.front.endLine || lines.length);
    const optionRanges = sr.options || [];
    const firstOption = optionRanges.length ? Math.max(0, optionRanges[0].startLine - sr.front.startLine) : frontLines.length;
    const questionLines = frontLines.slice(0, firstOption);
    const options = optionRanges.map((range, index) => {
      const source = lines.slice(range.startLine - 1, range.endLine);
      const first = source.shift() || '';
      const match = /^\s*(?:\(([A-E])\)|([A-E])[.)])\s*(.*)$/i.exec(first);
      const text = [match ? match[3] : first].concat(source).join('\n').trim();
      return { letter: range.letter || (match && (match[1] || match[2]).toUpperCase()) || String.fromCharCode(65 + index), text };
    });
    const questionText = questionLines.join('\n').replace(/^(?:\s*#\S+\s*)+/, '').trim();
    return { questionText, options };
  }

  function _noteRenderer(raw, note, options) {
    if (typeof NoteRenderer !== 'undefined') return NoteRenderer.render(raw, Object.assign({}, options || {}, { record: note.record }));
    return _esc(raw).replace(/\n/g, '<br />');
  }

  function renderHtml(note, state, options) {
    if (!note || !note.record || !note.record.sr) return '<div class="vault-question-empty">題目缺少 SR projection</div>';
    const sr = note.record.sr;
    const current = state || {};
    const mode = (options && options.mode) || 'card';
    const parts = _optionParts(note.raw, sr);
    const selected = current.selected || (sr.answerMode === 'all' ? [] : '');
    const revealed = current.revealed === true;
    const accepted = _acceptedAnswers(sr);
    const selectedAnswers = _chosenAnswers(selected);
    const correct = accepted.join(',');
    const scorable = _isScorable(sr);
    const reviewBadge = !scorable ? `<div class="vault-question-review-status">${_esc(sr.answerStatus === 'no_valid_answer' ? '無可接受答案' : '待覆核，不計分')}</div>` : '';
    const optionHtml = parts.options.map(option => {
      const selectedClass = selectedAnswers.includes(option.letter) ? ' selected' : '';
      const answerClass = revealed && accepted.includes(option.letter) ? ' correct' : (revealed && selectedAnswers.includes(option.letter) ? ' incorrect' : '');
      const tag = mode === 'exam' ? 'button' : 'button';
      return `<${tag} type="button" class="vault-question-option${selectedClass}${answerClass}" data-option="${_esc(option.letter)}"><span class="option-letter">${_esc(option.letter)}.</span><span>${_noteRenderer(option.text, note, options)}</span></${tag}>`;
    }).join('');
    const backHtml = revealed ? `<div class="vault-question-back"><div class="vault-answer-badge">${_esc(scorable ? `答案：${correct || '?'}` : (sr.answerStatus === 'no_valid_answer' ? '無可接受答案' : '答案待覆核'))}</div>${_noteRenderer(_sliceLines(note.raw, sr.back), note, options)}</div>` : '';
    const relationHtml = (sr.conceptIds || []).map(id => `<a class="concept-link vault-question-concept" href="#/concept/${encodeURIComponent(id)}">${_esc(id)}</a>`).join('');
    return `<article class="vault-question" data-question-id="${_esc(note.record.id)}" data-source-sha256="${_esc(note.record.sourceSha256 || '')}">
      <div class="vault-question-front">${_noteRenderer(parts.questionText, note, options)}</div>
      ${reviewBadge}
      <div class="vault-question-options">${optionHtml}</div>
      ${revealed && scorable ? `<div class="vault-question-result ${_isCorrect(sr, selected) ? 'correct' : 'incorrect'}">${_isCorrect(sr, selected) ? '答對' : '答錯'}</div>` : ''}
      ${backHtml}
      ${relationHtml ? `<div class="vault-question-relations">相關概念：${relationHtml}</div>` : ''}
    </article>`;
  }

  function scoreAnswers(records, answers) {
    const scorableRecords = records.filter(record => record.sr && _isScorable(record.sr));
    const result = { total: scorableRecords.length, correct: 0, wrong: 0, skipped: 0, unscored: records.length - scorableRecords.length };
    for (const record of scorableRecords) {
      const chosen = answers && answers[record.id];
      if (!chosen) result.skipped++;
      else if (_isCorrect(record.sr, chosen)) result.correct++;
      else result.wrong++;
    }
    result.pct = result.total ? Math.round(result.correct / result.total * 100) : 0;
    return result;
  }

  function bind(container, note, options) {
    if (!container || !note) return null;
    const config = Object.assign({ mode: 'card' }, options || {});
    const state = { selected: note.record.sr && note.record.sr.answerMode === 'all' ? [] : '', revealed: false };
    const render = () => { container.innerHTML = renderHtml(note, state, config); };
    container.addEventListener('click', event => {
      const option = event.target.closest && event.target.closest('[data-option]');
      if (!option) return;
      const mode = note.record.sr && note.record.sr.answerMode;
      if (mode === 'all') {
        const next = _chosenAnswers(state.selected);
        const letter = option.dataset.option || '';
        state.selected = next.includes(letter) ? next.filter(value => value !== letter) : next.concat(letter).sort();
      } else {
        state.selected = option.dataset.option || '';
      }
      if (config.mode === 'card') state.revealed = true;
      const result = { id: note.record.id, sourceSha256: note.record.sourceSha256, chosen: state.selected, correct: _isCorrect(note.record.sr, state.selected), scorable: _isScorable(note.record.sr) };
      if (typeof config.onAnswer === 'function') config.onAnswer(result, note);
      render();
    });
    render();
    return { state, render };
  }

  return { renderHtml, scoreAnswers, bind };
})();
