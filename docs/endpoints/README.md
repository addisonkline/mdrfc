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
- [`POST /rfc`](post_rfc.md)
- [`GET /rfc/{rfc_id}`](get_rfc.md)
- `GET /rfc/{rfc_id}/rev/current` is an alias for `GET /rfc/{rfc_id}`
- [`DELETE /rfc/{rfc_id}`](delete_rfc.md)

## Revisions

- [`GET /rfc/{rfc_id}/revs`](get_revs.md)
- [`GET /rfc/{rfc_id}/rev/{rev_id}`](get_rev.md)
- [`POST /rfc/{rfc_id}/rev`](post_rev.md)

## Comments

- [`POST /rfc/{rfc_id}/comment`](post_comment.md)
- [`GET /rfc/{rfc_id}/comments`](get_comments.md)
- [`GET /rfc/{rfc_id}/comments/quarantined`](get_comments_quarantined.md)
- [`DELETE /rfc/{rfc_id}/comments/quarantined/{quarantine_id}`](delete_comment_quarantined.md)
- [`POST /rfc/{rfc_id}/comments/quarantined/{quarantine_id}`](post_comment_quarantined.md)
- [`GET /rfc/{rfc_id}/comment/{comment_id}`](get_comment.md)
- [`DELETE /rfc/{rfc_id}/comment/{comment_id}`](delete_comment.md)
