import test from 'node:test';
import assert from 'node:assert/strict';
import { newToken, hashToken, createSession, lookupSession, deleteSessionByToken, SESSION_TTL_MS, LAST_USED_THROTTLE_MS } from '../src/session.js';
import { migratedDb } from './d1-stub.js';

async function seedUser(db, username = 'chen.wei') {
  await db.prepare('INSERT INTO users (username, display_name, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)').bind(username, username, '$x', 'member', 1).run();
  return (await db.prepare('SELECT id FROM users WHERE username = ?').bind(username).first()).id;
}

test('token is 32 random bytes base64url and only its hash is stored', async () => {
  const { token, tokenHash } = await newToken();
  assert.match(token, /^[A-Za-z0-9_-]{43}$/);
  assert.equal(tokenHash, await hashToken(token));
  assert.notEqual(tokenHash, token);
  const other = await newToken();
  assert.notEqual(other.token, token);
});

test('createSession/lookupSession round trip with 30-day expiry and throttled last_used', async () => {
  const db = migratedDb();
  const userId = await seedUser(db);
  const now = 1_700_000_000_000;
  const { token, expiresAt } = await createSession(db, userId, 'ua', now);
  assert.equal(expiresAt, now + SESSION_TTL_MS);
  const row = await db.prepare('SELECT token_hash, last_used_at FROM sessions').first();
  assert.equal(row.token_hash, await hashToken(token));
  const resolved = await lookupSession(db, token, now + 1000);
  assert.equal(resolved.user.username, 'chen.wei');
  assert.equal((await db.prepare('SELECT last_used_at FROM sessions').first()).last_used_at, now, 'not updated within throttle window');
  await lookupSession(db, token, now + LAST_USED_THROTTLE_MS + 1);
  assert.equal((await db.prepare('SELECT last_used_at FROM sessions').first()).last_used_at, now + LAST_USED_THROTTLE_MS + 1);
});

test('expired, unknown, deleted and disabled-user sessions resolve to null', async () => {
  const db = migratedDb();
  const userId = await seedUser(db);
  const now = 1_700_000_000_000;
  const { token } = await createSession(db, userId, 'ua', now);
  assert.equal(await lookupSession(db, token, now + SESSION_TTL_MS), null, 'expired');
  assert.equal(await lookupSession(db, 'unknown-token-value-here', now), null, 'unknown');
  await db.prepare('UPDATE users SET disabled_at = ? WHERE id = ?').bind(now, userId).run();
  assert.equal(await lookupSession(db, token, now + 1), null, 'disabled user');
  await db.prepare('UPDATE users SET disabled_at = NULL WHERE id = ?').bind(userId).run();
  assert.ok(await lookupSession(db, token, now + 1));
  await deleteSessionByToken(db, token);
  assert.equal(await lookupSession(db, token, now + 1), null, 'deleted');
});
