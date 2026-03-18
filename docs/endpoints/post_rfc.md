# `POST /rfc`

Creates a new RFC document.

## Auth

Requires a bearer token.

## Request

Headers:

```txt
Authorization: Bearer <jwt>
Content-Type: application/json
```

Body:

```json
{
  "title": "RFC Title",
  "slug": "rfc-title",
  "status": "draft",
  "summary": "Short summary.",
  "content": "# RFC Title\n\nBody",
  "agent_contributors": ["codex@openai"],
  "public": false
}
```

## Success Response

`200 OK`

```json
{
  "rfc_id": 1,
  "created_at": "2026-03-18T18:00:00Z",
  "metadata": {}
}
```

## Notes

- `status` currently accepts only `draft` or `open` on write.
- `agent_contributors` entries must be in `agent@host` format.
