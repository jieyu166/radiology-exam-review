const fs = require('fs');
const vm = require('vm');

const storage = {};
const localStorage = storage;
Object.defineProperties(localStorage, {
  getItem: { enumerable: false, value: key => Object.prototype.hasOwnProperty.call(storage, key) ? storage[key] : null },
  setItem: { enumerable: false, value: (key, value) => { storage[key] = String(value); } },
  removeItem: { enumerable: false, value: key => { delete storage[key]; } },
});
const listeners = {};
const fakeWindow = {
  addEventListener: (name, fn) => { (listeners[name] = listeners[name] || []).push(fn); },
  document: { visibilityState: 'visible', addEventListener: (name, fn) => { (listeners['doc:' + name] = listeners['doc:' + name] || []).push(fn); } },
};
const context = { console, localStorage, crypto: require('crypto').webcrypto, window: fakeWindow };
vm.createContext(context);
vm.runInContext(
  fs.readFileSync('js/data-loader.js', 'utf8') + '\nglobalThis.DataLoader = DataLoader;\n' +
  fs.readFileSync('js/attempt-outbox.js', 'utf8') + '\nglobalThis.AttemptOutbox = AttemptOutbox;',
  context,
);
const api = context.DataLoader;
const outbox = context.AttemptOutbox;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

(async () => {
  // no session → nothing is sent
  const calls = [];
  outbox.configure({ transport: async (queue, items) => { calls.push([queue, items.map(i => i.clientId || i.questionId)]); return { accepted: items.map(i => i.clientId || i.questionId) }; } });
  api.recordAnswer('2024-001', { chosen: 'A', correct: false, clientTs: 1 });
  let result = await outbox.flush();
  assert(result.skipped === true && calls.length === 0, 'flush is skipped without a session');
  assert(outbox.pendingCount() === 1, 'pending count counts queued items');

  // with session: order attempts → bookmarks → exams, batches ≤ 40
  api.setSession({ token: 't', username: 'u', expiresAt: Date.now() + 1e6 });
  for (let i = 0; i < 45; i++) api.recordAnswer('2024-00' + (i % 5), { chosen: 'B', correct: true, clientTs: 100 + i });
  api.toggleStar('2024-001');
  api.addExamRecord({ total: 1, correct: 1, wrong: 0, skipped: 0 });
  result = await outbox.flush();
  assert(result.sent === 48 && result.failed === 0, 'all items sent: ' + JSON.stringify(result));
  assert(calls.map(c => c[0]).join(',') === 'attempts,attempts,bookmarks,exams', 'queue order and batching: ' + calls.map(c => c[0]));
  assert(calls[0][1].length === 40 && calls[1][1].length === 6, 'batches of 40 then remainder');
  assert(outbox.pendingCount() === 0, 'outbox empty after flush');
  assert(Number.isFinite(api.getProgress().sync.lastSyncAt), 'lastSyncAt set');

  // partial failure keeps order and stops
  calls.length = 0;
  let fail = true;
  outbox.configure({ transport: async (queue, items) => {
    calls.push([queue, items.length]);
    if (queue === 'attempts' && calls.length === 2 && fail) { const e = new Error('net'); throw e; }
    return { accepted: items.map(i => i.clientId || i.questionId) };
  } });
  for (let i = 0; i < 50; i++) api.recordAnswer('2024-009', { chosen: 'C', correct: false, clientTs: 1000 + i });
  api.toggleStar('2024-002');
  result = await outbox.flush();
  assert(result.sent === 40 && result.failed === 10, 'first batch sent, second failed: ' + JSON.stringify(result));
  assert(calls.length === 2, 'flush stops after the first failure');
  const remaining = api.getOutbox();
  assert(remaining.attempts.length === 10 && remaining.attempts[0].clientTs === 1040, 'remaining items keep original order');
  assert(remaining.bookmarks.length === 1, 'later queues untouched after failure');
  fail = false;
  result = await outbox.flush();
  assert(result.sent === 11 && outbox.pendingCount() === 0, 'retry drains the rest');

  // invalid items are dropped, accepted items removed
  calls.length = 0;
  outbox.configure({ transport: async (queue, items) => ({ accepted: items.slice(1).map(i => i.clientId), invalid: [items[0].clientId] }) });
  api.recordAnswer('2024-003', { chosen: 'A', correct: true, clientTs: 5000 });
  api.recordAnswer('2024-004', { chosen: 'A', correct: true, clientTs: 5001 });
  result = await outbox.flush();
  assert(result.invalid === 1 && result.sent === 1 && outbox.pendingCount() === 0, 'invalid item removed from outbox');

  // 401 clears the session and keeps the outbox
  outbox.configure({ transport: async () => { const e = new Error('unauthorized'); e.status = 401; throw e; } });
  api.recordAnswer('2024-005', { chosen: 'A', correct: true, clientTs: 6000 });
  result = await outbox.flush();
  assert(result.failed === 1 && api.getSession() === null && outbox.pendingCount() === 1, '401 clears session, keeps outbox');

  // triggers are installed once and fire flush
  api.setSession({ token: 't', username: 'u', expiresAt: Date.now() + 1e6 });
  let kicked = 0;
  outbox.configure({ transport: async (queue, items) => { kicked++; return { accepted: items.map(i => i.clientId || i.questionId) }; } });
  outbox.install(fakeWindow);
  outbox.install(fakeWindow);
  await new Promise(r => setTimeout(r, 10));
  assert(listeners.online.length === 1 && listeners.pagehide.length === 1 && listeners['doc:visibilitychange'].length === 1, 'listeners installed once');
  assert(kicked >= 1, 'install flushes immediately');
  const subs = [];
  outbox.subscribe(n => subs.push(n));
  api.recordAnswer('2024-006', { chosen: 'A', correct: true, clientTs: 7000 });
  listeners.online[0]();
  await new Promise(r => setTimeout(r, 10));
  assert(subs[subs.length - 1] === 0, 'subscriber notified with pending count after flush');
  console.log('attempt outbox tests passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
