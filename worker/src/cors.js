// CORS for the static front end (GitHub Pages / localhost). Pure functions, no Request dependency.

export const ALLOW_METHODS = 'GET, POST, DELETE, OPTIONS';
export const ALLOW_HEADERS = 'Content-Type, Authorization';
export const MAX_AGE = '7200';

export function parseAllowedOrigins(raw) {
  return String(raw || '')
    .split(',')
    .map(item => item.trim().replace(/\/+$/, ''))
    .filter(Boolean);
}

/** Headers to attach to every response. Unlisted origins get no allow headers at all. */
export function corsHeaders(origin, allowedOrigins) {
  const list = Array.isArray(allowedOrigins) ? allowedOrigins : parseAllowedOrigins(allowedOrigins);
  const headers = { Vary: 'Origin' };
  if (origin && list.includes(origin.replace(/\/+$/, ''))) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers['Access-Control-Allow-Methods'] = ALLOW_METHODS;
    headers['Access-Control-Allow-Headers'] = ALLOW_HEADERS;
    headers['Access-Control-Max-Age'] = MAX_AGE;
  }
  return headers;
}

export function isAllowedOrigin(origin, allowedOrigins) {
  return 'Access-Control-Allow-Origin' in corsHeaders(origin, allowedOrigins);
}
