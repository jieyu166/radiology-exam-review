// Password hashing: WebCrypto PBKDF2-HMAC-SHA256, PHC string, transparent iteration upgrades.
// workerd caps PBKDF2 at 100,000 iterations; keep PBKDF2_ITERATIONS at or below that.

import { randomBytes, bytesToBase64url, base64urlToBytes, timingSafeEqual } from './util.js';

export const PBKDF2_ITERATIONS = 100000;
export const PBKDF2_MAX_ITERATIONS = 100000;
export const SALT_BYTES = 16;
export const HASH_BYTES = 32;
export const PASSWORD_MIN = 8;
export const PASSWORD_MAX = 128;

const encoder = new TextEncoder();

async function derive(password, salt, iterations) {
  const key = await crypto.subtle.importKey('raw', encoder.encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations }, key, HASH_BYTES * 8);
  return new Uint8Array(bits);
}

export function isValidPassword(password) {
  return typeof password === 'string' && password.length >= PASSWORD_MIN && password.length <= PASSWORD_MAX;
}

export function formatPhc(iterations, salt, hash) {
  return `$pbkdf2-sha256$i=${iterations}$${bytesToBase64url(salt)}$${bytesToBase64url(hash)}`;
}

export function parsePhc(phc) {
  const match = /^\$pbkdf2-sha256\$i=(\d+)\$([A-Za-z0-9_-]+)\$([A-Za-z0-9_-]+)$/.exec(String(phc || ''));
  if (!match) return null;
  const iterations = Number(match[1]);
  if (!Number.isInteger(iterations) || iterations < 1) return null;
  return { iterations, salt: base64urlToBytes(match[2]), hash: base64urlToBytes(match[3]) };
}

export async function hashPassword(password, iterations = PBKDF2_ITERATIONS) {
  const rounds = Math.min(Math.max(1, Math.trunc(iterations)), PBKDF2_MAX_ITERATIONS);
  const salt = randomBytes(SALT_BYTES);
  const hash = await derive(password, salt, rounds);
  return formatPhc(rounds, salt, hash);
}

/** @returns {Promise<{ok: boolean, needsRehash: boolean}>} */
export async function verifyPassword(password, phc, currentIterations = PBKDF2_ITERATIONS) {
  const parsed = parsePhc(phc);
  if (!parsed || typeof password !== 'string') return { ok: false, needsRehash: false };
  const candidate = await derive(password, parsed.salt, parsed.iterations);
  const ok = timingSafeEqual(candidate, parsed.hash);
  return { ok, needsRehash: ok && parsed.iterations < Math.min(currentIterations, PBKDF2_MAX_ITERATIONS) };
}
