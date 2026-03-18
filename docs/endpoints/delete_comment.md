# `DELETE /rfc/{rfc_id}/comment/{comment_id}`

Quarantines a comment. This is a soft delete, not a permanent delete.

## Auth

Requires a bearer token from the comment's author or an admin.

## Request

Headers:

```txt
Authorization: Bearer <jwt>
```

Path parameters:

```txt
rfc_id: integer
comment_id: integer
```

Query parameter:

```txt
reason: string
```

## Success Response

`200 OK`

```json
{
  "message": "success",
  "quarantined_at": "2026-03-18T18:55:00Z",
  "metadata": {}
}
```

## Notes

- The reason is validated server-side.
- Non-authors who are not admins fail with `401`.
- Missing or already quarantined comments fail with `404`.
