// /admin/* routes: invites and user management (role=admin only).

import { json, readJson, HttpError } from './http.js';
import { requireAdmin } from './session.js';
import { createInvite, listInvites, revokeInvite } from './invites.js';

export async function routeAdmin(request, env, ctx, { path, cors }) {
  const now = Date.now();
  const admin = await requireAdmin(request, env, now);

  if (path === '/admin/invites' && request.method === 'POST') {
    const body = await readJson(request).catch(() => ({}));
    const invite = await createInvite(env.DB, { createdBy: admin.user.id, note: body.note, expiresInDays: Number(body.expiresInDays), now });
    return json(201, { id: invite.id, code: invite.code, expiresAt: invite.expiresAt }, cors);
  }
  if (path === '/admin/invites' && request.method === 'GET') {
    return json(200, { invites: await listInvites(env.DB, now) }, cors);
  }
  const revoke = /^\/admin\/invites\/(\d+)$/.exec(path);
  if (revoke && request.method === 'DELETE') {
    const ok = await revokeInvite(env.DB, Number(revoke[1]), now);
    if (!ok) throw new HttpError(404, 'invite_not_found', 'invite not found or already used/revoked');
    return json(200, { ok: true }, cors);
  }
  if (path === '/admin/users' && request.method === 'GET') {
    const { results } = await env.DB.prepare('SELECT id, username, display_name, role, created_at, disabled_at FROM users ORDER BY id').all();
    return json(200, { users: results.map(row => ({ id: row.id, username: row.username, displayName: row.display_name, role: row.role, createdAt: row.created_at, disabledAt: row.disabled_at })) }, cors);
  }
  const disable = /^\/admin\/users\/(\d+)\/disable$/.exec(path);
  if (disable && request.method === 'POST') {
    const id = Number(disable[1]);
    if (id === admin.user.id) throw new HttpError(400, 'cannot_disable_self', 'an admin cannot disable their own account');
    const result = await env.DB.prepare('UPDATE users SET disabled_at = ? WHERE id = ? AND disabled_at IS NULL').bind(now, id).run();
    if (!(result && result.meta && result.meta.changes)) throw new HttpError(404, 'user_not_found', 'user not found or already disabled');
    await env.DB.prepare('DELETE FROM sessions WHERE user_id = ?').bind(id).run();
    return json(200, { ok: true }, cors);
  }
  throw new HttpError(404, 'not_found', `no route for ${request.method} ${path}`);
}
