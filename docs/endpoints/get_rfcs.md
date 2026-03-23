# `GET /rfcs`

Returns RFC summaries.

## Auth

Auth is optional.

- Anonymous callers only receive public RFCs.
- Authenticated callers receive both public and private RFCs.

## Request

No path parameters or request body.

Optional query parameters:

```txt
limit: integer (default 20, min 1, max 100)
offset: integer (default 0, min 0)
status: "draft" | "open" | "accepted" | "rejected"
public: boolean
author_id: integer
review_requested: boolean
sort: "updated_at_desc" | "updated_at_asc" | "created_at_desc" | "created_at_asc"
```

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
  "metadata": {
    "pagination": {
      "limit": 20,
      "offset": 0,
      "returned": 1,
      "total": 1,
      "has_more": false
    },
    "filters": {
      "status": null,
      "public": null,
      "author_id": null,
      "review_requested": null
    },
    "sort": "updated_at_desc"
  }
}
```

## Notes

- Empty result sets return `200 OK` with `"rfcs": []`.
- Anonymous callers are always restricted to public RFCs even when no `public` filter is supplied.
