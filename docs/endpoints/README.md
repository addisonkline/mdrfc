# MDRFC HTTP Endpoint Reference

This directory documents the current routes exposed by `src/mdrfc/server.py`.

## Basic

- [`GET /`](get_root.md)

## Authentication

- [`POST /login`](post_login.md)
- [`POST /signup`](post_signup.md)
- [`POST /verify-email`](post_verify_email.md)
- [`GET /users/me`](get_users_me.md)

## RFCs

- [`GET /rfcs`](get_rfcs.md)
- [`GET /rfcs/quarantined`](get_rfcs_quarantined.md)
- [`DELETE /rfcs/quarantined/{quarantine_id}`](delete_rfcs_quarantined.md)
- [`POST /rfcs/quarantined/{quarantine_id}`](post_rfcs_quarantined.md)
- [`POST /rfcs`](post_rfc.md)
- [`GET /rfcs/{rfc_id}`](get_rfc.md)
- [`DELETE /rfcs/{rfc_id}`](delete_rfc.md)
- Deprecated aliases: `POST /rfc`, `GET /rfc/{rfc_id}`, `GET /rfc/{rfc_id}/rev/current`, `DELETE /rfc/{rfc_id}`

## Revisions

- [`GET /rfcs/{rfc_id}/revs`](get_revs.md)
- [`GET /rfcs/{rfc_id}/revs/{rev_id}`](get_rev.md)
- [`POST /rfcs/{rfc_id}/revs`](post_rev.md)
- Deprecated aliases: `GET /rfc/{rfc_id}/revs`, `GET /rfc/{rfc_id}/rev/{rev_id}`, `POST /rfc/{rfc_id}/rev`

## Comments

- [`POST /rfcs/{rfc_id}/comments`](post_comment.md)
- [`GET /rfcs/{rfc_id}/comments`](get_comments.md)
- [`GET /rfcs/{rfc_id}/comments/quarantined`](get_comments_quarantined.md)
- [`DELETE /rfcs/{rfc_id}/comments/quarantined/{quarantine_id}`](delete_comment_quarantined.md)
- [`POST /rfcs/{rfc_id}/comments/quarantined/{quarantine_id}`](post_comment_quarantined.md)
- [`GET /rfcs/{rfc_id}/comments/{comment_id}`](get_comment.md)
- [`DELETE /rfcs/{rfc_id}/comments/{comment_id}`](delete_comment.md)
- Deprecated aliases: `POST /rfc/{rfc_id}/comment`, `GET /rfc/{rfc_id}/comments`, `GET /rfc/{rfc_id}/comments/quarantined`, `DELETE /rfc/{rfc_id}/comments/quarantined/{quarantine_id}`, `POST /rfc/{rfc_id}/comments/quarantined/{quarantine_id}`, `GET /rfc/{rfc_id}/comment/{comment_id}`, `DELETE /rfc/{rfc_id}/comment/{comment_id}`
