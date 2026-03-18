# MDRFC Server Guide

This document covers the current FastAPI backend in `src/mdrfc/server.py`.

## Overview

The backend provides:

- email-verified signup and JWT-based login
- RFC creation, retrieval, revision history, and soft-delete quarantine
- threaded comments with reply support
- admin endpoints for reviewing, restoring, and permanently deleting quarantined content

The server loads environment variables from `.env` automatically through `python-dotenv`.

## Required Backend Configuration

Always required:

- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Required when email delivery is enabled:

- `APP_BASE_URL`
- `EMAIL_FROM`
- `SMTP_HOST`

Optional email and policy settings:

- `SMTP_PORT` (defaults to `587`)
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_STARTTLS` (defaults to `true`)
- `SMTP_USE_SSL` (defaults to `false`)
- `RESEND_API_KEY`
- `REQUIRED_EMAIL_SUFFIX`
- `EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES`
- `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN`

`AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true` is useful for local development. It returns the raw verification token from `POST /signup` and skips sending email.

## Database and Startup

Run setup:

```bash
uv run mdrfc setup
```

The setup command validates the backend environment, checks database connectivity, and applies Alembic migrations to `head`.

If you want it to write the missing local-development defaults first, use:

```bash
uv run mdrfc setup --dev-defaults
```

Start the API:

```bash
uv run mdrfc serve --reload
```

Default runtime:

- host: `127.0.0.1`
- port: `8026`
- log file: `mdrfc.log`

FastAPI's interactive docs are available at `http://127.0.0.1:8026/docs`.

## Authentication Flow

The current auth flow is:

1. `POST /signup` creates an unverified account.
2. `POST /verify-email` activates the account with a one-time token.
3. `POST /login` returns a bearer token.
4. Authenticated requests send `Authorization: Bearer <token>`.

`POST /login` uses form data, not JSON.

Example:

```bash
curl -X POST http://127.0.0.1:8026/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=StrongPassword1"
```

If the account has not been verified yet, login returns `403`.

## Access Model

- Anonymous users can only see public RFCs and their comments or revisions.
- Authenticated users can see both public and private RFCs.
- Only the RFC author can create a revision for an RFC.
- Only the RFC author or an admin can quarantine an RFC.
- Only the comment author or an admin can quarantine a comment.
- Only admins can use the quarantine review, restore, and permanent-delete endpoints.

## Moderation and Quarantine

RFC and comment deletes are soft deletes:

- `DELETE /rfc/{rfc_id}` moves an RFC into quarantine.
- `DELETE /rfc/{rfc_id}/comment/{comment_id}` moves a comment into quarantine.

Admin-only follow-up endpoints live under:

- `/rfcs/quarantined`
- `/rfc/{rfc_id}/comments/quarantined`

These routes let an admin list quarantined items, restore them, or delete them permanently.

## Signup Restrictions and Rate Limits

The backend enforces the following signup rules:

- usernames and emails are normalized to lowercase
- `REQUIRED_EMAIL_SUFFIX`, if set, restricts which email domains are accepted
- signup attempts are rate-limited in memory to 5 attempts per IP per 15 minutes
- the same 5-attempt limit also applies per `(username, email)` identity pair

## `mdrfc serve` Options

`mdrfc serve` currently supports:

- `-H`, `--host`
- `-p`, `--port`
- `-r`, `--reload`
- `-lf`, `--log-file`
- `-llf`, `--log-level-file`
- `-llc`, `--log-level-console`

## Related Docs

- [Quickstart](quickstart.md)
- [CLI client guide](client.md)
- [Endpoint reference](endpoints/README.md)
