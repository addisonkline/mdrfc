# Endpoint `POST /rfc`

Post a new RFC document to this server.

>[!INFO]
>You must be logged in to use this endpoint.

## Request

This endpoint requires the following headers:

```
Authorization: Bearer {your JWT}
Content-Type: application/json
```

The JSON body schema for this request is as follows:

```json
{
    "title": string,
    "slug": string,
    "status": string, // must be one of "draft", "open"
    "summary": string,
    "content": string, // the Markdown document itself
    "agent_contributors": array // array of agent contributor names (string)
}
```

## Response

If the request is malformed (i.e., one or more body parameters does not follow server/database restrictions), the server returns a `422` response. If the operation was successful, the server returns a `200` response with the following JSON body:

```json
{
    "rfc_id": int, // the ID of the RFC just created
    "created_at": string, // timestamp as string
    "metadata": { ... }
}
```