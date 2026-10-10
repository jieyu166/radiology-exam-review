// rex-api — Cloudflare Worker entry: routing, CORS, JSON errors.
// Business logic lives in the sibling modules and is unit-tested with node --test.

import { corsHeaders } from './cors.js';
import { json, errorResponse, HttpError } from './http.js';
import { routeAuth } from './auth.js';
import { routeAdmin } from './admin.js';
import { routeSync } from './sync.js';

export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get('Origin');
    const cors = corsHeaders(origin, env.ALLOWED_ORIGINS);
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';
    try {
      if (path === '/health' && request.method === 'GET') {
        return json(200, { ok: true, service: 'rex-api', time: Date.now() }, cors);
      }
      if (path.startsWith('/auth/')) return await routeAuth(request, env, ctx, { path, url, cors });
      if (path.startsWith('/admin/')) return await routeAdmin(request, env, ctx, { path, url, cors });
      if (path.startsWith('/sync/')) return await routeSync(request, env, ctx, { path, url, cors });
      throw new HttpError(404, 'not_found', `no route for ${request.method} ${path}`);
    } catch (error) {
      return errorResponse(error, cors);
    }
  },
};
