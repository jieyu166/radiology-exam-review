const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('js/note-renderer.js', 'utf8') + '\n' + fs.readFileSync('js/vault-question-view.js', 'utf8') + '\nglobalThis.VaultQuestionView = VaultQuestionView;';
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
console.log('vault question view tests passed');
