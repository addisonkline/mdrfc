# MDRFC Roadmap

Current repository state:

- FastAPI backend is implemented
- CLI client is implemented
- React frontend exists in `frontend/`
- email verification, revisions, threaded comments, and quarantine routes all exist in code
- `mdrfc setup` still only prints `TODO`

## High Priority

### Finish `mdrfc setup`

There is already a top-level CLI command for setup, but it is not wired up yet. It should eventually handle the current manual bootstrap steps:

- validating `.env`
- checking database connectivity
- applying Alembic migrations
- optionally creating local dev defaults

### Clean up the migration chain

The migration history still needs a fresh-database pass to make sure a brand-new Postgres instance can move cleanly from base schema to head.

### Persist signup rate limiting

The signup rate limiter is currently in-memory. It resets on every restart. For real deployment it should move to Redis or Postgres.

### Frontend moderation support

The backend has quarantine review, restore, and permanent-delete endpoints, but the browser app still needs first-class admin workflows for them.

## Medium Priority

### Pagination and filtering

`GET /rfcs` and `GET /rfc/{id}/comments` currently return full lists. Add pagination and server-side filtering before the dataset gets large.

### Search

There is no backend search yet. The frontend can only work with whatever it already fetched.

### Deployment docs for the frontend

The repository has both a Vite dev proxy and an `nginx.conf`, but production frontend deployment is still a manual exercise.

### Better local verification UX

In debug-token mode the backend returns the raw verification token, but the React signup flow still assumes email delivery. Local development would be smoother with a dedicated dev-only verification screen or debug banner.

## Nice to Have

- Markdown preview in the CLI client
- RFC status transition rules
- stronger ownership and moderation ergonomics in the frontend
- backup and restore playbooks for production deployments
