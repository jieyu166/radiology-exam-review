// Minimal D1-compatible shim over node:sqlite for unit tests (prepare/bind/first/all/run/batch).
import { DatabaseSync } from 'node:sqlite';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));

class Statement {
  constructor(db, sql, params = []) { this.db = db; this.sql = sql; this.params = params; }
  bind(...params) { return new Statement(this.db, this.sql, params.map(p => (p === undefined ? null : p))); }
  _prepared() { return this.db.raw.prepare(this.sql); }
  async first(column) {
    const row = this._prepared().get(...this.params) ?? null;
    if (row && column) return row[column];
    return row;
  }
  async all() { return { results: this._prepared().all(...this.params), success: true }; }
  async run() {
    const info = this._prepared().run(...this.params);
    return { success: true, meta: { changes: Number(info.changes), last_row_id: Number(info.lastInsertRowid) } };
  }
}

export class D1Stub {
  constructor() {
    this.raw = new DatabaseSync(':memory:');
    this.raw.exec('PRAGMA foreign_keys = ON');
  }
  prepare(sql) { return new Statement(this, sql); }
  async batch(statements) {
    this.raw.exec('BEGIN');
    try {
      const results = [];
      for (const statement of statements) results.push(await statement.run());
      this.raw.exec('COMMIT');
      return results;
    } catch (error) {
      this.raw.exec('ROLLBACK');
      throw error;
    }
  }
  exec(sql) { this.raw.exec(sql); }
}

export function migratedDb() {
  const db = new D1Stub();
  const dir = path.join(here, '..', 'migrations');
  for (const file of readdirSync(dir).filter(f => f.endsWith('.sql')).sort()) db.exec(readFileSync(path.join(dir, file), 'utf8'));
  return db;
}

export function makeEnv(overrides = {}) {
  return Object.assign({
    DB: migratedDb(),
    ALLOWED_ORIGINS: 'https://jieyu166.github.io,http://localhost:8777',
    ADMIN_USERNAMES: 'boss',
    BOOTSTRAP_INVITE_CODE: 'BOOTSTRAPBOOTSTRAPBOOT22',
    LOGIN_LIMITER: { limit: async () => ({ success: true }) },
  }, overrides);
}

export async function call(worker, env, method, pathname, { body, token, origin } = {}) {
  const headers = { Origin: origin || 'https://jieyu166.github.io' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (token) headers.Authorization = `Bearer ${token}`;
  const request = new Request(`https://rex-api.test${pathname}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  const response = await worker.fetch(request, env, {});
  const text = await response.text();
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch (e) { json = { raw: text }; }
  return { status: response.status, body: json, headers: response.headers };
}
