const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('js/data-loader.js', 'utf8') + '\nglobalThis.DataLoader = DataLoader;';
const storage = {
  rex_edits_concepts: JSON.stringify({ 'brain-abscess': { name: 'legacy override' } }),
};
const localStorage = storage;
Object.defineProperties(localStorage, {
  getItem: { enumerable: false, value: key => Object.prototype.hasOwnProperty.call(storage, key) ? storage[key] : null },
  setItem: { enumerable: false, value: (key, value) => { storage[key] = String(value); } },
  removeItem: { enumerable: false, value: key => { delete storage[key]; } },
  clear: { enumerable: false, value: () => { Object.keys(storage).forEach(key => delete storage[key]); } },
  key: { enumerable: false, value: index => Object.keys(storage)[index] || null },
  length: { enumerable: false, get: () => Object.keys(storage).length },
});
const context = {
  console,
  localStorage,
  fetch: async url => {
    if (url === 'data/2024.json') return { ok: true, json: async () => ({ questions: [{ id: '2024-001', questionText: 'vault text' }] }) };
    if (url === 'data/concepts.json') return { ok: true, json: async () => ({ concepts: { 'brain-abscess': { name: 'vault name' } } }) };
    if (url === 'data/concepts-index.json') return { ok: true, json: async () => ({ concepts: [{ slug: 'brain-abscess', name: 'vault name' }] }) };
    if (url === 'data/index.json') return { ok: true, json: async () => ({ years: [{ year: 2024 }] }) };
    return { ok: false, status: 404, json: async () => ({}) };
  },
};
vm.createContext(context);
vm.runInContext(code, context);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

(async () => {
  const questions = await context.DataLoader.loadYear(2024);
  assert(questions[0].questionText === 'vault text', 'rex_edits must not override loaded content');
  const progress = context.DataLoader.getProgress();
  assert(progress.schemaVersion === 2, 'progress should use schema version 2');
  context.DataLoader.recordAnswer('2024-001', { chosen: 'C', correct: false, sourceSha256: 'new-hash' });
  context.DataLoader.addExamRecord({ total: 1, correct: 0, wrong: 1, skipped: 0, sourceSha256ByQuestion: { '2024-001': 'new-hash' } });
  const saved = context.DataLoader.getProgress();
  assert(saved.answers['2024-001'].sourceSha256 === 'new-hash', 'answer should keep source revision');
  assert(saved.examHistory[0].sourceSha256ByQuestion['2024-001'] === 'new-hash', 'exam history should keep source revision');
  assert(context.DataLoader.exportLegacyEdits()['rex_edits_concepts']['brain-abscess'].name === 'legacy override', 'legacy edits must remain exportable');
  context.DataLoader.saveQuestionEdit('2024-001', { questionText: 'attempted override' });
  assert(!Object.prototype.hasOwnProperty.call(storage, 'rex_edits_year_2024'), 'new content patches must not be written');
  console.log('study progress tests passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
