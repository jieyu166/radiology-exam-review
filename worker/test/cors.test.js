import test from 'node:test';
import assert from 'node:assert/strict';
import { corsHeaders, parseAllowedOrigins, isAllowedOrigin } from '../src/cors.js';

const ALLOWED = 'https://jieyu166.github.io, http://localhost:8777/';

test('allowed origin echoes origin with full allow headers', () => {
  const headers = corsHeaders('https://jieyu166.github.io', ALLOWED);
  assert.equal(headers['Access-Control-Allow-Origin'], 'https://jieyu166.github.io');
  assert.equal(headers.Vary, 'Origin');
  assert.equal(headers['Access-Control-Allow-Methods'], 'GET, POST, DELETE, OPTIONS');
  assert.equal(headers['Access-Control-Allow-Headers'], 'Content-Type, Authorization');
  assert.equal(headers['Access-Control-Max-Age'], '7200');
  assert.ok(!('Access-Control-Allow-Credentials' in headers), 'bearer scheme never needs credentials');
});

test('unlisted origin gets no allow headers', () => {
  const headers = corsHeaders('https://evil.example', ALLOWED);
  assert.deepEqual(headers, { Vary: 'Origin' });
  assert.equal(isAllowedOrigin('https://evil.example', ALLOWED), false);
});

test('missing origin (same-origin or curl) gets no allow headers but no error', () => {
  assert.deepEqual(corsHeaders(null, ALLOWED), { Vary: 'Origin' });
});

test('origins are trimmed and trailing slashes ignored', () => {
  assert.deepEqual(parseAllowedOrigins(ALLOWED), ['https://jieyu166.github.io', 'http://localhost:8777']);
  assert.equal(isAllowedOrigin('http://localhost:8777', ALLOWED), true);
});
