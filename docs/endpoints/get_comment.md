# Endpoint `GET /rfc/{rfc_id}/comment/{comment_id}`

Get a specific comment (with replies) on a given RFC, if it exists.

## Request

This endpoint expects the path parameters `rfc_id` and `comment_id`, which must both be valid integers.

## Response

If neither the RFC or comment within it exists, the server returns a `404` response. If the specified comment does exist, the server returns a `200` response with the following JSON body:

```json
{
    "comment": { // CommentThread object
        "id": int,
        "parent_id": int?, // the comment this is a reply to, if applicable
        "author_name_first": string,
        "author_name_last": string,
        "created_at": string, // timetamp as string
        "content": string,
        "replies": array // list of CommentThread objects
    },
    "metadata": { ... }
}
```