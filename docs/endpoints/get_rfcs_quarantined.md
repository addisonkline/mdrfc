# `GET /rfcs/quarantined`

Returns the admin view of quarantined RFCs.

## Auth

Requires a bearer token from an admin user.

## Request

Header:

```txt
Authorization: Bearer <jwt>
```

## Success Response

`200 OK`

```json
{
  "quarantined_rfcs": [
    {
      "quarantine_id": 4,
      "quarantined_by_name_last": "Admin",
      "quarantined_by_name_first": "Alice",
      "quarantined_at": "2026-03-18T18:40:00Z",
      "reason": "Superseded by a newer draft.",
      "rfc_id": 1,
      "rfc_title": "RFC Title",
      "rfc_slug": "rfc-title",
      "rfc_status": "open",
      "rfc_summary": "Short summary."
    }
  ],
  "metadata": {}
}
```

## Notes

- Non-admin callers fail with `401`.
