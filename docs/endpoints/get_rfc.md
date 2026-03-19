# `GET /rfcs/{rfc_id}`

Deprecated aliases: `GET /rfc/{rfc_id}`, `GET /rfc/{rfc_id}/rev/current`.

Returns a full RFC document.

## Auth

Auth is optional.

- Anonymous callers can only read public RFCs.
- Authenticated callers can read public and private RFCs.

## Request

Path parameter:

```txt
rfc_id: integer
```

## Success Response

`200 OK`

```json
{
  "rfc": {
    "id": 1,
    "author_name_last": "Smith",
    "author_name_first": "Alice",
    "created_at": "2026-03-18T18:00:00Z",
    "updated_at": "2026-03-18T18:15:00Z",
    "title": "RFC Title",
    "slug": "rfc-title",
    "status": "open",
    "content": "# RFC Title\n\nBody",
    "summary": "Short summary.",
    "revisions": ["f6f1b8b3-4a38-4d2b-8c2a-53fa1aa8f7d3"],
    "current_revision": "f6f1b8b3-4a38-4d2b-8c2a-53fa1aa8f7d3",
    "agent_contributions": {
      "f6f1b8b3-4a38-4d2b-8c2a-53fa1aa8f7d3": ["codex@openai"]
    },
    "public": true
  },
  "metadata": {}
}
```

## Notes

- Missing RFCs return `404`.
- Anonymous requests for private RFCs return `401`.
