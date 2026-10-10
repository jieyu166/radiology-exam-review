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
const context = { console, localStorage };
vm.createContext(context);
vm.runInContext(code, context);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

(async () => {
  const api = context.DataLoader;
  const legacyLoaders = ['loadIndex', 'loadYear', 'loadConcepts', 'loadConceptsIndex', 'loadConcept', 'loadAllAvailableYears', 'getLoadedQuestions', 'saveQuestionEdit', 'saveConceptEdit', 'discardAllEdits', 'countPendingEdits'];
  legacyLoaders.forEach(name => assert(typeof api[name] === 'undefined', 'legacy data/ loader must be removed: ' + name));
  assert(!/fetch\(/.test(code), 'data-loader.js must not fetch legacy data/ JSON');

  const progress = api.getProgress();
  assert(progress.schemaVersion === 2, 'progress should use schema version 2');
  api.recordAnswer('2024-001', { chosen: 'C', correct: false, sourceSha256: 'new-hash' });
  api.addExamRecord({ total: 1, correct: 0, wrong: 1, skipped: 0, sourceSha256ByQuestion: { '2024-001': 'new-hash' } });
  const saved = api.getProgress();
  assert(saved.answers['2024-001'].sourceSha256 === 'new-hash', 'answer should keep source revision');
  assert(saved.examHistory[0].sourceSha256ByQuestion['2024-001'] === 'new-hash', 'exam history should keep source revision');
  assert(api.exportLegacyEdits()['rex_edits_concepts']['brain-abscess'].name === 'legacy override', 'legacy edits must remain exportable');
  assert(api.exportAllEdits === api.exportLegacyEdits, 'exportLegacyEdits should alias exportAllEdits');
  ['markSeen', 'toggleStar', 'isStarred', 'exportProgress', 'importProgress', 'clearProgress'].forEach(name => assert(typeof api[name] === 'function', 'progress API missing: ' + name));
  assert(api.toggleStar('2024-001') === true && api.isStarred('2024-001') === true, 'toggleStar should star a question');
  const exported = api.exportProgress();
  assert(exported.rex_progress.schemaVersion === 2, 'exportProgress should wrap rex_progress');
  api.clearProgress();
  assert(api.getProgress().examHistory.length === 0, 'clearProgress should reset progress');
  const stats = api.importProgress(exported);
  assert(stats.answers === 1 && stats.examHistory === 1 && stats.starred === 1, 'importProgress should restore exported progress');
  console.log('study progress tests passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
