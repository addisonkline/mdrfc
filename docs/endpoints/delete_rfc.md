# `DELETE /rfc/{rfc_id}`

Quarantines an RFC. This is a soft delete, not a permanent delete.

## Auth

Requires a bearer token from the RFC's author or an admin.

## Request

Headers:

```txt
Authorization: Bearer <jwt>
```

Path parameter:

```txt
rfc_id: integer
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
  "quarantined_at": "2026-03-18T18:40:00Z",
  "metadata": {}
}
```

## Notes

- The reason is validated server-side and must be long enough to pass the quarantine validator.
- Non-authors who are not admins fail with `401`.
- Missing or already quarantined RFCs fail with `404`.
