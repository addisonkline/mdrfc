# `POST /login`

Logs in a verified user and returns a bearer token.

## Auth

No auth required.

## Request

This endpoint expects `application/x-www-form-urlencoded` data, not JSON.

Minimum required fields:

```txt
username
password
```

The CLI client also sends the extra OAuth2 password-flow fields, but the server only needs a valid username and password pair.

## Success Response

`200 OK`

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

## Notes

- `401` means the username or password is incorrect.
- `403` means the account exists but the email address has not been verified yet.
