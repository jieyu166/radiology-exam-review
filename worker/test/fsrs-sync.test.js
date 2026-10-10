import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../src/index.js';
import { makeEnv, call, migratedDb } from './d1-stub.js';

const BOOT = 'BOOTSTRAPBOOTSTRAPBOOT22';
const PASS = 'correct horse battery';

async function login(env) {
  return (await call(worker, env, 'POST', '/auth/register', { body: { username: 'boss', password: PASS, inviteCode: BOOT } })).body.token;
}

function card(questionId, updatedAt, extra = {}) {
  return Object.assign({ questionId, dueAt: 1700000600000, stability: 1.2, difficulty: 5.1, elapsedDays: 0, scheduledDays: 0, learningSteps: 1, reps: 1, lapses: 0, state: 1, lastReviewAt: 1700000000000, updatedAt }, extra);
}

function log(clientId, questionId, extra = {}) {
  return Object.assign({ clientId, questionId, rating: 'good', state: 0, dueAt: 1700000600000, stability: 1.2, difficulty: 5.1, elapsedDays: 0, lastElapsedDays: 0, scheduledDays: 0, learningSteps: 1, reviewedAt: 1700000000000 }, extra);
}

test('migration 0003 rebuilds attempts in place preserving rows and ids', async () => {
  const { D1Stub } = await import('./d1-stub.js');
  const { readFileSync } = await import('node:fs');
  const db = new D1Stub();
  db.exec(readFileSync(new URL('../migrations/0001_accounts.sql', import.meta.url), 'utf8'));
  db.exec(readFileSync(new URL('../migrations/0002_attempts.sql', import.meta.url), 'utf8'));
  db.exec("INSERT INTO users (username, display_name, password_hash, role, created_at) VALUES ('u', 'u', '$x', 'member', 1)");
  db.exec("INSERT INTO attempts (user_id, client_id, question_id, chosen, is_correct, source, elapsed_ms, confidence, source_sha256, client_ts, created_at) VALUES (1, 'a1', 'q1', 'A', 1, 'card', 100, 3, 'sha', 10, 10), (1, 'a2', 'q2', NULL, NULL, 'exam', NULL, NULL, NULL, 20, 20)");
  db.exec(readFileSync(new URL('../migrations/0003_fsrs.sql', import.meta.url), 'utf8'));
  const rows = (await db.prepare('SELECT id, client_id, source, chosen, confidence FROM attempts ORDER BY id').all()).results.map(r => ({ ...r }));
  assert.deepEqual(rows, [{ id: 1, client_id: 'a1', source: 'card', chosen: 'A', confidence: 3 }, { id: 2, client_id: 'a2', source: 'exam', chosen: null, confidence: null }]);
  await db.prepare("INSERT INTO attempts (user_id, client_id, question_id, chosen, is_correct, source, client_ts, created_at) VALUES (1, 'a3', 'q3', 'B', 1, 'review', 30, 30)").run();
  assert.equal((await db.prepare('SELECT COUNT(*) AS n FROM attempts').first()).n, 3);
  await assert.rejects(db.prepare("INSERT INTO attempts (user_id, client_id, question_id, chosen, is_correct, source, client_ts, created_at) VALUES (1, 'a4', 'q4', 'B', 1, 'bogus', 40, 40)").run(), /CHECK|constraint/i);
});

test('migrated schema accepts source=review through the API', async () => {
  const db = migratedDb();
  const row = await db.prepare("SELECT sql FROM sqlite_master WHERE name = 'attempts'").first();
  assert.match(row.sql, /'review'/);
  const env = makeEnv({ DB: db });
  const token = await login(env);
  const res = await call(worker, env, 'POST', '/sync/attempts', { token, body: { items: [{ clientId: 'r1', questionId: '2020-100', chosen: 'A', isCorrect: true, source: 'review', clientTs: 1 }] } });
  assert.equal(res.status, 200);
  assert.equal(res.body.accepted, 1);
});

test('cards are last-write-wins by updatedAt', async () => {
  const env = makeEnv();
  const token = await login(env);
  const first = await call(worker, env, 'POST', '/sync/cards', { token, body: { items: [card('2020-100', 100, { reps: 1 })] } });
  assert.equal(first.body.accepted, 1);
  const newer = await call(worker, env, 'POST', '/sync/cards', { token, body: { items: [card('2020-100', 200, { reps: 2 })] } });
  assert.equal(newer.body.accepted, 1);
  const older = await call(worker, env, 'POST', '/sync/cards', { token, body: { items: [card('2020-100', 150, { reps: 9 })] } });
  assert.equal(older.body.accepted, 0);
  assert.equal(older.body.ignored, 1);
  const snap = (await call(worker, env, 'GET', '/sync/snapshot', { token })).body;
  assert.equal(snap.cards.length, 1);
  assert.equal(snap.cards[0].reps, 2);
  assert.equal(snap.cards[0].updatedAt, 200);
  const bad = await call(worker, env, 'POST', '/sync/cards', { token, body: { items: [card('x', 1, { state: 7 })] } });
  assert.equal(bad.status, 400);
});

test('review logs are idempotent by clientId and snapshot filters by sinceReviewLogId', async () => {
  const env = makeEnv();
  const token = await login(env);
  const items = [log('l1', '2020-100'), log('l2', '2019-521', { rating: 'again', state: 2 })];
  const first = await call(worker, env, 'POST', '/sync/review-logs', { token, body: { items } });
  assert.deepEqual([first.body.accepted, first.body.ignored], [2, 0]);
  const second = await call(worker, env, 'POST', '/sync/review-logs', { token, body: { items } });
  assert.deepEqual([second.body.accepted, second.body.ignored], [0, 2]);
  const snap = (await call(worker, env, 'GET', '/sync/snapshot', { token })).body;
  assert.equal(snap.reviewLogs.length, 2);
  assert.equal(snap.latestReviewLogId, 2);
  const since = (await call(worker, env, 'GET', '/sync/snapshot?sinceReviewLogId=1', { token })).body;
  assert.equal(since.reviewLogs.length, 1);
  assert.equal(since.reviewLogs[0].clientId, 'l2');
  const bad = await call(worker, env, 'POST', '/sync/review-logs', { token, body: { items: [log('l3', 'q', { rating: 'meh' })] } });
  assert.equal(bad.status, 400);
});

test('settings sync last-write-wins and appear in the snapshot', async () => {
  const env = makeEnv();
  const token = await login(env);
  assert.equal((await call(worker, env, 'GET', '/sync/snapshot', { token })).body.settings, null);
  await call(worker, env, 'POST', '/sync/settings', { token, body: { items: [{ newPerDay: 35, dayStartHour: 5, examSecondsPerQuestion: 60, updatedAt: 100 }] } });
  const older = await call(worker, env, 'POST', '/sync/settings', { token, body: { items: [{ newPerDay: 10, dayStartHour: 4, examSecondsPerQuestion: 90, updatedAt: 50 }] } });
  assert.equal(older.body.accepted, 0);
  const snap = (await call(worker, env, 'GET', '/sync/snapshot', { token })).body;
  assert.deepEqual(snap.settings, { newPerDay: 35, dayStartHour: 5, examSecondsPerQuestion: 60, updatedAt: 100 });
  const clamped = await call(worker, env, 'POST', '/sync/settings', { token, body: { items: [{ newPerDay: 999, dayStartHour: 30, updatedAt: 200 }] } });
  assert.equal(clamped.body.accepted, 1);
  assert.deepEqual((await call(worker, env, 'GET', '/sync/snapshot', { token })).body.settings, { newPerDay: 200, dayStartHour: 23, examSecondsPerQuestion: 90, updatedAt: 200 });
});
