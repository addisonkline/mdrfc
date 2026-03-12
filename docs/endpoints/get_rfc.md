# Endpoint `GET /rfc/{rfc_id}`

Get an existing RFC document by its ID.

## Request

This endpoint accepts a path parameter, `rfc_id`, which must be an integer.

## Response

If no RFC exists with the specified ID, the server returns a `404` response. If an RFC was found, the server returns a `200` response with the following JSON body:

```json
{
    "rfc": { // the RFC document
        "id": int,
        "author_name_last": string,
        "author_name_first": string,
        "created_at": string, // timestamp as string
        "updated_at": string, // timestamp as string
        "title": string,
        "slug": string,
        "status": string, // must be one of "draft", "open", "accepted", "rejected"
        "content": string, // the Markdown document
        "summary": string,
        "revisions": array, // array of UUIDs as strings
        "current_revision": string, // UUID as string
        "agent_contributions": object, // keys are revision IDs (UUID as string), values are arrays of agent contributors (string)
    },
    "metadata": { ... }
}
```