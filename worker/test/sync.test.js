import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../src/index.js';
import { makeEnv, call } from './d1-stub.js';
import { clampElapsedMs, validateAttempt, MAX_BATCH } from '../src/attempts.js';

const BOOT = 'BOOTSTRAPBOOTSTRAPBOOT22';
const PASS = 'correct horse battery';

async function login(env, username = 'boss') {
  const res = await call(worker, env, 'POST', '/auth/register', { body: { username, password: PASS, inviteCode: BOOT } });
  return res.body.token;
}

function attempt(i, extra = {}) {
  return Object.assign({ clientId: `c-${i}`, questionId: '2020-100', chosen: 'A', isCorrect: false, source: 'card', elapsedMs: 2500, confidence: 3, sourceSha256: 'sha', clientTs: 1700000000000 + i }, extra);
}

test('elapsed time clamping (spec example table)', () => {
  assert.equal(clampElapsedMs(-5), 0);
  assert.equal(clampElapsedMs(2500), 2500);
  assert.equal(clampElapsedMs(5400000), 1800000);
  assert.equal(clampElapsedMs('fast'), null);
  assert.equal(validateAttempt(attempt(1, { elapsedMs: 'fast' })).value.elapsedMs, null);
});

test('attempts upload is idempotent: 3 accepted then 3 ignored, exactly 3 rows', async () => {
  const env = makeEnv();
  const token = await login(env);
  const items = [attempt(1), attempt(2), attempt(3)];
  const first = await call(worker, env, 'POST', '/sync/attempts', { token, body: { items } });
  assert.equal(first.status, 200);
  assert.deepEqual([first.body.accepted, first.body.ignored], [3, 0]);
  const second = await call(worker, env, 'POST', '/sync/attempts', { token, body: { items } });
  assert.deepEqual([second.body.accepted, second.body.ignored], [0, 3]);
  assert.equal((await env.DB.prepare('SELECT COUNT(*) AS n FROM attempts').first()).n, 3);
  assert.deepEqual(second.body.acceptedIds, ['c-1', 'c-2', 'c-3'], 'ignored ids are still acknowledged for outbox removal');
});

test('an invalid item rejects the whole batch with errors[index]', async () => {
  const env = makeEnv();
  const token = await login(env);
  const res = await call(worker, env, 'POST', '/sync/attempts', { token, body: { items: [attempt(1), attempt(2, { chosen: 'F' })] } });
  assert.equal(res.status, 400);
  assert.equal(res.body.error, 'invalid_items');
  assert.equal(res.body.errors[0].index, 1);
  assert.match(res.body.errors[0].reason, /chosen/);
  assert.equal((await env.DB.prepare('SELECT COUNT(*) AS n FROM attempts').first()).n, 0);
  const tooMany = await call(worker, env, 'POST', '/sync/attempts', { token, body: { items: Array.from({ length: MAX_BATCH + 1 }, (_, i) => attempt(i)) } });
  assert.equal(tooMany.status, 400);
});

test('bookmarks are last-write-wins by updatedAt', async () => {
  const env = makeEnv();
  const token = await login(env);
  await call(worker, env, 'POST', '/sync/bookmarks', { token, body: { items: [{ questionId: '2017-008', starred: false, updatedAt: 100 }] } });
  const newer = await call(worker, env, 'POST', '/sync/bookmarks', { token, body: { items: [{ questionId: '2017-008', starred: true, updatedAt: 200 }] } });
  assert.equal(newer.body.accepted, 1);
  const older = await call(worker, env, 'POST', '/sync/bookmarks', { token, body: { items: [{ questionId: '2017-008', starred: false, updatedAt: 150 }] } });
  assert.equal(older.body.accepted, 0);
  const snap = (await call(worker, env, 'GET', '/sync/snapshot', { token })).body;
  assert.deepEqual(snap.bookmarks, [{ questionId: '2017-008', starred: true, updatedAt: 200 }]);
});

test('exam results are append-only by clientId and snapshot returns everything with cursor filtering', async () => {
  const env = makeEnv();
  const token = await login(env);
  const exam = { clientId: 'exam-1', total: 2, correct: 1, wrong: 1, skipped: 0, pct: 50, wrongIds: ['2020-100'], sourceSha256ByQuestion: { '2020-100': 'sha' }, clientTs: 1700000005000 };
  assert.equal((await call(worker, env, 'POST', '/sync/exams', { token, body: { items: [exam] } })).body.accepted, 1);
  assert.equal((await call(worker, env, 'POST', '/sync/exams', { token, body: { items: [exam] } })).body.ignored, 1);
  await call(worker, env, 'POST', '/sync/attempts', { token, body: { items: [attempt(1), attempt(2, { questionId: '2019-521', chosen: 'B', isCorrect: true })] } });
  const snap = (await call(worker, env, 'GET', '/sync/snapshot', { token })).body;
  assert.equal(snap.attempts.length, 2);
  assert.equal(snap.attempts[1].isCorrect, true);
  assert.equal(snap.latestAttemptId, 2);
  assert.equal(snap.exams.length, 1);
  assert.deepEqual(snap.exams[0].wrongIds, ['2020-100']);
  const since = (await call(worker, env, 'GET', '/sync/snapshot?sinceAttemptId=1', { token })).body;
  assert.equal(since.attempts.length, 1);
  assert.equal(since.attempts[0].clientId, 'c-2');
});

test('users only see their own data; sync requires a session', async () => {
  const env = makeEnv();
  const a = await login(env, 'boss');
  await call(worker, env, 'POST', '/sync/attempts', { token: a, body: { items: [attempt(1)] } });
  const { createInvite } = await import('../src/invites.js');
  const { code } = await createInvite(env.DB, { createdBy: 1, note: '', now: Date.now() });
  const b = (await call(worker, env, 'POST', '/auth/register', { body: { username: 'other', password: PASS, inviteCode: code } })).body.token;
  const snapB = (await call(worker, env, 'GET', '/sync/snapshot', { token: b })).body;
  assert.equal(snapB.attempts.length, 0);
  assert.equal((await call(worker, env, 'GET', '/sync/snapshot')).status, 401);
});
