# `GET /rfcs/{rfc_id}/comments/{comment_id}`

Deprecated alias: `GET /rfc/{rfc_id}/comment/{comment_id}`.

Returns a single comment thread node. The response includes that comment and any nested replies below it.

## Auth

Auth is optional.

- Anonymous callers can only access comments on public RFCs.
- Authenticated callers can access comments on public and private RFCs.

## Request

Path parameters:

```txt
rfc_id: integer
comment_id: integer
```

## Success Response

`200 OK`

```json
{
  "comment": {
    "id": 10,
    "parent_id": null,
    "author_name_first": "Alice",
    "author_name_last": "Smith",
    "created_at": "2026-03-18T18:20:00Z",
    "content": "Top-level comment",
    "replies": [
      {
        "id": 11,
        "parent_id": 10,
        "author_name_first": "Bob",
        "author_name_last": "Jones",
        "created_at": "2026-03-18T18:25:00Z",
        "content": "Reply",
        "replies": []
      }
    ]
  },
  "metadata": {}
}
```

## Notes

- `400` means the `comment_id` does not belong to the given `rfc_id`.
- `404` means the RFC or comment was not found.
