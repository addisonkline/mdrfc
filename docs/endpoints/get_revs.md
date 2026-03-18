# `GET /rfc/{rfc_id}/revs`

Returns revision summaries for one RFC.

## Auth

Auth is optional.

- Anonymous callers can only access public RFCs.
- Authenticated callers can access public and private RFCs.

## Request

Path parameter:

```txt
rfc_id: integer
```

## Success Response

`200 OK`

```json
{
  "revisions": [
    {
      "id": "f6f1b8b3-4a38-4d2b-8c2a-53fa1aa8f7d3",
      "rfc_id": 1,
      "created_at": "2026-03-18T18:15:00Z",
      "author_name_last": "Smith",
      "author_name_first": "Alice",
      "agent_contributors": ["codex@openai"],
      "message": "Clarify rollout plan",
      "public": false
    }
  ],
  "metadata": {}
}
```

## Notes

- Missing RFCs return `404`.
- Anonymous requests against private RFCs return `401`.
