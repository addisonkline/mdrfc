# Endpoint `POST /rfc/{rfc_id}/rev`

Revise an existing RFC, if authorized.

>[!INFO]
>You must be logged in to use this endpoint.

## Request

This request requires the following headers to be specified:

```
Authorization: Bearer {your JWT}
Content-Type: application/json
```

The path parameter `rfc_id` must be a valid integer.

The response body expects the following JSON schema:

```json
{
    "update": {
        "title": string?, // the new title, if updating
        "slug": string?, // the new slug, if updating
        "status": string?, // if updating, must be one of "draft", "open", "accepted", "rejected"
        "content": string?, // the new content, if updating
        "summary": string?, // the new summary, if updating
        "agent_contributors": array? // array of agent contributor names (string), if updating
    },
    "message": string // the message for this revision
}
```

## Response

If the client is not the same user as the author of the original RFC, the server returns a `401` response. If the revision process was successful, the server returns a `200` response with the following JSON body:

```json
{
    "revision": { // the full RFC revision
        "id": string, // UUID as string
        "rfc_id": int,
        "created_at": string, // timestamp as string
        "author_name_last": string,
        "author_name_first": string,
        "agent_contributors": array, // array of agent contributor names (string)
        "title": string,
        "slug": string,
        "status": string, // must be one of "draft", "open", "accepted", "rejected"
        "content": string,
        "summary": string,
        "message": string // the message for this revision
    },
    "metadata": { ... }
}
```