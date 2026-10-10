// Invite codes: 24-char base32, stored as SHA-256 hex, single use, expiring.

import { randomBase32, sha256Hex } from './util.js';

export const INVITE_CODE_LENGTH = 24;
export const DEFAULT_INVITE_DAYS = 14;
const DAY_MS = 24 * 60 * 60 * 1000;

export function normalizeInviteCode(raw) {
  return String(raw == null ? '' : raw).trim().toUpperCase().replace(/[^A-Z2-7]/g, '');
}

export async function createInvite(db, { createdBy, note, expiresInDays, now }) {
  const code = randomBase32(INVITE_CODE_LENGTH);
  const days = Number.isFinite(expiresInDays) && expiresInDays > 0 ? Math.min(365, Math.trunc(expiresInDays)) : DEFAULT_INVITE_DAYS;
  const expiresAt = now + days * DAY_MS;
  const result = await db.prepare('INSERT INTO invites (code_hash, note, created_by, created_at, expires_at) VALUES (?, ?, ?, ?, ?)')
    .bind(await sha256Hex(code), String(note || '').slice(0, 200), createdBy || null, now, expiresAt).run();
  const id = result && result.meta && result.meta.last_row_id != null ? result.meta.last_row_id : null;
  return { id, code, expiresAt };
}

/** Returns the invite row when the code is unused, unrevoked and unexpired; otherwise null. */
export async function findValidInvite(db, code, now) {
  const normalized = normalizeInviteCode(code);
  if (normalized.length !== INVITE_CODE_LENGTH) return null;
  const row = await db.prepare('SELECT id, note, created_by, expires_at, used_by, revoked_at FROM invites WHERE code_hash = ?')
    .bind(await sha256Hex(normalized)).first();
  if (!row) return null;
  if (row.used_by || row.revoked_at || row.expires_at <= now) return null;
  return row;
}

export function inviteStatus(row, now) {
  if (row.used_by) return 'used';
  if (row.revoked_at) return 'revoked';
  if (row.expires_at <= now) return 'expired';
  return 'active';
}

export async function listInvites(db, now) {
  const { results } = await db.prepare(
    'SELECT i.id, i.note, i.created_at, i.expires_at, i.used_at, i.revoked_at, i.used_by, c.username AS created_by_username, u.username AS used_by_username '
    + 'FROM invites i LEFT JOIN users c ON c.id = i.created_by LEFT JOIN users u ON u.id = i.used_by ORDER BY i.id DESC',
  ).all();
  return results.map(row => ({
    id: row.id,
    note: row.note,
    status: inviteStatus(row, now),
    createdAt: row.created_at,
    expiresAt: row.expires_at,
    usedAt: row.used_at,
    revokedAt: row.revoked_at,
    createdBy: row.created_by_username,
    usedBy: row.used_by_username,
  }));
}

export async function revokeInvite(db, id, now) {
  const result = await db.prepare('UPDATE invites SET revoked_at = ? WHERE id = ? AND used_by IS NULL AND revoked_at IS NULL').bind(now, id).run();
  return !!(result && result.meta && result.meta.changes);
}
