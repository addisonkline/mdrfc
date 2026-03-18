# MDRFC Quickstart

This guide brings up the backend first, then optionally the frontend and CLI client.

## 1. Prerequisites

- Python 3.12 or newer
- [`uv`](https://github.com/astral-sh/uv)
- PostgreSQL
- Node.js and npm if you want to run the React frontend

## 2. Install the Backend Dependencies

From the repository root:

```bash
uv sync --dev
```

This installs the package, the `mdrfc` CLI, and the development tools used by the repository.

## 3. Configure `.env`

Copy `.env.example` to `.env` and set the minimum backend configuration:

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

For local development, `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true` is the simplest option because it skips SMTP delivery and returns the verification token directly from `POST /signup`.

## 4. Run the Database Migrations

```bash
uv run alembic upgrade head
```

`mdrfc setup` is not ready yet, so Alembic is the current setup path.

## 5. Start the Backend

```bash
uv run mdrfc serve --reload
```

By default the server listens on `http://127.0.0.1:8026`.

Useful URLs:

- API root: `http://127.0.0.1:8026/`
- FastAPI docs: `http://127.0.0.1:8026/docs`

## 6. Create and Verify a User

With `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true`, you can create and verify a user with `curl`:

```bash
curl -s -X POST http://127.0.0.1:8026/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "name_first": "Alice",
    "name_last": "Smith",
    "password": "StrongPassword1"
  }'
```

The response includes `metadata.verification_token`. Use it here:

```bash
curl -X POST http://127.0.0.1:8026/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token":"<verification_token>"}'
```

If you sign up through the React frontend while debug-token mode is enabled, the UI still says "check your email". For local development, use the network response or `curl` to read the raw token.

## 7. Optional: Run the Frontend

The browser app lives in [`frontend/`](../frontend/):

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` to `http://127.0.0.1:8026`, so the frontend can talk to the local backend without extra configuration.

## 8. Optional: Run the CLI Client

Start the REPL client from the repository root:

```bash
uv run mdrfc client http://127.0.0.1:8026 --no-login
```

Then log in interactively:

```text
login alice
```

If you want automatic login on startup, set:

```env
MDRFC_USERNAME=alice
MDRFC_PASSWORD=StrongPassword1
```

## Next Steps

- [Server guide](server.md)
- [CLI client guide](client.md)
- [Endpoint reference](endpoints/README.md)
