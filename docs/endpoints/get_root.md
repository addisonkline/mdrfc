# Endpoint `GET /`

Obtain basic server information and metadata.

## Request

No parameters (path, query, or body) are accepted.

## Response

If the server is running, it should return a `200` response with the following JSON body:

```json
{
    "name": "mdrfc",
    "version": string, // the current MDRFC version
    "status": "ok",
    "uptime": float, // must be > 0.0
    "metadata": { ... }
}
```