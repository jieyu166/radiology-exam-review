const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('js/question-timer.js', 'utf8') + '\nglobalThis.QuestionTimer = QuestionTimer;\n' + fs.readFileSync('js/note-renderer.js', 'utf8') + '\n' + fs.readFileSync('js/vault-question-view.js', 'utf8') + '\nglobalThis.VaultQuestionView = VaultQuestionView;';
const context = { console, window: { REX_PUBLICATION_BASE: 'dist/' } };
vm.createContext(context);
vm.runInContext(code, context);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const note = {
  record: {
    id: '2024-001', sourceSha256: 'source-hash',
    embeds: [],
    sr: {
      front: { startLine: 1, endLine: 7 },
      back: { startLine: 9, endLine: 11 },
      options: [
        { letter: 'A', startLine: 3, endLine: 3 }, { letter: 'B', startLine: 4, endLine: 4 },
        { letter: 'C', startLine: 5, endLine: 5 }, { letter: 'D', startLine: 6, endLine: 6 },
        { letter: 'E', startLine: 7, endLine: 7 },
      ],
      correctAnswer: 'B', conceptIds: ['brain-abscess'],
    },
  },
  raw: 'Question text\n\n(A) One\n(B) Two\n(C) Three\n(D) Four\n(E) Five\n??\nAns: B\nExplanation body',
};
const html = context.VaultQuestionView.renderHtml(note, { selected: 'C', revealed: true });
assert(html.includes('Question text'), 'front question should render');
assert(html.includes('data-option="C"'), 'selected option should render');
assert(html.includes('答案：B'), 'back should reveal projected answer');
assert(html.includes('Explanation body'), 'back should reveal raw explanation');
assert(html.includes('#/concept/brain-abscess'), 'related concept should render');
const score = context.VaultQuestionView.scoreAnswers([note.record], { '2024-001': 'C' });
assert(score.wrong === 1 && score.correct === 0, 'exam scoring should use projected answer');

const anyNote = {
  record: {
    id: '2017-010', sourceSha256: 'multi-hash', embeds: [],
    sr: {
      front: { startLine: 1, endLine: 6 }, back: { startLine: 8, endLine: 9 },
      options: [
        { letter: 'A', startLine: 2, endLine: 2 }, { letter: 'B', startLine: 3, endLine: 3 },
        { letter: 'C', startLine: 4, endLine: 4 }, { letter: 'D', startLine: 5, endLine: 5 },
      ], answerStatus: 'confirmed', answerMode: 'any', acceptedAnswers: ['B', 'D'], scorable: true,
    },
  },
  raw: 'Question text\n(A) One\n(B) Two\n(C) Three\n(D) Four\n??\nAns: BD\nExplanation',
};
const anyHtml = context.VaultQuestionView.renderHtml(anyNote, { selected: 'D', revealed: true });
assert(anyHtml.includes('答案：B,D'), 'multi-answer projection should reveal accepted answers');
const anyScore = context.VaultQuestionView.scoreAnswers([anyNote.record], { '2017-010': 'D' });
assert(anyScore.correct === 1 && anyScore.wrong === 0, 'any answer mode should accept either answer');

const unresolvedNote = {
  record: {
    id: '2018-360', sourceSha256: 'unresolved-hash', embeds: [],
    sr: {
      front: { startLine: 1, endLine: 6 }, back: { startLine: 8, endLine: 9 },
      options: [{ letter: 'A', startLine: 2, endLine: 2 }, { letter: 'B', startLine: 3, endLine: 3 }],
      answerStatus: 'unresolved', answerMode: 'none', acceptedAnswers: [], scorable: false,
    },
  },
  raw: 'Question text\n(A) One\n(B) Two\n??\nAnswer status: unresolved',
};
const unresolvedHtml = context.VaultQuestionView.renderHtml(unresolvedNote, { selected: 'A', revealed: true });
assert(unresolvedHtml.includes('待覆核，不計分'), 'unresolved question should show review-only status');
const unresolvedScore = context.VaultQuestionView.scoreAnswers([unresolvedNote.record], { '2018-360': 'A' });
assert(unresolvedScore.total === 0 && unresolvedScore.unscored === 1, 'unresolved question should not be scored');

// reference projection: shown after reveal, hidden before reveal and when empty, always escaped
const refNote = JSON.parse(JSON.stringify(note));
refNote.record.id = '2008-001';
refNote.record.sr.reference = 'AJR 2008;190:S18-S22';
const refRevealed = context.VaultQuestionView.renderHtml(refNote, { selected: 'B', revealed: true });
assert(refRevealed.includes('<div class="vault-question-reference">參考來源：AJR 2008;190:S18-S22</div>'), 'revealed back should show reference block');
assert(refRevealed.indexOf('vault-answer-badge') < refRevealed.indexOf('vault-question-reference'), 'reference block should follow the answer badge');
const refHidden = context.VaultQuestionView.renderHtml(refNote, { selected: 'B', revealed: false });
assert(!refHidden.includes('vault-question-reference'), 'reference must not render before reveal');
const emptyRefNote = JSON.parse(JSON.stringify(note));
emptyRefNote.record.sr.reference = '';
const emptyRefHtml = context.VaultQuestionView.renderHtml(emptyRefNote, { selected: 'B', revealed: true });
assert(!emptyRefHtml.includes('vault-question-reference'), 'empty reference must not render a block');
const noRefHtml = context.VaultQuestionView.renderHtml(note, { selected: 'B', revealed: true });
assert(!noRefHtml.includes('vault-question-reference'), 'missing reference key must not render a block');
const escNote = JSON.parse(JSON.stringify(note));
escNote.record.sr.reference = '<b>bold</b> & more';
const escHtml = context.VaultQuestionView.renderHtml(escNote, { selected: 'B', revealed: true });
assert(escHtml.includes('參考來源：&lt;b&gt;bold&lt;/b&gt; &amp; more'), 'reference text must be HTML-escaped');
assert(!escHtml.includes('<b>bold</b>'), 'reference markup must not be interpreted');
// corrected answer state: official answer shown as wrong, reviewed answer scores
const correctedNote = JSON.parse(JSON.stringify(note));
correctedNote.record.id = '2020-013';
Object.assign(correctedNote.record.sr, { answerStatus: 'corrected', answerMode: 'single', acceptedAnswers: ['D'], correctAnswer: 'D', officialAnswer: 'B', scorable: true });
const correctedWrong = context.VaultQuestionView.renderHtml(correctedNote, { selected: 'B', revealed: true });
assert(correctedWrong.includes('<div class="vault-question-correction">官方公布 B 有誤，依覆核答案 D 計分</div>'), 'corrected question should explain the official answer error');
assert(correctedWrong.includes('vault-question-result incorrect'), 'choosing the official (wrong) answer must be marked incorrect');
const correctedScore = context.VaultQuestionView.scoreAnswers([correctedNote.record], { '2020-013': 'D' });
assert(correctedScore.correct === 1 && correctedScore.total === 1, 'reviewed answer must score on a corrected question');
const confirmedHtml = context.VaultQuestionView.renderHtml(note, { selected: 'B', revealed: true });
assert(!confirmedHtml.includes('vault-question-correction'), 'confirmed question must not show a correction');
const correctedHidden = context.VaultQuestionView.renderHtml(correctedNote, { selected: 'B', revealed: false });
assert(!correctedHidden.includes('vault-question-correction'), 'correction must not show before reveal');
// confidence buttons only in card mode before reveal; result carries timing + confidence
const cardBefore = context.VaultQuestionView.renderHtml(note, { selected: '', revealed: false }, { mode: 'card' });
assert((cardBefore.match(/data-confidence="/g) || []).length === 3, 'card mode shows three confidence buttons before reveal');
const cardAfter = context.VaultQuestionView.renderHtml(note, { selected: 'B', revealed: true }, { mode: 'card' });
assert(!cardAfter.includes('data-confidence'), 'confidence buttons disappear after reveal');
const examBefore = context.VaultQuestionView.renderHtml(note, { selected: '', revealed: false }, { mode: 'exam' });
assert(!examBefore.includes('data-confidence'), 'exam mode never shows confidence buttons');
const timerState = context.QuestionTimer.startTimer(1000);
const built = context.VaultQuestionView.buildResult(note, { selected: 'C', revealed: true, confidence: 3, timer: timerState }, { mode: 'card' }, 43000);
assert(built.elapsedMs === 42000 && built.confidence === 3 && built.source === 'card' && built.correct === false && built.clientTs === 43000, 'buildResult carries elapsedMs, confidence, source: ' + JSON.stringify(built));
const builtExam = context.VaultQuestionView.buildResult(note, { selected: 'B', revealed: false, confidence: 2, timer: null }, { mode: 'exam' }, 5000);
assert(builtExam.source === 'exam' && builtExam.elapsedMs === null && builtExam.correct === true, 'exam result without timer');
assert(context.VaultQuestionView.isCorrect(note.record.sr, 'B') === true && context.VaultQuestionView.isScorable(note.record.sr) === true, 'isCorrect/isScorable exported');
console.log('vault question view tests passed');
