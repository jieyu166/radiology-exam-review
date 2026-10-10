import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../src/index.js';
import { makeEnv, call } from './d1-stub.js';
import { createInvite } from '../src/invites.js';
import { MAX_FAILURES } from '../src/auth.js';

const BOOT = 'BOOTSTRAPBOOTSTRAPBOOT22';
const PASS = 'correct horse battery';

async function bootstrap(env, username = 'boss') {
  const res = await call(worker, env, 'POST', '/auth/register', { body: { username, password: PASS, inviteCode: BOOT } });
  assert.equal(res.status, 201, JSON.stringify(res.body));
  return res.body;
}

test('bootstrap code registers the first user only; admin role from ADMIN_USERNAMES', async () => {
  const env = makeEnv();
  const first = await bootstrap(env, 'Boss');
  assert.equal(first.user.username, 'boss');
  assert.equal(first.user.role, 'admin');
  assert.equal(first.bootstrap, true);
  assert.match(first.token, /^[A-Za-z0-9_-]{43}$/);
  const second = await call(worker, env, 'POST', '/auth/register', { body: { username: 'other', password: PASS, inviteCode: BOOT } });
  assert.equal(second.status, 400);
  assert.equal(second.body.error, 'invite_invalid');
});

test('username normalization and validation (spec example table)', async () => {
  const env = makeEnv();
  await bootstrap(env);
  const { code } = await createInvite(env.DB, { createdBy: 1, note: 'x', now: Date.now() });
  const ok = await call(worker, env, 'POST', '/auth/register', { body: { username: 'Chen.Wei', password: PASS, inviteCode: code } });
  assert.equal(ok.status, 201);
  assert.equal(ok.body.user.username, 'chen.wei');
  assert.equal(ok.body.user.role, 'member');
  for (const bad of ['ab', '_lead']) {
    const res = await call(worker, env, 'POST', '/auth/register', { body: { username: bad, password: PASS, inviteCode: code } });
    assert.equal(res.status, 400);
    assert.equal(res.body.error, 'invalid_username');
  }
  const short = await call(worker, env, 'POST', '/auth/register', { body: { username: 'valid.name', password: 'short', inviteCode: code } });
  assert.equal(short.body.error, 'invalid_password');
});

test('invite is single-use and marked used in the same batch; used/revoked/expired are rejected', async () => {
  const env = makeEnv();
  await bootstrap(env);
  const now = Date.now();
  const used = await createInvite(env.DB, { createdBy: 1, note: 'used', now });
  const first = await call(worker, env, 'POST', '/auth/register', { body: { username: 'one', password: PASS, inviteCode: used.code } });
  assert.equal(first.status, 201);
  const row = await env.DB.prepare('SELECT used_by, used_at FROM invites WHERE id = ?').bind(used.id).first();
  assert.equal(row.used_by, first.body.user.id);
  assert.ok(row.used_at);
  const again = await call(worker, env, 'POST', '/auth/register', { body: { username: 'two', password: PASS, inviteCode: used.code } });
  assert.equal(again.status, 400); assert.equal(again.body.error, 'invite_invalid');

  const revoked = await createInvite(env.DB, { createdBy: 1, note: 'revoked', now });
  await env.DB.prepare('UPDATE invites SET revoked_at = ? WHERE id = ?').bind(now, revoked.id).run();
  const r2 = await call(worker, env, 'POST', '/auth/register', { body: { username: 'three', password: PASS, inviteCode: revoked.code } });
  assert.equal(r2.body.error, 'invite_invalid');

  const expired = await createInvite(env.DB, { createdBy: 1, note: 'expired', now: now - 400 * 24 * 3600 * 1000 });
  const r3 = await call(worker, env, 'POST', '/auth/register', { body: { username: 'four', password: PASS, inviteCode: expired.code } });
  assert.equal(r3.body.error, 'invite_invalid');
  assert.equal((await env.DB.prepare('SELECT COUNT(*) AS n FROM users').first()).n, 2, 'no user created for rejected invites');
});

test('login: success, wrong password, unknown user share one message; lockout after 5 failures; reset on success', async () => {
  const env = makeEnv();
  await bootstrap(env);
  const ok = await call(worker, env, 'POST', '/auth/login', { body: { username: 'BOSS', password: PASS } });
  assert.equal(ok.status, 200);
  assert.equal(ok.body.user.role, 'admin');
  const wrong = await call(worker, env, 'POST', '/auth/login', { body: { username: 'boss', password: 'nope-nope' } });
  const unknown = await call(worker, env, 'POST', '/auth/login', { body: { username: 'ghost', password: 'nope-nope' } });
  assert.equal(wrong.status, 401); assert.equal(unknown.status, 401);
  assert.equal(wrong.body.message, unknown.body.message);

  for (let i = 1; i < MAX_FAILURES; i++) await call(worker, env, 'POST', '/auth/login', { body: { username: 'boss', password: 'nope-nope' } });
  const locked = await call(worker, env, 'POST', '/auth/login', { body: { username: 'boss', password: PASS } });
  assert.equal(locked.status, 423);
  assert.equal(locked.body.error, 'locked');
  assert.ok(locked.body.retryAfterSeconds > 0);

  // simulate lock expiry
  await env.DB.prepare('UPDATE login_attempts SET locked_until = ? WHERE username = ?').bind(Date.now() - 1, 'boss').run();
  const after = await call(worker, env, 'POST', '/auth/login', { body: { username: 'boss', password: PASS } });
  assert.equal(after.status, 200);
  assert.equal((await env.DB.prepare('SELECT failed_count FROM login_attempts WHERE username = ?').bind('boss').first()).failed_count, 0);
});

test('rate limiter rejection yields 429 before password verification', async () => {
  const env = makeEnv({ LOGIN_LIMITER: { limit: async () => ({ success: false }) } });
  const res = await call(worker, env, 'POST', '/auth/login', { body: { username: 'boss', password: PASS } });
  assert.equal(res.status, 429);
});

test('me/logout: token works, logout invalidates, disabled user gets 401', async () => {
  const env = makeEnv();
  const { token } = await bootstrap(env);
  const me = await call(worker, env, 'GET', '/auth/me', { token });
  assert.equal(me.status, 200); assert.equal(me.body.user.username, 'boss');
  const noToken = await call(worker, env, 'GET', '/auth/me');
  assert.equal(noToken.status, 401);
  await env.DB.prepare('UPDATE users SET disabled_at = ? WHERE username = ?').bind(Date.now(), 'boss').run();
  assert.equal((await call(worker, env, 'GET', '/auth/me', { token })).status, 401);
  await env.DB.prepare('UPDATE users SET disabled_at = NULL WHERE username = ?').bind('boss').run();
  const out = await call(worker, env, 'POST', '/auth/logout', { token });
  assert.equal(out.status, 200);
  assert.equal((await call(worker, env, 'GET', '/auth/me', { token })).status, 401);
});

test('low-iteration hash is transparently upgraded on successful login', async () => {
  const env = makeEnv();
  await bootstrap(env);
  const { hashPassword, parsePhc } = await import('../src/password.js');
  await env.DB.prepare('UPDATE users SET password_hash = ? WHERE username = ?').bind(await hashPassword(PASS, 1000), 'boss').run();
  const res = await call(worker, env, 'POST', '/auth/login', { body: { username: 'boss', password: PASS } });
  assert.equal(res.status, 200);
  const stored = (await env.DB.prepare('SELECT password_hash FROM users WHERE username = ?').bind('boss').first()).password_hash;
  assert.equal(parsePhc(stored).iterations, 100000);
});

test('CORS headers and OPTIONS preflight on the router', async () => {
  const env = makeEnv();
  const pre = await call(worker, env, 'OPTIONS', '/auth/login', { origin: 'https://jieyu166.github.io' });
  assert.equal(pre.status, 204);
  assert.equal(pre.headers.get('Access-Control-Allow-Origin'), 'https://jieyu166.github.io');
  assert.equal(pre.headers.get('Access-Control-Max-Age'), '7200');
  const health = await call(worker, env, 'GET', '/health', { origin: 'https://evil.example' });
  assert.equal(health.status, 200);
  assert.equal(health.headers.get('Access-Control-Allow-Origin'), null);
  assert.equal(health.headers.get('Vary'), 'Origin');
});
