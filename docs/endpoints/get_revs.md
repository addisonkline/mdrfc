# Endpoint `GET /rfc/{rfc_id}/revs`

Get a summary for every revision on the specified RFC, if it exists.

## Request

This endpoint expects the path parameter `rfc_id`, which must be a valid integer.

## Response

If no RFC with the given ID exists, the server returns a `404` response. If the RFC ID is valid, the server returns a `200` response with the following JSON body:

```json
{
    "revisions": [ // all revision objects for this RFC
        {
            "id": string, // UUID as string
            "rfc_id": int,
            "created_at": string, // timestamp as string
            "author_name_last": string,
            "author_name_first": string,
            "agent_contributors": array, // array of agent contributor names (string)
            "message": string, // message for this revision
        }
    ],
    "metadata": { ... }
}
```