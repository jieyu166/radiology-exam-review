// /sync/* routes: append-only attempts, last-write-wins bookmarks, append-only exam results, snapshot.

import { json, readJson, HttpError } from './http.js';
import { requireUser } from './session.js';
import { validateAttempt, validateBookmark, validateExam, validateBatch } from './attempts.js';
import { uploadCards, uploadReviewLogs, uploadSettings, fsrsSnapshot } from './fsrs-sync.js';

function changes(result) {
  return result && result.meta && Number.isFinite(result.meta.changes) ? result.meta.changes : 0;
}

export async function uploadAttempts(db, userId, items, now) {
  const batch = validateBatch(items, validateAttempt);
  if (!batch.ok) throw new HttpError(400, 'invalid_items', 'one or more items are invalid', { errors: batch.errors });
  if (!batch.values.length) return { accepted: 0, ignored: 0, acceptedIds: [] };
  const statements = batch.values.map(v => db.prepare(
    'INSERT OR IGNORE INTO attempts (user_id, client_id, question_id, chosen, is_correct, source, elapsed_ms, confidence, source_sha256, client_ts, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
  ).bind(userId, v.clientId, v.questionId, v.chosen, v.isCorrect, v.source, v.elapsedMs, v.confidence, v.sourceSha256, v.clientTs, now));
  const results = await db.batch(statements);
  const accepted = results.reduce((sum, r) => sum + changes(r), 0);
  return { accepted, ignored: batch.values.length - accepted, acceptedIds: batch.values.map(v => v.clientId) };
}

export async function uploadBookmarks(db, userId, items, now) {
  const batch = validateBatch(items, validateBookmark);
  if (!batch.ok) throw new HttpError(400, 'invalid_items', 'one or more items are invalid', { errors: batch.errors });
  if (!batch.values.length) return { accepted: 0, ignored: 0, acceptedIds: [] };
  const statements = batch.values.map(v => db.prepare(
    'INSERT INTO bookmarks (user_id, question_id, starred, updated_at) VALUES (?, ?, ?, ?) '
    + 'ON CONFLICT(user_id, question_id) DO UPDATE SET starred = excluded.starred, updated_at = excluded.updated_at WHERE excluded.updated_at > bookmarks.updated_at',
  ).bind(userId, v.questionId, v.starred, v.updatedAt));
  const results = await db.batch(statements);
  const accepted = results.reduce((sum, r) => sum + changes(r), 0);
  return { accepted, ignored: batch.values.length - accepted, acceptedIds: batch.values.map(v => v.questionId) };
}

export async function uploadExams(db, userId, items, now) {
  const batch = validateBatch(items, validateExam);
  if (!batch.ok) throw new HttpError(400, 'invalid_items', 'one or more items are invalid', { errors: batch.errors });
  if (!batch.values.length) return { accepted: 0, ignored: 0, acceptedIds: [] };
  const statements = batch.values.map(v => db.prepare(
    'INSERT OR IGNORE INTO exam_results (user_id, client_id, total, correct, wrong, skipped, pct, wrong_ids, source_sha256_by_question, client_ts, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
  ).bind(userId, v.clientId, v.total, v.correct, v.wrong, v.skipped, v.pct, JSON.stringify(v.wrongIds), JSON.stringify(v.sourceSha256ByQuestion), v.clientTs, now));
  const results = await db.batch(statements);
  const accepted = results.reduce((sum, r) => sum + changes(r), 0);
  return { accepted, ignored: batch.values.length - accepted, acceptedIds: batch.values.map(v => v.clientId) };
}

function parseJsonField(text, fallback) {
  try { return JSON.parse(text); } catch (e) { return fallback; }
}

export async function snapshot(db, userId, sinceAttemptId) {
  const since = Number.isFinite(sinceAttemptId) && sinceAttemptId > 0 ? Math.trunc(sinceAttemptId) : 0;
  const attempts = (await db.prepare(
    'SELECT id, client_id, question_id, chosen, is_correct, source, elapsed_ms, confidence, source_sha256, client_ts FROM attempts WHERE user_id = ? AND id > ? ORDER BY id',
  ).bind(userId, since).all()).results.map(row => ({
    id: row.id,
    clientId: row.client_id,
    questionId: row.question_id,
    chosen: row.chosen,
    isCorrect: row.is_correct == null ? null : row.is_correct === 1,
    source: row.source,
    elapsedMs: row.elapsed_ms,
    confidence: row.confidence,
    sourceSha256: row.source_sha256,
    clientTs: row.client_ts,
  }));
  const bookmarks = (await db.prepare('SELECT question_id, starred, updated_at FROM bookmarks WHERE user_id = ?').bind(userId).all()).results
    .map(row => ({ questionId: row.question_id, starred: row.starred === 1, updatedAt: row.updated_at }));
  const exams = (await db.prepare(
    'SELECT client_id, total, correct, wrong, skipped, pct, wrong_ids, source_sha256_by_question, client_ts FROM exam_results WHERE user_id = ? ORDER BY client_ts DESC',
  ).bind(userId).all()).results.map(row => ({
    clientId: row.client_id,
    total: row.total,
    correct: row.correct,
    wrong: row.wrong,
    skipped: row.skipped,
    pct: row.pct,
    wrongIds: parseJsonField(row.wrong_ids, []),
    sourceSha256ByQuestion: parseJsonField(row.source_sha256_by_question, {}),
    ts: row.client_ts,
    clientTs: row.client_ts,
  }));
  const latest = await db.prepare('SELECT COALESCE(MAX(id), 0) AS latest FROM attempts WHERE user_id = ?').bind(userId).first();
  return { attempts, bookmarks, exams, latestAttemptId: latest ? Number(latest.latest) : 0 };
}

const UPLOADERS = {
  '/sync/attempts': uploadAttempts,
  '/sync/bookmarks': uploadBookmarks,
  '/sync/exams': uploadExams,
  '/sync/cards': uploadCards,
  '/sync/review-logs': uploadReviewLogs,
  '/sync/settings': uploadSettings,
};

export async function routeSync(request, env, ctx, { path, url, cors }) {
  const now = Date.now();
  const { user } = await requireUser(request, env, now);
  if (request.method === 'POST' && UPLOADERS[path]) {
    const body = await readJson(request);
    const result = await UPLOADERS[path](env.DB, user.id, body.items, now);
    return json(200, result, cors);
  }
  if (path === '/sync/snapshot' && request.method === 'GET') {
    const since = Number(url.searchParams.get('sinceAttemptId') || 0);
    const sinceLog = Number(url.searchParams.get('sinceReviewLogId') || 0);
    const [base, fsrs] = await Promise.all([snapshot(env.DB, user.id, since), fsrsSnapshot(env.DB, user.id, sinceLog)]);
    return json(200, Object.assign({}, base, fsrs), cors);
  }
  throw new HttpError(404, 'not_found', `no route for ${request.method} ${path}`);
}
