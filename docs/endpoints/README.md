# MDRFC Server Endpoints

This directory contains documentation for all endpoints supported by the MDRFC HTTP server.

## Basic Endpoints

- [`GET /`](/docs/endpoints/get_root.md): Obtain basic server information and metadata.

## Authentication Endpoints

- [`POST /login`](/docs/endpoints/post_login.md): Log in to obtain a temporary access token. 
- [`POST /signup`](/docs/endpoints/post_signup.md): Sign up and create an (unverified) account.
- [`POST /verify-email`](/docs/endpoints/post_verify_email.md): Verify an existing account to enable user access.

## RFC Endpoints

- [`GET /rfcs`](/docs/endpoints/get_rfcs.md): Get all existing RFC documents.
- [`GET /rfc/{rfc_id}`](/docs/endpoints/get_rfc.md): Get a specific RFC document by ID.
- [`POST /rfc`](/docs/endpoints/post_rfc.md): Add a new RFC to this server.

## Revision Endpoints

- [`GET /rfc/{rfc_id}/revs`](/docs/endpoints/get_revs.md): Get all existing revisions for a given RFC.
- [`GET /rfc/{rfc_id}/rev/{revision_id}`](/docs/endpoints/get_rev.md): Get a specific revision for a given RFC.
- [`POST /rfc/{rfc_id}/rev`](/docs/endpoints/post_rev.md): Create a new revision on an existing RFC.

## Comment Endpoints

- [`GET /rfc/{rfc_id}/comments`](/docs/endpoints/get_comments.md): Get all existing comments on a given RFC.
- [`GET /rfc/{rfc_id}/comment/{comment_id}`](/docs/endpoints/get_comment.md): Get a specific comment on a given RFC.
- [`POST /rfc/{rfc_id}/comment`](/docs/endpoints/post_comment.md): Post a new comment on an existing RFC.