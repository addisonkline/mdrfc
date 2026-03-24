# MDRFC Roadmap

Current repository state:

- FastAPI backend is implemented
- CLI client is implemented
- React frontend now matches the core auth, RFC, revision, comment, moderation, README, and author-action flows exposed by the backend
- email verification, revisions, threaded comments, quarantine, README, and moderation routes all exist in code and are surfaced in the browser app
- `mdrfc setup` validates backend env vars, checks database connectivity, and applies migrations
- backend tests now exercise the real Alembic upgrade path against isolated Postgres databases

## Recently Completed

### Clean up the migration chain

The base Alembic revision is now frozen to the original schema instead of importing live application metadata. Fresh Postgres databases can move cleanly from base schema to head, and that path is covered by automated tests.

### Pagination and filtering

`GET /rfcs` and `GET /rfcs/{id}/comments` now support pagination and server-side filtering so the frontend and CLI no longer need full-list fetches.

### Frontend contract reset and revision-centric RFC workflow

The React app now uses the backend's actual RFC and revision contract instead of a stale `PATCH /rfcs/{id}` edit model. RFC creation exposes visibility and agent contributor inputs, the browser app has revision history and revision detail pages, and RFC authors can create revisions, request review, and quarantine their own RFCs directly from the browser.

### Frontend moderation support

The browser app now has first-class admin workflows for the backend's moderation contract: review-needed queues, accept/reject review actions, quarantined RFC restore and permanent delete flows, and quarantined comment management. The backend review transition now also clears RFCs from the review queue, and that behavior is covered by regression tests.

### Frontend README support and better local verification UX

The browser app now surfaces the server README, README revision history, and admin README revision publishing. The signup and verification flow also exposes the backend's debug-token mode more clearly, with an explicit post-signup token handoff and a manual verification path for local development.

## High Priority

### Persist signup rate limiting

The signup rate limiter is currently in-memory. It resets on every restart. For real deployment it should move to Redis or Postgres.

## Medium Priority

### Search

There is no backend search yet. The frontend can only work with whatever it already fetched.

### Deployment docs for the frontend

The repository has both a Vite dev proxy and an `nginx.conf`, but production frontend deployment is still a manual exercise.

### Migration authoring guardrails

The fresh-database path is now covered, but future schema changes should continue to avoid importing runtime DB code or using `metadata.create_all()` inside Alembic revisions. A short contributor guide or checklist would make that expectation explicit.

## Nice to Have

- Markdown preview in the CLI client
- RFC status transition rules
- stronger admin and moderation ergonomics in the frontend
- backup and restore playbooks for production deployments
