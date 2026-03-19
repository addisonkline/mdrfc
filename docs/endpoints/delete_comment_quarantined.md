# `DELETE /rfcs/{rfc_id}/comments/quarantined/{quarantine_id}`

Deprecated alias: `DELETE /rfc/{rfc_id}/comments/quarantined/{quarantine_id}`.

Permanently deletes a quarantined comment.

## Auth

Requires a bearer token from an admin user.

## Request

Headers:

```txt
Authorization: Bearer <jwt>
```

Path parameters:

```txt
rfc_id: integer
quarantine_id: integer
```

## Success Response

`200 OK`

```json
{
  "message": "success",
  "deleted_at": "2026-03-18T19:00:00Z",
  "metadata": {}
}
```

## Notes

- Missing quarantine entries fail with `404`.
