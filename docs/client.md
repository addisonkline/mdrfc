# MDRFC CLI Client Guide

This document covers the terminal client implemented in `src/mdrfc/client.py`.

## Launching the Client

Start the REPL with:

```bash
uv run mdrfc client http://127.0.0.1:8026 --no-login
```

By default the client does two things on startup:

- it loads `mdrfc_client.config` from the current working directory
- it attempts auto-login with `MDRFC_USERNAME` and `MDRFC_PASSWORD`

If you do not want those behaviors, use:

- `--no-config`
- `--no-login`

## Optional Environment Variables

```env
MDRFC_USERNAME=alice
MDRFC_PASSWORD=StrongPassword1
```

If both are set, the client will try to log in automatically on startup. The `refresh` command also reuses `MDRFC_PASSWORD` instead of prompting again.

## Client Config File

The config model is versioned and currently expects version `0.3.0`.

Example:

```json
{
  "version": "0.5.0",
  "aliases": [
    { "alias": "ls", "command": "rfc-list" },
    { "alias": "cat", "command": "rfc-get" }
  ]
}
```

The repository root already contains a sample [`mdrfc_client.config`](../mdrfc_client.config).

## Common Commands

Authentication:

- `ping`
- `login <username>`
- `refresh`
- `logout`
- `whoami`

RFCs:

- `rfc-list`
- `rfc-get <id>`
- `rfc-post <docpath> <title> <slug> <summary> <status>`
- `rfc-delete <rfc_id> <reason>`

Revisions:

- `revision-list <rfc_id>`
- `revision-get <rfc_id> <revision_id>`
- `revision-post <rfc_id> <message> [--title ... --slug ... --status ... --summary ... --content-file ...]`

`revision-post` is only valid while the RFC is still open for revision. Once the author requests admin review, or once the RFC is marked `accepted` or `rejected`, revision submission is rejected by the server.

`rfc-list` also supports backend search via `--query "..."`. When a query is provided, the CLI defaults to `--sort relevance_desc`; otherwise it defaults to `updated_at_desc`.

Comments:

- `comment-list <rfc_id>`
- `comment-get <rfc_id> <comment_id>`
- `comment-post <rfc_id> <content> [--reply-to <comment_id>]`
- `comment-delete <rfc_id> <comment_id> <reason>`

Admin moderation:

- `rfc-quarantine-list`
- `rfc-quarantine-post <quarantine_id>`
- `comment-quarantine-list <rfc_id>`
- `comment-quarantine-post <rfc_id> <quarantine_id>`

Aliases:

- `alias-set <command> <alias>`
- `alias-get <alias>`
- `alias-list`

## REPL Behavior

- `help` or `?` prints the command list
- `<command> -h` shows help for a single command
- `exit` and `quit` close the session

`login` prompts for a password interactively. `rfc-post` reads Markdown content from the file path you pass in `docpath`.

## Notes

- The client is useful for day-to-day API access, but the [endpoint reference](endpoints/README.md) is still the source of truth for the full HTTP surface.
- The browser frontend in [`frontend/`](../frontend/) is separate from the CLI client.
