// FSRS scheduler sync: cards (last-write-wins by updated_at), review logs (append-only by client_id),
// per-user scheduler settings (last-write-wins). Mounted under /sync/* by sync.js.

import { HttpError } from './http.js';
import { validateBatch } from './attempts.js';

const RATINGS = ['again', 'hard', 'good', 'easy'];

function num(value, fallback = 0) {
  return Number.isFinite(value) ? value : fallback;
}

function isId(value) {
  return typeof value === 'string' && value.length > 0 && value.length <= 128;
}

export function validateCard(raw) {
  if (!raw || typeof raw !== 'object') return { ok: false, errors: ['not an object'] };
  const errors = [];
  if (!isId(raw.questionId)) errors.push('questionId must be a non-empty string');
  if (!Number.isFinite(raw.dueAt)) errors.push('dueAt must be a number');
  if (!Number.isFinite(raw.updatedAt)) errors.push('updatedAt must be a number');
  if (![0, 1, 2, 3].includes(raw.state)) errors.push('state must be 0-3');
  if (errors.length) return { ok: false, errors };
  return {
    ok: true,
    value: {
      questionId: raw.questionId,
      dueAt: Math.trunc(raw.dueAt),
      stability: num(raw.stability),
      difficulty: num(raw.difficulty),
      elapsedDays: Math.trunc(num(raw.elapsedDays)),
      scheduledDays: Math.trunc(num(raw.scheduledDays)),
      learningSteps: Math.trunc(num(raw.learningSteps)),
      reps: Math.trunc(num(raw.reps)),
      lapses: Math.trunc(num(raw.lapses)),
      state: raw.state,
      lastReviewAt: Number.isFinite(raw.lastReviewAt) ? Math.trunc(raw.lastReviewAt) : null,
      updatedAt: Math.trunc(raw.updatedAt),
    },
  };
}

export function validateReviewLog(raw) {
  if (!raw || typeof raw !== 'object') return { ok: false, errors: ['not an object'] };
  const errors = [];
  if (!isId(raw.clientId)) errors.push('clientId must be a non-empty string');
  if (!isId(raw.questionId)) errors.push('questionId must be a non-empty string');
  if (!RATINGS.includes(raw.rating)) errors.push('rating must be again|hard|good|easy');
  if (![0, 1, 2, 3].includes(raw.state)) errors.push('state must be 0-3');
  if (!Number.isFinite(raw.reviewedAt)) errors.push('reviewedAt must be a number');
  if (errors.length) return { ok: false, errors };
  return {
    ok: true,
    value: {
      clientId: raw.clientId,
      questionId: raw.questionId,
      rating: raw.rating,
      state: raw.state,
      dueAt: Math.trunc(num(raw.dueAt)),
      stability: num(raw.stability),
      difficulty: num(raw.difficulty),
      elapsedDays: Math.trunc(num(raw.elapsedDays)),
      lastElapsedDays: Math.trunc(num(raw.lastElapsedDays)),
      scheduledDays: Math.trunc(num(raw.scheduledDays)),
      learningSteps: Math.trunc(num(raw.learningSteps)),
      reviewedAt: Math.trunc(raw.reviewedAt),
    },
  };
}

export function validateSettings(raw) {
  if (!raw || typeof raw !== 'object') return { ok: false, errors: ['not an object'] };
  if (!Number.isFinite(raw.updatedAt)) return { ok: false, errors: ['updatedAt must be a number'] };
  const clamp = (v, lo, hi, d) => (Number.isFinite(v) ? Math.min(hi, Math.max(lo, Math.trunc(v))) : d);
  return {
    ok: true,
    value: {
      newPerDay: clamp(raw.newPerDay, 0, 200, 20),
      dayStartHour: clamp(raw.dayStartHour, 0, 23, 4),
      examSecondsPerQuestion: clamp(raw.examSecondsPerQuestion, 0, 600, 90),
      updatedAt: Math.trunc(raw.updatedAt),
    },
  };
}

function changes(result) {
  return result && result.meta && Number.isFinite(result.meta.changes) ? result.meta.changes : 0;
}

export async function uploadCards(db, userId, items) {
  const batch = validateBatch(items, validateCard);
  if (!batch.ok) throw new HttpError(400, 'invalid_items', 'one or more items are invalid', { errors: batch.errors });
  if (!batch.values.length) return { accepted: 0, ignored: 0, acceptedIds: [] };
  const statements = batch.values.map(v => db.prepare(
    'INSERT INTO fsrs_cards (user_id, question_id, due_at, stability, difficulty, elapsed_days, scheduled_days, learning_steps, reps, lapses, state, last_review_at, updated_at) '
    + 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(user_id, question_id) DO UPDATE SET '
    + 'due_at = excluded.due_at, stability = excluded.stability, difficulty = excluded.difficulty, elapsed_days = excluded.elapsed_days, '
    + 'scheduled_days = excluded.scheduled_days, learning_steps = excluded.learning_steps, reps = excluded.reps, lapses = excluded.lapses, '
    + 'state = excluded.state, last_review_at = excluded.last_review_at, updated_at = excluded.updated_at WHERE excluded.updated_at > fsrs_cards.updated_at',
  ).bind(userId, v.questionId, v.dueAt, v.stability, v.difficulty, v.elapsedDays, v.scheduledDays, v.learningSteps, v.reps, v.lapses, v.state, v.lastReviewAt, v.updatedAt));
  const results = await db.batch(statements);
  const accepted = results.reduce((sum, r) => sum + changes(r), 0);
  return { accepted, ignored: batch.values.length - accepted, acceptedIds: batch.values.map(v => v.questionId) };
}

export async function uploadReviewLogs(db, userId, items, now) {
  const batch = validateBatch(items, validateReviewLog);
  if (!batch.ok) throw new HttpError(400, 'invalid_items', 'one or more items are invalid', { errors: batch.errors });
  if (!batch.values.length) return { accepted: 0, ignored: 0, acceptedIds: [] };
  const statements = batch.values.map(v => db.prepare(
    'INSERT OR IGNORE INTO fsrs_review_logs (user_id, client_id, question_id, rating, state, due_at, stability, difficulty, elapsed_days, last_elapsed_days, scheduled_days, learning_steps, reviewed_at, created_at) '
    + 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
  ).bind(userId, v.clientId, v.questionId, v.rating, v.state, v.dueAt, v.stability, v.difficulty, v.elapsedDays, v.lastElapsedDays, v.scheduledDays, v.learningSteps, v.reviewedAt, now));
  const results = await db.batch(statements);
  const accepted = results.reduce((sum, r) => sum + changes(r), 0);
  return { accepted, ignored: batch.values.length - accepted, acceptedIds: batch.values.map(v => v.clientId) };
}

export async function uploadSettings(db, userId, items) {
  const list = Array.isArray(items) ? items : [items];
  const latest = list.map(validateSettings).filter(r => r.ok).map(r => r.value).sort((a, b) => b.updatedAt - a.updatedAt)[0];
  if (!latest) throw new HttpError(400, 'invalid_items', 'settings item invalid', { errors: [{ index: 0, reason: 'updatedAt required' }] });
  const result = await db.prepare(
    'INSERT INTO user_settings (user_id, new_per_day, day_start_hour, exam_seconds_per_question, updated_at) VALUES (?, ?, ?, ?, ?) '
    + 'ON CONFLICT(user_id) DO UPDATE SET new_per_day = excluded.new_per_day, day_start_hour = excluded.day_start_hour, '
    + 'exam_seconds_per_question = excluded.exam_seconds_per_question, updated_at = excluded.updated_at WHERE excluded.updated_at > user_settings.updated_at',
  ).bind(userId, latest.newPerDay, latest.dayStartHour, latest.examSecondsPerQuestion, latest.updatedAt).run();
  return { accepted: changes(result), ignored: changes(result) ? 0 : 1, acceptedIds: [latest.updatedAt] };
}

export async function fsrsSnapshot(db, userId, sinceReviewLogId) {
  const since = Number.isFinite(sinceReviewLogId) && sinceReviewLogId > 0 ? Math.trunc(sinceReviewLogId) : 0;
  const cards = (await db.prepare('SELECT * FROM fsrs_cards WHERE user_id = ?').bind(userId).all()).results.map(r => ({
    questionId: r.question_id, dueAt: r.due_at, stability: r.stability, difficulty: r.difficulty, elapsedDays: r.elapsed_days,
    scheduledDays: r.scheduled_days, learningSteps: r.learning_steps, reps: r.reps, lapses: r.lapses, state: r.state,
    lastReviewAt: r.last_review_at, updatedAt: r.updated_at,
  }));
  const reviewLogs = (await db.prepare('SELECT * FROM fsrs_review_logs WHERE user_id = ? AND id > ? ORDER BY id').bind(userId, since).all()).results.map(r => ({
    id: r.id, clientId: r.client_id, questionId: r.question_id, rating: r.rating, state: r.state, dueAt: r.due_at, stability: r.stability,
    difficulty: r.difficulty, elapsedDays: r.elapsed_days, lastElapsedDays: r.last_elapsed_days, scheduledDays: r.scheduled_days,
    learningSteps: r.learning_steps, reviewedAt: r.reviewed_at,
  }));
  const settingsRow = await db.prepare('SELECT * FROM user_settings WHERE user_id = ?').bind(userId).first();
  const settings = settingsRow ? { newPerDay: settingsRow.new_per_day, dayStartHour: settingsRow.day_start_hour, examSecondsPerQuestion: settingsRow.exam_seconds_per_question, updatedAt: settingsRow.updated_at } : null;
  const latest = await db.prepare('SELECT COALESCE(MAX(id), 0) AS latest FROM fsrs_review_logs WHERE user_id = ?').bind(userId).first();
  return { cards, reviewLogs, settings, latestReviewLogId: latest ? Number(latest.latest) : 0 };
}
