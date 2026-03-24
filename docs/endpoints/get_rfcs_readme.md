# `GET /rfcs/README`

Returns the server's RFC README document and metadata.

## Auth

Auth is optional.

- Anonymous callers can access the README when it is public.
- Authenticated callers can access both public and private README states.

## Request

No path parameters, query parameters, or request body.

## Success Response

`200 OK`

Content-Type: `application/json`

```json
{
  "message": "success",
  "readme": {
    "content": "# Using MDRFC\n\nThis document serves as an introductory and reference document for this MDRFC server.",
    "created_at": "2026-03-19T21:33:00Z",
    "updated_at": "2026-03-23T20:15:00Z",
    "current_revision": "11111111-1111-1111-1111-111111111111",
    "revisions": ["11111111-1111-1111-1111-111111111111"],
    "public": true
  },
  "metadata": {}
}
```

## Notes

- Anonymous callers receive `401` when the current README is private.
- The default README content comes from `src/mdrfc/utils/rfcs_readme.py`.
- Override it at startup with `uv run mdrfc serve --readme MY_README.md`.
