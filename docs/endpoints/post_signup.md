# Endpoint `POST /signup`

Attempt to create a new account on an MDRFC server.

>[!INFO]
>Any new account must be verified after this endpoint succeeds. See [`POST /verify-email`](/docs/endpoints/post_verify_email.md) for more info.

## Request

This endpoint accepts a JSON body, so the following header is required:

```Content-Type: application/json```

The JSON body schema is as follows:

```json
{
    "username": string,
    "email": string,
    "name_last": string,
    "name_first": string,
    "password": string
}
```

## Response

It is possible that the client may not be permitted to sign up, either because of rate limits or IP limits--in which case, a `4xx` response is returned. If the signup attempt succeeds, the server returns a `200` response with the following JSON body:

```json
{
    "username": string, // the username requested
    "email": string, // the email requested
    "created_at": string, // as a timestamp
    "metadata": {
        "verification_required": true,
        "verification_expires_at": string, // as a timestamp
        "verification_token": string? // null if email bypass is enabled
    } 
}
```

Note that the response field `metadata.verification_token` will be `null` unless the server is intentionally bypassing the verification email process.

Once a `verification_token` has been received, you can verify your account with the endpoint [`POST /verify-email`](/docs/endpoints/post_verify_email.md).