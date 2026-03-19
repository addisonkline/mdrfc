# `GET /rfcs/{rfc_id}/comments/quarantined`

Deprecated alias: `GET /rfc/{rfc_id}/comments/quarantined`.

Returns the admin view of quarantined comments for one RFC.

## Auth

Requires a bearer token from an admin user.

## Request

Headers:

```txt
Authorization: Bearer <jwt>
```

Path parameter:

```txt
rfc_id: integer
```

## Success Response

`200 OK`

```json
{
  "quarantined_comments": [
    {
      "quarantine_id": 7,
      "quarantined_by_name_last": "Admin",
      "quarantined_by_name_first": "Alice",
      "quarantined_at": "2026-03-18T18:55:00Z",
      "reason": "Off-topic.",
      "comment": {
        "id": 11,
        "parent_id": 10,
        "rfc_id": 1,
        "created_at": "2026-03-18T18:25:00Z",
        "content": "Reply text",
        "author_name_first": "Bob",
        "author_name_last": "Jones"
      }
    }
  ],
  "metadata": {}
}
```

## Notes

- Non-admin callers fail with `401`.
