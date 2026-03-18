# mdrfc

MDRFC is a Markdown RFC system with three interfaces in this repository:

- a FastAPI backend for auth, RFCs, revisions, comments, and moderation
- a terminal client exposed through the `mdrfc` CLI
- a Vite/React frontend in [`frontend/`](frontend/)

## Features

- Email-verified signup and JWT login
- Public and private RFCs
- Revision history with per-revision messages and agent contributor metadata
- Threaded comments
- Quarantine flows for RFCs and comments, with admin-only review endpoints

## Quick Start

1. Install the Python dependencies:

```bash
uv sync --dev
```

2. Copy `.env.example` to `.env` and set at least:

```env
DATABASE_URL=postgresql://...
SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true
```

Generate a secret key with:

```bash
openssl rand -hex 32
```

3. Apply the database migrations:

```bash
uv run alembic upgrade head
```

4. Start the backend:

```bash
uv run mdrfc serve --reload
```

The API listens on `http://127.0.0.1:8026` by default. FastAPI also exposes interactive API docs at `http://127.0.0.1:8026/docs`.

5. Optional: start the frontend:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` to the backend on port `8026`.

6. Optional: start the CLI client:

```bash
uv run mdrfc client http://127.0.0.1:8026 --no-login
```

If you are not running from the repository root, add `--no-config` or create an `mdrfc_client.config` file first.

## Email Verification

`POST /signup` always creates an unverified user. The account must be confirmed with `POST /verify-email` before `POST /login` will succeed.

For local development, set `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true`. In that mode the signup response includes the raw verification token and the server skips email delivery.

For real email delivery, configure:

- `APP_BASE_URL`
- `EMAIL_FROM`
- `SMTP_HOST`

You can also set:

- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_STARTTLS`
- `SMTP_USE_SSL`
- `RESEND_API_KEY`
- `REQUIRED_EMAIL_SUFFIX`
- `EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES`

## Notes

- `mdrfc setup` exists in the CLI but is still a placeholder.
- The Python server does not serve the frontend bundle directly; the frontend is a separate app in [`frontend/`](frontend/).

## Documentation

- [Repository docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Server guide](docs/server.md)
- [CLI client guide](docs/client.md)
- [Endpoint reference](docs/endpoints/README.md)
- [Roadmap](docs/ROADMAP.md)
