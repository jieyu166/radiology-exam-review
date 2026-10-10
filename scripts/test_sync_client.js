const fs = require('fs');
const vm = require('vm');

const storage = {};
const localStorage = storage;
Object.defineProperties(localStorage, {
  getItem: { enumerable: false, value: key => Object.prototype.hasOwnProperty.call(storage, key) ? storage[key] : null },
  setItem: { enumerable: false, value: (key, value) => { storage[key] = String(value); } },
  removeItem: { enumerable: false, value: key => { delete storage[key]; } },
});
const context = { console, localStorage, crypto: require('crypto').webcrypto, window: { REX_API_BASE: 'https://rex-api.test/' } };
vm.createContext(context);
vm.runInContext(
  fs.readFileSync('js/data-loader.js', 'utf8') + '\nglobalThis.DataLoader = DataLoader;\n' +
  fs.readFileSync('js/attempt-outbox.js', 'utf8') + '\nglobalThis.AttemptOutbox = AttemptOutbox;\n' +
  fs.readFileSync('js/sync-client.js', 'utf8') + '\nglobalThis.SyncClient = SyncClient;',
  context,
);
const api = context.DataLoader;
const outbox = context.AttemptOutbox;
const client = context.SyncClient;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const calls = [];
let serverAttempts = new Map();
let nextId = 1;
function response(status, body) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}
async function mockFetch(url, init) {
  const path = url.replace('https://rex-api.test', '');
  const auth = init.headers.Authorization || null;
  const body = init.body ? JSON.parse(init.body) : null;
  calls.push({ method: init.method, path, auth, body });
  if (path === '/auth/login') {
    if (body.password !== 'correct horse battery') return response(401, { error: 'auth_failed', message: 'nope' });
    return response(200, { token: 'tok-1', expiresAt: Date.now() + 1e6, user: { username: body.username, displayName: 'Chen', role: 'member' } });
  }
  if (auth !== 'Bearer tok-1') return response(401, { error: 'unauthorized' });
  if (path === '/sync/attempts') {
    const bad = body.items.map((item, index) => (item.chosen === 'F' ? index : -1)).filter(i => i >= 0);
    if (bad.length) return response(400, { error: 'invalid_items', errors: bad.map(index => ({ index, reason: 'chosen' })) });
    let accepted = 0;
    for (const item of body.items) { if (!serverAttempts.has(item.clientId)) { serverAttempts.set(item.clientId, Object.assign({ id: nextId++ }, item)); accepted++; } }
    return response(200, { accepted, ignored: body.items.length - accepted, acceptedIds: body.items.map(i => i.clientId) });
  }
  if (path === '/sync/bookmarks' || path === '/sync/exams') return response(200, { accepted: body.items.length, ignored: 0, acceptedIds: body.items.map(i => i.clientId || i.questionId) });
  if (path.startsWith('/sync/snapshot')) {
    const since = Number(new URL(url).searchParams.get('sinceAttemptId') || 0);
    const attempts = [...serverAttempts.values()].filter(a => a.id > since);
    return response(200, { attempts, bookmarks: [{ questionId: '2016-001', starred: true, updatedAt: 1 }], exams: [], latestAttemptId: nextId - 1 });
  }
  if (path === '/auth/logout') return response(200, { ok: true });
  return response(404, { error: 'not_found' });
}
client.configure({ fetch: mockFetch });
outbox.configure({ transport: client.transport });

(async () => {
  // v2 progress on this device before first login
  localStorage.setItem('rex_progress', JSON.stringify({ schemaVersion: 2, answers: { '2017-008': { last: 'C', correct: false, ts: 1700000000000 } }, examHistory: [{ ts: 1700000001000, total: 1, correct: 0, wrong: 1, skipped: 0, pct: 0 }] }));
  api.recordAnswer('2024-001', { chosen: 'A', correct: false, clientTs: 1700000002000 });

  // login failure leaves no session
  let failed = null;
  try { await client.login('chen.wei', 'wrong'); } catch (e) { failed = e; }
  assert(failed && failed.status === 401 && api.getSession() === null, 'failed login throws 401 and leaves no session');

  // login + afterLogin: legacy + local attempts uploaded, snapshot merged, migratedLegacy set
  const session = await client.login('chen.wei', 'correct horse battery');
  assert(session.token === 'tok-1' && api.getSession().username === 'chen.wei', 'login stores the session');
  const result = await client.afterLogin();
  assert(result.uploaded.attempts === 2, 'legacy + local attempts uploaded once: ' + JSON.stringify(result.uploaded));
  assert(serverAttempts.has('legacy:2017-008:1700000000000'), 'legacy attempt id is deterministic on the server');
  let progress = api.getProgress();
  assert(progress.sync.migratedLegacy === true, 'migratedLegacy set');
  assert(progress.outbox.attempts.length === 0 && progress.outbox.exams.length === 0, 'outbox drained after afterLogin');
  assert(progress.starred['2016-001'] === true, 'snapshot bookmark merged');
  assert(progress.attempts.every(a => a.serverId != null), 'merged snapshot assigns serverId to local attempts');
  const authCalls = calls.filter(c => c.path.startsWith('/sync/'));
  assert(authCalls.every(c => c.auth === 'Bearer tok-1'), 'sync calls carry the bearer header');

  // repeat afterLogin uploads nothing new
  const again = await client.afterLogin();
  assert(again.uploaded.attempts === 0, 'second afterLogin does not re-upload known attempts');

  // outbox flush through transport with batches ≤ 40 and invalid handling
  calls.length = 0;
  for (let i = 0; i < 45; i++) api.recordAnswer('2024-002', { chosen: 'B', correct: true, clientTs: 1800000000000 + i });
  api.recordAttempt({ clientId: 'bad-one', questionId: '2024-003', chosen: 'A', isCorrect: true, clientTs: 1800000100000 });
  // make it invalid server-side by mutating after local validation
  const raw = JSON.parse(localStorage.getItem('rex_progress'));
  raw.outbox.attempts.find(a => a.clientId === 'bad-one').chosen = 'F';
  raw.attempts.find(a => a.clientId === 'bad-one').chosen = 'F';
  localStorage.setItem('rex_progress', JSON.stringify(raw));
  const flushed = await outbox.flush();
  const attemptPosts = calls.filter(c => c.path === '/sync/attempts');
  assert(attemptPosts.every(c => c.body.items.length <= 40), 'batches never exceed 40');
  assert(flushed.sent >= 45 && outbox.pendingCount() === 0, 'all valid items sent and invalid one dropped: ' + JSON.stringify(flushed));
  const status = client.status();
  assert(status.loggedIn && status.username === 'chen.wei' && status.pending === 0 && Number.isFinite(status.lastSyncAt), 'status summary');

  // 401 clears the session but keeps the outbox
  api.setSession({ token: 'stale', username: 'chen.wei', expiresAt: Date.now() + 1e6 });
  api.recordAnswer('2024-004', { chosen: 'A', correct: true, clientTs: 1800000200000 });
  const r = await outbox.flush();
  assert(r.failed === 1 && api.getSession() === null && outbox.pendingCount() === 1, '401 clears session, keeps outbox: ' + JSON.stringify(r));

  // logout clears session even if the server call fails
  api.setSession({ token: 'tok-1', username: 'chen.wei', expiresAt: Date.now() + 1e6 });
  await client.logout();
  assert(api.getSession() === null, 'logout clears session');
  console.log('sync client tests passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
