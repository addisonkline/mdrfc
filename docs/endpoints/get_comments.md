# `GET /rfcs/{rfc_id}/comments`

Deprecated alias: `GET /rfc/{rfc_id}/comments`.

Returns the comment threads for one RFC.

## Auth

Auth is optional.

- Anonymous callers can only access comments on public RFCs.
- Authenticated callers can access comments on public and private RFCs.

## Request

Path parameter:

```txt
rfc_id: integer
```

## Success Response

`200 OK`

```json
{
  "comment_threads": [
    {
      "id": 10,
      "parent_id": null,
      "author_name_first": "Alice",
      "author_name_last": "Smith",
      "created_at": "2026-03-18T18:20:00Z",
      "content": "Top-level comment",
      "replies": [
        {
          "id": 11,
          "parent_id": 10,
          "author_name_first": "Bob",
          "author_name_last": "Jones",
          "created_at": "2026-03-18T18:25:00Z",
          "content": "Reply",
          "replies": []
        }
      ]
    }
  ],
  "metadata": {}
}
```

## Notes

- Missing RFCs return `404`.
- Anonymous requests against private RFCs return `401`.
