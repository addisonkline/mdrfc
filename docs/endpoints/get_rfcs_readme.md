# `GET /rfcs/README`

Returns the server's RFC README document as Markdown.

## Auth

Auth is optional.

## Request

No path parameters, query parameters, or request body.

## Success Response

`200 OK`

Content-Type: `text/markdown; charset=utf-8`

```markdown
# Using MDRFC

This document serves as an introductory and reference document for this MDRFC server.
```

## Notes

- The default response body comes from `src/mdrfc/utils/rfcs_readme.py`.
- Override it at startup with `uv run mdrfc serve --readme MY_README.md`.
