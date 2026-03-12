# Endpoint `POST /login`

Attempt to log into the server and retrieve a temporary access token.

## Request

This endpoint follows the OAuth2 schema and syntax. Specifically, the following header is required:

```Content-Type: application/x-www-form-urlencoded```

With this header, provide the following JSON body:

```json
{
    "grant_type": "password",
    "username": string, // your username
    "password": string, // your password
    "scope": string?, // can be null or an empty string
    "client_id": string, // your username
    "client_secret": string // your password
}
```

## Response

If the given credentials are not valid, the server returns `401`. If the credentials are valid, the server returns a `200` response with the following JSON body:

```json
{
    "access_token": string, // JWT
    "token_type": "bearer"
}
```