# Endpoint `POST /rfc/{rfc_id}/comment`

Post a new comment on an existing RFC.

>[!INFO]
>You must be logged in to use this endpoint.

## Request

This endpoint requires the following headers:

```
Authorization: Bearer {your JWT}
Content-Type: application/json
```

The path parameter `rfc_id` is required and must be a valid integer.

This endpoint expects a request body with the following JSON schema:

```json
{
    "parent_comment_id": int?, // the ID of the comment to reply to, if desired
    "content": string
}
```

## Response

If no RFC with the specified `rfc_id` exists, the server returns a `404` response. If the comment operation was successful, the server returns the following JSON body:

```json
{
    "comment_id": int, // the ID of the created comment
    "created_at": string, // timestamp as string
    "metadata": { ... }
}
```