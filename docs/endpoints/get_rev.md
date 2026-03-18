# `GET /rfc/{rfc_id}/rev/{rev_id}`

Returns one full RFC revision.

## Auth

Auth is optional.

- Anonymous callers can only access public revisions.
- Authenticated callers can access public and private revisions.

## Request

Path parameters:

```txt
rfc_id: integer
rev_id: UUID string
```

## Success Response

`200 OK`

```json
{
  "revision": {
    "id": "f6f1b8b3-4a38-4d2b-8c2a-53fa1aa8f7d3",
    "rfc_id": 1,
    "created_at": "2026-03-18T18:15:00Z",
    "author_name_last": "Smith",
    "author_name_first": "Alice",
    "agent_contributors": ["codex@openai"],
    "title": "RFC Title",
    "slug": "rfc-title",
    "status": "open",
    "content": "# RFC Title\n\nBody",
    "summary": "Short summary.",
    "message": "Clarify rollout plan",
    "public": false
  },
  "metadata": {}
}
```

## Notes

- Missing revisions return `404`.
- Anonymous requests for private revisions return `401`.
