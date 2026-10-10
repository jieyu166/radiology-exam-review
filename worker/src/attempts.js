// Validation for sync payloads. Pure functions.
// clampElapsedMs follows mcq-bank (MIT) worker/lib/attempts.ts with a 30-minute ceiling.

export const MAX_ELAPSED_MS = 30 * 60 * 1000;
export const MAX_BATCH = 40;
export const LETTERS = ['A', 'B', 'C', 'D', 'E'];
export const SOURCES = ['card', 'exam', 'legacy'];

export function clampElapsedMs(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return null;
  return Math.min(Math.max(Math.trunc(value), 0), MAX_ELAPSED_MS);
}

function isId(value) {
  return typeof value === 'string' && value.length > 0 && value.length <= 128;
}

export function validateAttempt(raw) {
  const errors = [];
  if (!raw || typeof raw !== 'object') return { ok: false, errors: ['not an object'] };
  if (!isId(raw.clientId)) errors.push('clientId must be a non-empty string (<=128)');
  if (!isId(raw.questionId)) errors.push('questionId must be a non-empty string');
  const chosen = raw.chosen == null ? null : String(raw.chosen).toUpperCase();
  if (chosen !== null && !LETTERS.includes(chosen)) errors.push('chosen must be A-E or null');
  if (!(raw.isCorrect === true || raw.isCorrect === false || raw.isCorrect == null)) errors.push('isCorrect must be boolean or null');
  if (!SOURCES.includes(raw.source)) errors.push('source must be card, exam or legacy');
  if (!(raw.confidence == null || [1, 2, 3].includes(raw.confidence))) errors.push('confidence must be 1, 2, 3 or null');
  if (raw.sourceSha256 != null && typeof raw.sourceSha256 !== 'string') errors.push('sourceSha256 must be a string or null');
  if (!Number.isFinite(raw.clientTs)) errors.push('clientTs must be a number');
  if (errors.length) return { ok: false, errors };
  return {
    ok: true,
    value: {
      clientId: raw.clientId,
      questionId: raw.questionId,
      chosen,
      isCorrect: raw.isCorrect == null ? null : (raw.isCorrect ? 1 : 0),
      source: raw.source,
      elapsedMs: clampElapsedMs(raw.elapsedMs),
      confidence: raw.confidence == null ? null : raw.confidence,
      sourceSha256: raw.sourceSha256 == null ? null : raw.sourceSha256,
      clientTs: Math.trunc(raw.clientTs),
    },
  };
}

export function validateBookmark(raw) {
  if (!raw || typeof raw !== 'object') return { ok: false, errors: ['not an object'] };
  const errors = [];
  if (!isId(raw.questionId)) errors.push('questionId must be a non-empty string');
  if (typeof raw.starred !== 'boolean') errors.push('starred must be boolean');
  if (!Number.isFinite(raw.updatedAt)) errors.push('updatedAt must be a number');
  if (errors.length) return { ok: false, errors };
  return { ok: true, value: { questionId: raw.questionId, starred: raw.starred ? 1 : 0, updatedAt: Math.trunc(raw.updatedAt) } };
}

export function validateExam(raw) {
  if (!raw || typeof raw !== 'object') return { ok: false, errors: ['not an object'] };
  const errors = [];
  if (!isId(raw.clientId)) errors.push('clientId must be a non-empty string');
  for (const key of ['total', 'correct', 'wrong', 'skipped']) {
    if (!Number.isInteger(raw[key]) || raw[key] < 0) errors.push(`${key} must be a non-negative integer`);
  }
  const ts = Number.isFinite(raw.clientTs) ? raw.clientTs : raw.ts;
  if (!Number.isFinite(ts)) errors.push('clientTs (or ts) must be a number');
  if (raw.wrongIds != null && !Array.isArray(raw.wrongIds)) errors.push('wrongIds must be an array');
  if (errors.length) return { ok: false, errors };
  const total = raw.total;
  const pct = Number.isFinite(raw.pct) ? Math.trunc(raw.pct) : (total ? Math.round(raw.correct / total * 100) : 0);
  return {
    ok: true,
    value: {
      clientId: raw.clientId,
      total,
      correct: raw.correct,
      wrong: raw.wrong,
      skipped: raw.skipped,
      pct,
      wrongIds: (raw.wrongIds || []).filter(isId),
      sourceSha256ByQuestion: raw.sourceSha256ByQuestion && typeof raw.sourceSha256ByQuestion === 'object' ? raw.sourceSha256ByQuestion : {},
      clientTs: Math.trunc(ts),
    },
  };
}

/** Validate a batch; returns {ok, values} or {ok:false, errors:[{index, reason}]}. */
export function validateBatch(items, validate) {
  if (!Array.isArray(items)) return { ok: false, errors: [{ index: -1, reason: 'items must be an array' }] };
  if (items.length > MAX_BATCH) return { ok: false, errors: [{ index: -1, reason: `at most ${MAX_BATCH} items per batch` }] };
  const values = [];
  const errors = [];
  items.forEach((item, index) => {
    const result = validate(item);
    if (result.ok) values.push(result.value);
    else errors.push({ index, reason: result.errors.join('; ') });
  });
  return errors.length ? { ok: false, errors } : { ok: true, values };
}
