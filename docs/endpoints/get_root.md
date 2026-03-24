# `GET /`

Returns basic server metadata and uptime.

## Auth

No auth required.

## Request

No path parameters, query parameters, or request body.

## Success Response

`200 OK`

```json
{
  "name": "mdrfc",
  "version": "0.4.0",
  "status": "ok",
  "uptime": 12.34,
  "metadata": {}
}
```
