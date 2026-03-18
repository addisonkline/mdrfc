# `POST /signup`

Creates a new unverified account.

After a successful signup, the account must be activated through [`POST /verify-email`](post_verify_email.md).

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
  "username": "alice",
  "email": "alice@example.com",
  "name_last": "Smith",
  "name_first": "Alice",
  "password": "StrongPassword1"
}
```

## Success Response

`200 OK`

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2026-03-18T18:00:00",
  "metadata": {
    "verification_required": true,
    "verification_expires_at": "2026-03-18T19:00:00",
    "verification_token": "raw-token-or-null"
  }
}
```

## Notes

- When `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true`, `metadata.verification_token` contains the raw token.
- Otherwise the server sends the token by email and `metadata.verification_token` is `null`.
- Signup can fail with `429` when the in-memory rate limiter is triggered.
- If `REQUIRED_EMAIL_SUFFIX` is configured and the email does not match it, the request fails with `401`.
- Duplicate usernames or emails fail with `409`.
