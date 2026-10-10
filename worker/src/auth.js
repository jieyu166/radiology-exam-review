// /auth/* routes: invite-only registration, login with throttling + lockout, logout, me.

import { json, readJson, HttpError, bearerToken } from './http.js';
import { hashPassword, verifyPassword, isValidPassword, PBKDF2_ITERATIONS, PASSWORD_MIN, PASSWORD_MAX } from './password.js';
import { createSession, lookupSession, deleteSessionByToken, requireUser } from './session.js';
import { findValidInvite, normalizeInviteCode } from './invites.js';
import { normalizeUsername, isValidUsername, parseList } from './util.js';

export const MAX_FAILURES = 5;
export const LOCK_MS = 15 * 60 * 1000;
const AUTH_FAILED = 'account or password incorrect';

export function roleFor(username, env) {
  return parseList(env.ADMIN_USERNAMES).includes(username) ? 'admin' : 'member';
}

/** Iteration count: env PBKDF2_ITERATIONS (tuned per plan CPU budget) or the code default; never above the workerd cap. */
export function iterationsFor(env) {
  const raw = Number(env && env.PBKDF2_ITERATIONS);
  return Number.isFinite(raw) && raw >= 1000 ? Math.trunc(raw) : PBKDF2_ITERATIONS;
}

function publicUser(row) {
  return { id: row.id, username: row.username, displayName: row.display_name, role: row.role };
}

async function userCount(db) {
  const row = await db.prepare('SELECT COUNT(*) AS n FROM users').first();
  return row ? Number(row.n) : 0;
}

/** Registration: invite required; BOOTSTRAP_INVITE_CODE accepted only while the users table is empty. */
export async function register(env, body, meta) {
  const now = meta.now;
  const username = normalizeUsername(body.username);
  if (!isValidUsername(username)) throw new HttpError(400, 'invalid_username', 'username must match ^[a-z0-9][a-z0-9_.-]{2,31}$');
  if (!isValidPassword(body.password)) throw new HttpError(400, 'invalid_password', `password must be ${PASSWORD_MIN}-${PASSWORD_MAX} characters`);
  const displayName = String(body.displayName || '').trim().slice(0, 64);

  const inviteCode = normalizeInviteCode(body.inviteCode);
  let invite = await findValidInvite(env.DB, inviteCode, now);
  let bootstrap = false;
  if (!invite) {
    const bootstrapCode = normalizeInviteCode(env.BOOTSTRAP_INVITE_CODE);
    if (bootstrapCode && inviteCode && inviteCode === bootstrapCode && (await userCount(env.DB)) === 0) bootstrap = true;
    else throw new HttpError(400, 'invite_invalid', 'invite code is invalid, used, revoked or expired');
  }
  const existing = await env.DB.prepare('SELECT id FROM users WHERE username = ?').bind(username).first();
  if (existing) throw new HttpError(409, 'username_taken', 'username already exists');

  const passwordHash = await hashPassword(body.password, iterationsFor(env));
  const role = roleFor(username, env);
  const statements = [
    env.DB.prepare('INSERT INTO users (username, display_name, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)').bind(username, displayName || username, passwordHash, role, now),
  ];
  if (invite) {
    statements.push(env.DB.prepare('UPDATE invites SET used_by = (SELECT id FROM users WHERE username = ?), used_at = ? WHERE id = ? AND used_by IS NULL').bind(username, now, invite.id));
  }
  await env.DB.batch(statements);
  const created = await env.DB.prepare('SELECT id, username, display_name, role FROM users WHERE username = ?').bind(username).first();
  if (invite) {
    const check = await env.DB.prepare('SELECT used_by FROM invites WHERE id = ?').bind(invite.id).first();
    if (!check || check.used_by !== created.id) throw new HttpError(409, 'invite_race', 'invite was used concurrently');
  }
  const session = await createSession(env.DB, created.id, meta.userAgent, now);
  return { status: 201, body: { token: session.token, expiresAt: session.expiresAt, user: publicUser(created), bootstrap } };
}

async function lockState(db, username, now) {
  const row = await db.prepare('SELECT failed_count, locked_until FROM login_attempts WHERE username = ?').bind(username).first();
  if (!row) return { failedCount: 0, lockedUntil: null, locked: false };
  const locked = !!row.locked_until && row.locked_until > now;
  return { failedCount: row.failed_count, lockedUntil: row.locked_until, locked };
}

async function recordFailure(db, username, now) {
  const state = await lockState(db, username, now);
  const failedCount = (state.lockedUntil && state.lockedUntil <= now ? 0 : state.failedCount) + 1;
  const lockedUntil = failedCount >= MAX_FAILURES ? now + LOCK_MS : null;
  await db.prepare('INSERT INTO login_attempts (username, failed_count, locked_until, updated_at) VALUES (?, ?, ?, ?) '
    + 'ON CONFLICT(username) DO UPDATE SET failed_count = excluded.failed_count, locked_until = excluded.locked_until, updated_at = excluded.updated_at')
    .bind(username, failedCount, lockedUntil, now).run();
}

async function clearFailures(db, username, now) {
  await db.prepare('INSERT INTO login_attempts (username, failed_count, locked_until, updated_at) VALUES (?, 0, NULL, ?) '
    + 'ON CONFLICT(username) DO UPDATE SET failed_count = 0, locked_until = NULL, updated_at = excluded.updated_at').bind(username, now).run();
}

export async function login(env, body, meta) {
  const now = meta.now;
  const username = normalizeUsername(body.username);
  const password = typeof body.password === 'string' ? body.password : '';
  if (!username) throw new HttpError(401, 'auth_failed', AUTH_FAILED);

  if (env.LOGIN_LIMITER && typeof env.LOGIN_LIMITER.limit === 'function') {
    const { success } = await env.LOGIN_LIMITER.limit({ key: username });
    if (!success) throw new HttpError(429, 'rate_limited', 'too many login attempts, slow down');
  }
  const state = await lockState(env.DB, username, now);
  if (state.locked) throw new HttpError(423, 'locked', 'account temporarily locked', { retryAfterSeconds: Math.ceil((state.lockedUntil - now) / 1000) });

  const user = await env.DB.prepare('SELECT id, username, display_name, password_hash, role, disabled_at FROM users WHERE username = ?').bind(username).first();
  const iterations = iterationsFor(env);
  const verified = user ? await verifyPassword(password, user.password_hash, iterations) : { ok: false, needsRehash: false };
  if (!user || !verified.ok || user.disabled_at) {
    await recordFailure(env.DB, username, now);
    throw new HttpError(401, 'auth_failed', AUTH_FAILED);
  }
  await clearFailures(env.DB, username, now);
  const role = roleFor(username, env);
  const updates = [];
  if (verified.needsRehash) updates.push(env.DB.prepare('UPDATE users SET password_hash = ? WHERE id = ?').bind(await hashPassword(password, iterations), user.id));
  if (role !== user.role) updates.push(env.DB.prepare('UPDATE users SET role = ? WHERE id = ?').bind(role, user.id));
  if (updates.length) await env.DB.batch(updates);
  const session = await createSession(env.DB, user.id, meta.userAgent, now);
  return { status: 200, body: { token: session.token, expiresAt: session.expiresAt, user: publicUser(Object.assign({}, user, { role })) } };
}

export async function routeAuth(request, env, ctx, { path, cors }) {
  const now = Date.now();
  const meta = { now, userAgent: request.headers.get('User-Agent') || '' };
  if (path === '/auth/register' && request.method === 'POST') {
    const result = await register(env, await readJson(request), meta);
    return json(result.status, result.body, cors);
  }
  if (path === '/auth/login' && request.method === 'POST') {
    const result = await login(env, await readJson(request), meta);
    return json(result.status, result.body, cors);
  }
  if (path === '/auth/logout' && request.method === 'POST') {
    const token = bearerToken(request);
    if (token) await deleteSessionByToken(env.DB, token);
    return json(200, { ok: true }, cors);
  }
  if (path === '/auth/me' && request.method === 'GET') {
    const resolved = await requireUser(request, env, now);
    return json(200, { user: resolved.user, session: resolved.session }, cors);
  }
  throw new HttpError(404, 'not_found', `no route for ${request.method} ${path}`);
}

export { lookupSession };
