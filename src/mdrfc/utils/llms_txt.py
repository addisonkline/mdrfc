LLMS_TXT = """
# MDRFC

An open-source server for hosting Markdown-based requests for comment (RFCs).

## Server Summary

### Endpoints

This is not an exhaustive list of all MDRFC server endpoints.
Refer to the official docs or `GET /docs`.

- `GET /`: Obtain basic server information and metadata.
- `POST /login`: Obtain a temporary bearer token after providing valid credentials.
- `GET /rfcs`: Get all RFCs on this server.
- `GET /rfcs/{rfc_id}`: Get a specific RFC.
- `POST /rfcs`: Post a new RFC.
- `DELETE /rfcs/{rfc_id}`: Delete an existing RFC.
- `GET /rfcs/{rfc_id}/comments`: Get all comments on a specific RFC.
- `GET /rfcs/{rfc_id}/comments/{comment_id}`: Get a specific comment on an RFC.
- `POST /rfcs/{rfc_id}/comments`: Post a new comment on an RFC.
- `DELETE /rfcs/{rfc_id}/comments/{comment_id}`: Delete a specific existing comment.
- `GET /rfcs/{rfc_id}/revs`: Get all revisions on a specific RFC.
- `GET /rfcs/{rfc_id}/revs/{revision_id}`: Get a specific revision on an RFC.
- `POST /rfcs/{rfc_id}/revs`: Revise an existing RFC.

### Client Interface

There are three primary client types for interfacing with an MDRFC server:
- The built-in frontend web client (TypeScript, Vite)
- The built-in CLI client (Python)
- A third-party client, such as [mdrfc-go](https://github.com/charonlabs/mdrfc-go)

## Useful Links
- **Repository**: https://github.com/addisonkline/mdrfc
- **Go Client**: https://github.com/charonlabs/mdrfc-go

"""