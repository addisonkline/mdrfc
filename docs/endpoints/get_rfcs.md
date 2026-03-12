# Endpoint `GET /rfcs`

Get summarized versions of all RFC documents currently on this server.

## Request

No parameters (path, query, or body) are accepted by this endpoint.

## Response

The server should return a `200` response with the following JSON body:

```json
{
    "rfcs": [ // list of RFC document summaries
        {
            "id": int,
            "author_name_last": string,
            "author_name_first": string,
            "created_at": string, // timestamp as string
            "updated_at": string, // timestmap as string
            "title": string,
            "slug": string,
            "status": string, // must be one of "draft", "open", "accepted", "rejected"
            "summary": string
        }
    ],
    "metadata": { ... }
}
```