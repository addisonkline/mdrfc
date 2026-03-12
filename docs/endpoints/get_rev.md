# Endpoint `GET /rfc/{rfc_id}/rev/{revision_id}`

Get a specific revision (in full) for a specified RFC, if it exists.

## Request

This endpoint requires two path parameters: `rfc_id` and `revision_id`. `rfc_id` must be a valid integer, and `revision_id` must be a string representation of a UUID.

## Response

If the specified revision does not exist, the server returns a `404` response. If the specified revision ID is valid, the server returns a `200` response with the following JSON body:

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