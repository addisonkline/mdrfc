# `POST /rfcs/{rfc_id}/revs`

Deprecated alias: `POST /rfc/{rfc_id}/rev`.

Creates a new revision for an existing RFC.

## Auth

Requires a bearer token from the RFC's author. The current implementation does not allow non-authors to create revisions.

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
  "update": {
    "title": "Updated RFC Title",
    "slug": "updated-rfc-title",
    "status": "open",
    "summary": "Updated summary.",
    "content": "# Updated RFC Title\n\nBody",
    "agent_contributors": ["codex@openai"],
    "public": true
  },
  "message": "Clarify rollout plan"
}
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
    "title": "Updated RFC Title",
    "slug": "updated-rfc-title",
    "status": "open",
    "content": "# Updated RFC Title\n\nBody",
    "summary": "Updated summary.",
    "message": "Clarify rollout plan",
    "public": true
  },
  "metadata": {}
}
```

## Notes

- All fields inside `update` are optional.
- On write, `status` only accepts `draft` or `open`.
- `update.public=true` can publish the RFC, but `false` currently leaves the existing visibility unchanged.
