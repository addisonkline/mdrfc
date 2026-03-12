# Endpoint `POST /verify-email`

Attempt to verify an existing, unverified account on this server.

## Request

Since this request accepts a JSON body, the following header is required:

```Content-Type: application/json```

The JSON body schema is as follows:

```json
{
    "token": string // your verification token
}
```

## Response

If the provided verification token is still valid, and the account has not already been verified, then the server returns a `200` response with the following JSON schema:

```json
{
    "username": string, // your username
    "email": string, // your email
    "created_at": string, // timestamp as string
    "metadata": { ... }
}
```