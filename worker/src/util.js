// Shared pure helpers (no D1, no Request).

const encoder = new TextEncoder();

export async function sha256Hex(text) {
  const digest = await crypto.subtle.digest('SHA-256', encoder.encode(String(text)));
  return bytesToHex(new Uint8Array(digest));
}

export function bytesToHex(bytes) {
  return Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
}

export function bytesToBase64url(bytes) {
  let binary = '';
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export function base64urlToBytes(text) {
  const normalized = String(text).replace(/-/g, '+').replace(/_/g, '/');
  const padded = normalized + '='.repeat((4 - normalized.length % 4) % 4);
  const binary = atob(padded);
  return Uint8Array.from(binary, c => c.charCodeAt(0));
}

export function randomBytes(length) {
  const out = new Uint8Array(length);
  crypto.getRandomValues(out);
  return out;
}

const BASE32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
export function randomBase32(length) {
  const bytes = randomBytes(length);
  let out = '';
  for (const b of bytes) out += BASE32[b % 32];
  return out;
}

/** Constant-time comparison of two equal-length byte arrays. */
export function timingSafeEqual(a, b) {
  if (crypto.subtle && typeof crypto.subtle.timingSafeEqual === 'function') {
    if (a.byteLength !== b.byteLength) return false;
    return crypto.subtle.timingSafeEqual(a, b);
  }
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

export const USERNAME_RE = /^[a-z0-9][a-z0-9_.-]{2,31}$/;

export function normalizeUsername(raw) {
  return String(raw == null ? '' : raw).trim().toLowerCase();
}

export function isValidUsername(username) {
  return USERNAME_RE.test(username);
}

export function parseList(raw) {
  return String(raw || '').split(',').map(item => item.trim().toLowerCase()).filter(Boolean);
}
