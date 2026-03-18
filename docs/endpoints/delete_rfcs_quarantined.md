# `DELETE /rfcs/quarantined/{quarantine_id}`

Permanently deletes a quarantined RFC.

## Auth

Requires a bearer token from an admin user.

## Request

Headers:

```txt
Authorization: Bearer <jwt>
```

Path parameter:

```txt
quarantine_id: integer
```

## Success Response

`200 OK`

```json
{
  "message": "success",
  "deleted_at": "2026-03-18T18:45:00Z",
  "metadata": {}
}
```

## Notes

- Missing quarantine entries fail with `404`.
