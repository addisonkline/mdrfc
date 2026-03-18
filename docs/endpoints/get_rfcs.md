# `GET /rfcs`

Returns RFC summaries.

## Auth

Auth is optional.

- Anonymous callers only receive public RFCs.
- Authenticated callers receive both public and private RFCs.

## Request

No path parameters, query parameters, or request body.

## Success Response

`200 OK`

```json
{
  "rfcs": [
    {
      "id": 1,
      "author_name_last": "Smith",
      "author_name_first": "Alice",
      "created_at": "2026-03-18T18:00:00Z",
      "updated_at": "2026-03-18T18:00:00Z",
      "title": "RFC Title",
      "slug": "rfc-title",
      "status": "open",
      "summary": "Short summary.",
      "public": true
    }
  ],
  "metadata": {}
}
```

## Notes

- If there are no RFCs, the current implementation returns `404`.
