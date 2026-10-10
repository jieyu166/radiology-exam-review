// Small HTTP helpers shared by all routes.

export class HttpError extends Error {
  constructor(status, code, message, extra) {
    super(message || code);
    this.status = status;
    this.code = code;
    this.extra = extra || null;
  }
}

export function json(status, body, headers) {
  return new Response(JSON.stringify(body), {
    status,
    headers: Object.assign({ 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }, headers || {}),
  });
}

export function errorResponse(error, headers) {
  if (error instanceof HttpError) {
    return json(error.status, Object.assign({ error: error.code, message: error.message }, error.extra || {}), headers);
  }
  const message = String(error && error.message || error);
  if (/limit|quota|exceeded/i.test(message)) {
    return json(503, { error: 'quota', message: 'storage quota exceeded, retry later' }, headers);
  }
  console.error('[rex-api] unhandled', error);
  return json(500, { error: 'internal', message: 'internal error' }, headers);
}

export async function readJson(request) {
  const type = request.headers.get('Content-Type') || '';
  if (!type.includes('application/json')) throw new HttpError(415, 'unsupported_media_type', 'expected application/json');
  try {
    const body = await request.json();
    if (!body || typeof body !== 'object' || Array.isArray(body)) throw new Error('not an object');
    return body;
  } catch (e) {
    throw new HttpError(400, 'invalid_json', 'request body must be a JSON object');
  }
}

export function bearerToken(request) {
  const header = request.headers.get('Authorization') || '';
  const match = /^Bearer\s+([A-Za-z0-9_-]{16,256})$/.exec(header.trim());
  return match ? match[1] : null;
}

export const now = () => Date.now();
