# MDRFC Roadmap

Current state: backend API deployed on tinybox, served at `https://rfc.chrn.ai` via Cloudflare tunnel, both managed by systemd. No frontend deployed. Auth works but uses debug token return instead of real email.

---

## Usable by real people

### Deploy the frontend
Build the React SPA and serve it through the tunnel. Options:
- Serve the built `frontend/dist/` via nginx on the tinybox (config already exists in `nginx.conf`)
- Or add a second Cloudflare tunnel ingress rule pointing at a static file server
- The Vite config already proxies `/api/*` to the backend, and the nginx config does the same — just need to pick one and wire it up

### Real email verification
Right now `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true` returns the token in the signup API response, which defeats the point of verification. To fix:
1. Pick an email provider (Resend, Mailgun, AWS SES, etc.)
2. Set the SMTP env vars in `.env` on the tinybox
3. Set `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=false`
4. Set `APP_BASE_URL=https://rfc.chrn.ai`

Alternatively: rethink whether email verification is needed at all for the initial use case. If this is a small-group tool, invite-only or open signup without verification might be simpler.

### Database backups
There's one Postgres instance with no redundancy. A simple cron job would cover it:
```bash
# e.g., daily pg_dump to a file, rotate old ones
pg_dump -U mdrfc mdrfc | gzip > /home/tiny/backups/mdrfc-$(date +%F).sql.gz
```

---

## Doesn't degrade as it grows

### Pagination
No list endpoints are paginated — `GET /rfcs` returns every RFC, `GET /rfc/{id}/comments` returns every comment. Fine at small scale, bad at hundreds. Add `limit`/`offset` or cursor-based pagination to both.

### Persistent rate limiting
The signup rate limiter (`SlidingWindowRateLimiter`) is in-memory. It resets every time the server restarts. For real protection, back it with Redis or Postgres.

### Delete endpoints
No way to delete RFCs or comments through the API. Would need:
- `DELETE /rfc/{id}` (author only)
- `DELETE /rfc/{id}/comment/{cid}` (author or RFC author)
- Consider soft-delete vs hard-delete

### Fix the migration chain
The first Alembic migration uses `metadata_obj.create_all(engine)` which creates the full current schema, making later incremental migrations fail on fresh databases. Options:
- Squash all migrations into one clean initial migration
- Or change the first migration to use explicit `op.create_table()` calls matching the original schema

### Author check on frontend
`RfcDetailPage.tsx` checks authorship by comparing `name_first`/`name_last` between the logged-in user and the RFC author. This breaks if two users share a name. Should compare by user ID (would need the backend to return `created_by` in the RFC response, or a dedicated ownership endpoint).

---

## Nice to have

- Search/filter on the backend (currently frontend filters client-side only)
- RFC status transition rules (e.g., can't go from `rejected` back to `draft`)
- Markdown preview in the CLI client
- `mdrfc setup` command (currently prints `TODO`)
- HTTPS between cloudflared and backend (not strictly needed since it's localhost, but good hygiene)
