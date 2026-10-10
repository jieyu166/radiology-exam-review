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
const context = { console, localStorage, crypto: require('crypto').webcrypto };
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

  // ── empty + malformed ──
  let progress = api.getProgress();
  assert(progress.schemaVersion === 3, 'progress should use schema version 3');
  assert(Array.isArray(progress.attempts) && progress.attempts.length === 0, 'empty attempts');
  assert(progress.outbox && Array.isArray(progress.outbox.attempts), 'outbox queues exist');
  localStorage.setItem('rex_progress', '{not json');
  assert(api.getProgress().schemaVersion === 3, 'malformed entry returns empty progress');

  // ── v2 upgrade is deterministic ──
  const v2 = { schemaVersion: 2, seen: { '2017-008': 1 }, starred: { '2017-008': true }, answers: { '2017-008': { last: 'C', correct: false, ts: 1700000000000, sourceSha256: 'old' } }, examHistory: [{ ts: 1700000001000, total: 1, correct: 0, wrong: 1, skipped: 0, pct: 0, wrongIds: ['2017-008'] }] };
  localStorage.setItem('rex_progress', JSON.stringify(v2));
  const upgraded = api.getProgress();
  assert(upgraded.schemaVersion === 3, 'v2 upgrades to v3');
  assert(upgraded.attempts.length === 1 && upgraded.attempts[0].clientId === 'legacy:2017-008:1700000000000', 'legacy attempt id is deterministic');
  assert(upgraded.attempts[0].source === 'legacy' && upgraded.attempts[0].chosen === 'C', 'legacy attempt keeps chosen');
  assert(upgraded.answers['2017-008'].correct === false && upgraded.answers['2017-008'].sourceSha256 === 'old', 'answers derived from attempts');
  assert(upgraded.examHistory[0].clientId === 'legacy-exam:1700000001000', 'legacy exam id is deterministic');
  assert(upgraded.starred['2017-008'] === true && upgraded.bookmarks['2017-008'].starred === true, 'starred derived from bookmarks');
  api.markSeen('2017-009');
  const again = api.getProgress();
  assert(again.attempts.length === 1 && again.examHistory.length === 1, 'repeated normalization does not duplicate legacy events');
  assert(again.outbox.attempts.length === 0, 'legacy conversion does not enqueue by itself');

  // ── recordAnswer -> attempt + outbox; answers derived from newest ──
  api.recordAnswer('2024-001', { chosen: 'C', correct: false, sourceSha256: 'new-hash', elapsedMs: 42000, confidence: 3, clientTs: 1800000000000 });
  api.recordAnswer('2024-001', { chosen: 'B', correct: true, sourceSha256: 'new-hash', clientTs: 1800000001000 });
  progress = api.getProgress();
  assert(progress.attempts.filter(a => a.questionId === '2024-001').length === 2, 'two attempts recorded');
  assert(progress.answers['2024-001'].correct === true && progress.answers['2024-001'].last === 'B', 'answers reflect newest attempt');
  assert(progress.answers['2024-001'].sourceSha256 === 'new-hash', 'answer should keep source revision');
  assert(progress.outbox.attempts.length === 2, 'outbox holds both attempts');
  const first = progress.attempts.find(a => a.confidence === 3);
  assert(first.elapsedMs === 42000 && first.source === 'card', 'attempt carries timing and confidence');
  assert(progress.answers['2024-001'].correct === true, 'latest attempt wins');
  const dup = api.recordAttempt({ clientId: first.clientId, questionId: '2024-001', chosen: 'A', isCorrect: false });
  assert(api.getProgress().attempts.length === 3, 'same clientId is not recorded twice');
  assert(dup.clientId === first.clientId, 'duplicate returns the attempt');

  // ── exam record ──
  api.addExamRecord({ total: 1, correct: 0, wrong: 1, skipped: 0, sourceSha256ByQuestion: { '2024-001': 'new-hash' } });
  progress = api.getProgress();
  assert(progress.examHistory[0].sourceSha256ByQuestion['2024-001'] === 'new-hash', 'exam history should keep source revision');
  assert(progress.outbox.exams.length === 1 && progress.outbox.exams[0].clientId === progress.examHistory[0].clientId, 'exam result enqueued');

  // ── bookmarks LWW + outbox ──
  assert(api.toggleStar('2024-001') === true && api.isStarred('2024-001') === true, 'toggleStar should star a question');
  assert(api.getProgress().outbox.bookmarks.some(b => b.questionId === '2024-001' && b.starred === true), 'bookmark enqueued');
  api.toggleStar('2024-001');
  assert(api.getProgress().outbox.bookmarks.filter(b => b.questionId === '2024-001').length === 1, 'bookmark outbox keeps one item per question');

  // ── markSynced ──
  const outbox = api.getOutbox();
  api.markSynced({ attempts: outbox.attempts.map(a => a.clientId), bookmarks: ['2024-001'], exams: outbox.exams.map(e => e.clientId) });
  progress = api.getProgress();
  assert(progress.outbox.attempts.length === 0 && progress.outbox.bookmarks.length === 0 && progress.outbox.exams.length === 0, 'markSynced clears acknowledged items');
  assert(Number.isFinite(progress.sync.lastSyncAt), 'lastSyncAt updated');

  // ── mergeSnapshot: clientId dedupe, LWW bookmarks, cursor ──
  const snapshot = {
    attempts: [
      { id: 10, clientId: first.clientId, questionId: '2024-001', chosen: 'C', isCorrect: false, source: 'card', clientTs: 1800000000000 },
      { id: 11, clientId: 'srv-1', questionId: '2019-521', chosen: 'B', isCorrect: true, source: 'card', clientTs: 1800000002000 },
    ],
    bookmarks: [{ questionId: '2024-001', starred: true, updatedAt: Date.now() + 100000 }, { questionId: '2020-100', starred: true, updatedAt: 5 }],
    exams: [{ clientId: 'srv-exam-1', ts: 1800000003000, total: 2, correct: 1, wrong: 1, skipped: 0, pct: 50, wrongIds: ['2024-001'] }],
    latestAttemptId: 11,
  };
  api.mergeSnapshot(snapshot);
  api.mergeSnapshot(snapshot);
  progress = api.getProgress();
  assert(progress.attempts.filter(a => a.clientId === 'srv-1').length === 1, 'snapshot attempts deduped by clientId');
  assert(progress.attempts.filter(a => a.clientId === first.clientId).length === 1, 'existing attempt not duplicated');
  assert(progress.answers['2019-521'].correct === true, 'answers include snapshot attempts');
  assert(progress.starred['2024-001'] === true, 'newer snapshot bookmark wins');
  assert(progress.starred['2020-100'] === true, 'snapshot-only bookmark applied');
  assert(progress.examHistory.filter(e => e.clientId === 'srv-exam-1').length === 1, 'snapshot exams deduped');
  assert(progress.sync.latestAttemptId === 11, 'cursor stored');
  assert(progress.outbox.attempts.length === 0, 'snapshot merge does not enqueue');

  // ── attempts cap ──
  const big = api.getProgress();
  for (let i = 0; i < 5010; i++) big.attempts.push({ clientId: 'cap-' + i, questionId: '2016-001', chosen: 'A', isCorrect: true, source: 'card', clientTs: 1900000000000 + i });
  localStorage.setItem('rex_progress', JSON.stringify(big));
  progress = api.getProgress();
  assert(progress.attempts.length === 5000, 'attempts capped at 5000 newest');
  assert(progress.attempts[progress.attempts.length - 1].clientId === 'cap-5009', 'newest kept');

  // ── export / import ──
  assert(api.exportLegacyEdits()['rex_edits_concepts']['brain-abscess'].name === 'legacy override', 'legacy edits must remain exportable');
  assert(api.exportAllEdits === api.exportLegacyEdits, 'exportLegacyEdits should alias exportAllEdits');
  api.setSession({ token: 'secret-token', username: 'chen.wei', expiresAt: Date.now() + 1000000 });
  const exported = api.exportProgress();
  assert(exported.rex_progress.schemaVersion === 3 && Array.isArray(exported.rex_progress.attempts), 'exportProgress wraps v3 progress with attempts');
  assert(!JSON.stringify(exported).includes('secret-token') && !exported.rex_session, 'export must not include the session token');
  api.clearProgress();
  assert(api.getProgress().examHistory.length === 0, 'clearProgress should reset progress');
  const stats = api.importProgress(exported);
  assert(stats.answers === 5000 && stats.examHistory === 3 && stats.starred === 3, 'importProgress should restore exported progress: ' + JSON.stringify(stats));
  const statsAgain = api.importProgress(exported);
  assert(statsAgain.answers === 0 && statsAgain.examHistory === 0, 'repeated import adds nothing');
  assert(api.getProgress().outbox.attempts.length === 300, 'imported attempts are enqueued (outbox capped) when a session exists');
  api.clearProgress();
  api.importProgress({ rex_progress: v2 });
  const fromV2 = api.getProgress();
  api.clearProgress();
  const converted = JSON.parse(JSON.stringify(upgraded));
  api.importProgress({ rex_progress: converted });
  const fromV3 = api.getProgress();
  assert(JSON.stringify(fromV2.attempts) === JSON.stringify(fromV3.attempts) && JSON.stringify(fromV2.examHistory) === JSON.stringify(fromV3.examHistory), 'importing v2 equals importing the converted v3');

  // ── session ──
  assert(api.getSession().username === 'chen.wei', 'session readable');
  api.setSession({ token: 'expired', expiresAt: Date.now() - 1 });
  assert(api.getSession() === null, 'expired session is null');
  api.clearSession();
  assert(api.getSession() === null, 'session cleared');

  console.log('study progress tests passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
