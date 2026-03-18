# `POST /verify-email`

Activates a pending account with a verification token.

## Auth

No auth required.

## Request

Header:

```txt
Content-Type: application/json
```

Body:

```json
{
  "token": "<verification-token>"
}
```

## Success Response

`200 OK`

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "verified_at": "2026-03-18T18:05:00",
  "metadata": {}
}
```

## Notes

- Invalid or expired tokens fail with `400`.
- Very short or malformed tokens fail request validation with `422`.
