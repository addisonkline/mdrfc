# `GET /users/me`

Returns the currently authenticated user.

## Auth

Requires a bearer token.

## Request

Header:

```txt
Authorization: Bearer <jwt>
```

## Success Response

`200 OK`

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "name_last": "Smith",
  "name_first": "Alice",
  "is_verified": true,
  "verified_at": "2026-03-18T18:05:00",
  "created_at": "2026-03-18T18:00:00",
  "is_admin": false
}
```

## Notes

- Missing or invalid tokens fail with `401`.
