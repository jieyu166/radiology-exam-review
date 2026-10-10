import test from 'node:test';
import assert from 'node:assert/strict';
import { hashPassword, verifyPassword, parsePhc, formatPhc, PBKDF2_ITERATIONS, PBKDF2_MAX_ITERATIONS, isValidPassword } from '../src/password.js';

test('hash produces a PHC string that round-trips through parsePhc', async () => {
  const phc = await hashPassword('correct horse battery');
  assert.match(phc, /^\$pbkdf2-sha256\$i=\d+\$[A-Za-z0-9_-]+\$[A-Za-z0-9_-]+$/);
  const parsed = parsePhc(phc);
  assert.equal(parsed.iterations, PBKDF2_ITERATIONS);
  assert.equal(parsed.salt.length, 16);
  assert.equal(parsed.hash.length, 32);
  assert.equal(formatPhc(parsed.iterations, parsed.salt, parsed.hash), phc);
});

test('verify accepts the right password and rejects a wrong one', async () => {
  const phc = await hashPassword('correct horse battery');
  assert.deepEqual(await verifyPassword('correct horse battery', phc), { ok: true, needsRehash: false });
  assert.deepEqual(await verifyPassword('wrong password', phc), { ok: false, needsRehash: false });
  assert.deepEqual(await verifyPassword('correct horse battery', 'not-a-phc'), { ok: false, needsRehash: false });
});

test('lower stored iteration count flags needsRehash only on success', async () => {
  const phc = await hashPassword('correct horse battery', 50000);
  assert.equal(parsePhc(phc).iterations, 50000);
  assert.deepEqual(await verifyPassword('correct horse battery', phc, 100000), { ok: true, needsRehash: true });
  assert.deepEqual(await verifyPassword('nope', phc, 100000), { ok: false, needsRehash: false });
});

test('iteration constant never exceeds the workerd hard limit', async () => {
  assert.ok(PBKDF2_ITERATIONS <= PBKDF2_MAX_ITERATIONS && PBKDF2_MAX_ITERATIONS === 100000);
  const phc = await hashPassword('correct horse battery', 5000000);
  assert.equal(parsePhc(phc).iterations, 100000);
});

test('password length policy', () => {
  assert.equal(isValidPassword('1234567'), false);
  assert.equal(isValidPassword('12345678'), true);
  assert.equal(isValidPassword('x'.repeat(129)), false);
});
