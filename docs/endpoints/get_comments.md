# Endpoint `GET /rfc/{rfc_id}/comments`

Get all comments on a given RFC document, if it exists.

## Request

This endpoint expects the path parameter `rfc_id`, which must be a valid integer.

## Response

If no RFC with the specified `rfc_id` exists, the server returns a `404` response. If the RFC ID is valid, the server returns a `200` response with the following JSON body:

```json
{
    "comment_threads": [ // all comment threads on this RFC
        { // CommentThread object
            "id": int,
            "parent_id": int?, // the comment this is a reply to, if applicable
            "author_name_first": string,
            "author_name_last": string,
            "created_at": string, // timetamp as string
            "content": string,
            "replies": array // list of CommentThread objects
        }
    ],
    "metadata": { ... }
}
```