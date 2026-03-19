# `GET /llms.txt`

Returns an LLM-friendly plain-text document describing the server.

## Auth

No auth required.

## Request

No path parameters, query parameters, or request body.

## Success Response

`200 OK`

Content-Type: `text/plain; charset=utf-8`

```text
# MDRFC

An open-source server for hosting Markdown-based requests for comment (RFCs).
```

## Notes

- The default response body comes from `src/mdrfc/utils/llms_txt.py`.
- Override it at startup with `uv run mdrfc serve --llms-txt llms.txt`.
