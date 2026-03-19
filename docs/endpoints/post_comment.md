# `POST /rfcs/{rfc_id}/comments`

Deprecated alias: `POST /rfc/{rfc_id}/comment`.

Creates a new comment on an RFC.

## Auth

Requires a bearer token.

## Request

Headers:

```txt
Authorization: Bearer <jwt>
Content-Type: application/json
```

Path parameter:

```txt
rfc_id: integer
```

Body:

```json
{
  "parent_comment_id": 10,
  "content": "Reply text"
}
```

Set `parent_comment_id` to `null` for a top-level comment.

## Success Response

`200 OK`

```json
{
  "comment_id": 11,
  "created_at": "2026-03-18T18:25:00Z",
  "metadata": {}
}
```

## Notes

- Replies must point at a comment on the same RFC.
- Commenting on a missing or quarantined RFC fails.
