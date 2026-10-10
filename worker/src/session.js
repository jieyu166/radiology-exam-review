// Bearer session tokens: 32 random bytes (base64url), only the SHA-256 is stored.

import { randomBytes, bytesToBase64url, sha256Hex } from './util.js';
import { HttpError, bearerToken } from './http.js';

export const SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000;
export const LAST_USED_THROTTLE_MS = 5 * 60 * 1000;

export async function newToken() {
  const token = bytesToBase64url(randomBytes(32));
  return { token, tokenHash: await sha256Hex(token) };
}

export function hashToken(token) {
  return sha256Hex(token);
}

export async function createSession(db, userId, userAgent, now) {
  const { token, tokenHash } = await newToken();
  const expiresAt = now + SESSION_TTL_MS;
  await db.prepare('INSERT INTO sessions (user_id, token_hash, created_at, expires_at, last_used_at, user_agent) VALUES (?, ?, ?, ?, ?, ?)')
    .bind(userId, tokenHash, now, expiresAt, now, String(userAgent || '').slice(0, 256)).run();
  return { token, expiresAt };
}

/** Resolve a bearer token to {session, user}; null when unknown, expired or the user is disabled. */
export async function lookupSession(db, token, now) {
  if (!token) return null;
  const tokenHash = await hashToken(token);
  const row = await db.prepare(
    'SELECT s.id AS session_id, s.expires_at, s.last_used_at, u.id AS user_id, u.username, u.display_name, u.role, u.disabled_at '
    + 'FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ?',
  ).bind(tokenHash).first();
  if (!row) return null;
  if (row.expires_at <= now || row.disabled_at) return null;
  if (!row.last_used_at || now - row.last_used_at >= LAST_USED_THROTTLE_MS) {
    await db.prepare('UPDATE sessions SET last_used_at = ? WHERE id = ?').bind(now, row.session_id).run();
  }
  return {
    session: { id: row.session_id, expiresAt: row.expires_at },
    user: { id: row.user_id, username: row.username, displayName: row.display_name, role: row.role },
  };
}

export async function deleteSessionByToken(db, token) {
  const tokenHash = await hashToken(token);
  await db.prepare('DELETE FROM sessions WHERE token_hash = ?').bind(tokenHash).run();
}

/** Throws 401 unless the request carries a valid session. */
export async function requireUser(request, env, now) {
  const token = bearerToken(request);
  const resolved = await lookupSession(env.DB, token, now);
  if (!resolved) throw new HttpError(401, 'unauthorized', 'login required');
  return resolved;
}

export async function requireAdmin(request, env, now) {
  const resolved = await requireUser(request, env, now);
  if (resolved.user.role !== 'admin') throw new HttpError(403, 'forbidden', 'admin only');
  return resolved;
}
