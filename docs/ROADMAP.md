# MDRFC Roadmap

Current repository state:

- FastAPI backend is implemented
- CLI client is implemented
- React frontend exists in `frontend/`
- email verification, revisions, threaded comments, and quarantine routes all exist in code
- `mdrfc setup` validates backend env vars, checks database connectivity, and applies migrations
- backend tests now exercise the real Alembic upgrade path against isolated Postgres databases

## Recently Completed

### Clean up the migration chain

The base Alembic revision is now frozen to the original schema instead of importing live application metadata. Fresh Postgres databases can move cleanly from base schema to head, and that path is covered by automated tests.

## High Priority

### Persist signup rate limiting

The signup rate limiter is currently in-memory. It resets on every restart. For real deployment it should move to Redis or Postgres.

### Frontend moderation support

The backend has quarantine review, restore, and permanent-delete endpoints, but the browser app still needs first-class admin workflows for them.

## Medium Priority

### Pagination and filtering

`GET /rfcs` and `GET /rfcs/{id}/comments` currently return full lists. Add pagination and server-side filtering before the dataset gets large.

### Search

There is no backend search yet. The frontend can only work with whatever it already fetched.

### Deployment docs for the frontend

The repository has both a Vite dev proxy and an `nginx.conf`, but production frontend deployment is still a manual exercise.

### Better local verification UX

In debug-token mode the backend returns the raw verification token, but the React signup flow still assumes email delivery. Local development would be smoother with a dedicated dev-only verification screen or debug banner.

### Migration authoring guardrails

The fresh-database path is now covered, but future schema changes should continue to avoid importing runtime DB code or using `metadata.create_all()` inside Alembic revisions. A short contributor guide or checklist would make that expectation explicit.

## Nice to Have

- Markdown preview in the CLI client
- RFC status transition rules
- stronger ownership and moderation ergonomics in the frontend
- backup and restore playbooks for production deployments
