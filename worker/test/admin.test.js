import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../src/index.js';
import { makeEnv, call } from './d1-stub.js';

const BOOT = 'BOOTSTRAPBOOTSTRAPBOOT22';
const PASS = 'correct horse battery';

async function setup() {
  const env = makeEnv();
  const admin = (await call(worker, env, 'POST', '/auth/register', { body: { username: 'boss', password: PASS, inviteCode: BOOT } })).body;
  const invite = (await call(worker, env, 'POST', '/admin/invites', { token: admin.token, body: { note: 'R2 王醫師' } })).body;
  const member = (await call(worker, env, 'POST', '/auth/register', { body: { username: 'r2.wang', password: PASS, inviteCode: invite.code } })).body;
  return { env, admin, member, invite };
}

test('member is forbidden on every admin route', async () => {
  const { env, member } = await setup();
  for (const [method, path] of [['POST', '/admin/invites'], ['GET', '/admin/invites'], ['DELETE', '/admin/invites/1'], ['GET', '/admin/users'], ['POST', '/admin/users/1/disable']]) {
    const res = await call(worker, env, method, path, { token: member.token, body: method === 'POST' ? {} : undefined });
    assert.equal(res.status, 403, `${method} ${path}`);
  }
});

test('create invite reveals the code once; listing shows note and status only', async () => {
  const { env, admin, invite } = await setup();
  assert.match(invite.code, /^[A-Z2-7]{24}$/);
  const row = await env.DB.prepare('SELECT code_hash FROM invites WHERE id = ?').bind(invite.id).first();
  assert.notEqual(row.code_hash, invite.code);
  assert.match(row.code_hash, /^[0-9a-f]{64}$/);
  const list = (await call(worker, env, 'GET', '/admin/invites', { token: admin.token })).body.invites;
  assert.equal(list.length, 1);
  assert.equal(list[0].note, 'R2 王醫師');
  assert.equal(list[0].status, 'used');
  assert.equal(list[0].usedBy, 'r2.wang');
  assert.ok(!('code' in list[0]));
});

test('revoked invite cannot be used; revoking a used invite is 404', async () => {
  const { env, admin, invite } = await setup();
  const fresh = (await call(worker, env, 'POST', '/admin/invites', { token: admin.token, body: { note: 'fresh', expiresInDays: 3 } })).body;
  const revoke = await call(worker, env, 'DELETE', `/admin/invites/${fresh.id}`, { token: admin.token });
  assert.equal(revoke.status, 200);
  const reg = await call(worker, env, 'POST', '/auth/register', { body: { username: 'late', password: PASS, inviteCode: fresh.code } });
  assert.equal(reg.status, 400);
  assert.equal(reg.body.error, 'invite_invalid');
  const again = await call(worker, env, 'DELETE', `/admin/invites/${invite.id}`, { token: admin.token });
  assert.equal(again.status, 404);
});

test('disable user: listing shows disabledAt, old token is 401, self-disable refused', async () => {
  const { env, admin, member } = await setup();
  assert.equal((await call(worker, env, 'GET', '/auth/me', { token: member.token })).status, 200);
  const res = await call(worker, env, 'POST', `/admin/users/${member.user.id}/disable`, { token: admin.token, body: {} });
  assert.equal(res.status, 200);
  assert.equal((await call(worker, env, 'GET', '/auth/me', { token: member.token })).status, 401);
  const users = (await call(worker, env, 'GET', '/admin/users', { token: admin.token })).body.users;
  assert.ok(users.find(u => u.username === 'r2.wang').disabledAt);
  const self = await call(worker, env, 'POST', `/admin/users/${admin.user.id}/disable`, { token: admin.token, body: {} });
  assert.equal(self.status, 400);
  const login = await call(worker, env, 'POST', '/auth/login', { body: { username: 'r2.wang', password: PASS } });
  assert.equal(login.status, 401, 'disabled user cannot log in');
});
