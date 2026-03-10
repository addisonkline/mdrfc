# MDRFC contributor guide

A server for hosting Markdown-formatted RFCs. Built by Addison Kline (@addisonkline).

## Architecture

- **Backend**: FastAPI + asyncpg (raw SQL, not ORM) + PostgreSQL. Source in `src/mdrfc/`.
- **Frontend**: React 19 + Vite + Tailwind CSS 4. Source in `frontend/`.
- **CLI client**: Rich REPL that talks to the API via httpx. `src/mdrfc/client.py`.
- **Migrations**: Alembic, in `alembic/versions/`.

Entry point: `mdrfc` CLI (`src/mdrfc/cli.py`) with subcommands `serve`, `client`, `setup`.

## Key abstractions

- **RFC**: Markdown document with title, slug, summary, status (`draft|open|accepted|rejected`), content (up to 64KB). Only the original author can PATCH.
- **Comment**: Threaded via `parent_id` self-referencing FK. `build_comment_threads()` in `backend/comment.py` assembles flat DB rows into nested trees.
- **User**: Signup requires email verification. Passwords hashed with Argon2. Auth via JWT (OAuth2 password flow).

## API endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/` | No | Health check / server info |
| POST | `/signup` | No | Create account (unverified) |
| POST | `/verify-email` | No | Verify email with token |
| POST | `/login` | No | Get JWT token |
| GET | `/users/me` | Yes | Current user info |
| GET | `/rfcs` | No | List all RFCs (summaries) |
| POST | `/rfc` | Yes | Create RFC |
| GET | `/rfc/{id}` | No | Get RFC by ID |
| PATCH | `/rfc/{id}` | Yes | Update RFC (author only) |
| POST | `/rfc/comment` | Yes | Post comment on RFC |
| GET | `/rfc/{id}/comments` | No | List comment threads |
| GET | `/rfc/{id}/comment/{cid}` | No | Get specific comment thread |

## Development setup

Requires Python 3.12+, PostgreSQL, and uv.

```bash
cp .env.example .env  # then fill in values
uv sync
alembic upgrade head  # see migration caveat below
mdrfc serve -r        # starts on 127.0.0.1:8026 with hot reload
```

Frontend (separate terminal):
```bash
cd frontend && npm install && npm run dev
```

Vite proxies `/api/*` to the backend at `:8026`.

### Required env vars

```
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=<random hex string for JWT signing>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

For local dev without a real mail server, set `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true` — the signup response will include the verification token so you can call `/verify-email` directly.

SMTP vars (`APP_BASE_URL`, `EMAIL_FROM`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`) are only needed if you want actual email delivery. Without them, the background email task fails silently and logs a warning.

## Deployment (tinybox)

The backend is deployed at `~/mdrfc` on the tinybox (`ssh tiny@tinybox -p 2223`).

- PostgreSQL 14, database `mdrfc`, user `mdrfc`
- Server runs on `0.0.0.0:8026`
- Cloudflare tunnel (`mdrfc`, ID `cded8863-8b7e-4071-a9f1-6bbaf8a4a4ce`) exposes it at `https://rfc.chrn.ai`
- Tunnel config: `~/.cloudflared/config.yml` on the tinybox

### Starting the server

```bash
cd ~/mdrfc && nohup uv run mdrfc serve -H 0.0.0.0 > /tmp/mdrfc-server.log 2>&1 &
cloudflared tunnel run mdrfc
```

Neither persists across reboots yet — no systemd services configured.

## Migration caveat

The first Alembic migration uses `metadata_obj.create_all(engine)`, which creates tables from the *current* Python schema — including columns added by later migrations. On a fresh database, later migrations fail with "duplicate column" errors.

**Workaround for fresh deploys:**
```bash
alembic upgrade c271fd63e1c9   # run only the first migration
alembic stamp head              # mark all migrations as applied
```

## Running tests

```bash
uv run pytest
```

Tests are pure unit tests (no DB needed) — they monkeypatch the DB layer. Two test files:
- `tests/backend/test_auth_signup.py` — signup, verification, rate limiting, email
- `tests/backend/test_comment_threads.py` — comment thread building/searching

## Code conventions

- Pydantic models for all request/response types (`requests.py`, `responses.py`)
- Validation rules and field length limits centralized in `backend/constants.py`
- Frontend mirrors backend validation in `frontend/src/validation.ts`
- DB queries use raw asyncpg with parameterized queries (not SQLAlchemy ORM)
