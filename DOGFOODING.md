# MDRFC: Hosting and Serving Markdown-based RFC Documents

## Table of Contents
- [MDRFC: Hosting and Serving Markdown-based RFC Documents](#mdrfc-hosting-and-serving-markdown-based-rfc-documents)
  - [Table of Contents](#table-of-contents)
  - [Version](#version)
  - [Abstract](#abstract)
  - [Architectural Overview](#architectural-overview)
  - [Data Models](#data-models)
    - [RFC Documents](#rfc-documents)
    - [RFC Comments](#rfc-comments)
    - [RFC Revisions](#rfc-revisions)
    - [Users](#users)
  - [RFC Lifecycle](#rfc-lifecycle)
    - [Posting an RFC](#posting-an-rfc)
    - [Feedback](#feedback)
    - [Revising an RFC](#revising-an-rfc)
    - [Admin Review](#admin-review)
  - [Client Interfacing](#client-interfacing)
    - [Server Administrators](#server-administrators)
    - [Human Users](#human-users)
    - [Agentic Assistants](#agentic-assistants)
  - [Acknowledgements](#acknowledgements)
  - [References](#references)

## Version

0.2.0 (March 18, 2026)

## Abstract

Requests for Comment (RFCs) have been a core part of internet development throughout its entire history. The ability to submit a document for public review by other professionals is a powerful tool in any field, especially technology and software. Though RFCs have been around for decades, the core technology has stayed largely unchanged--documents are stored and rendered mostly as plain text. In recent years--especially since the rise of LLMs--Markdown has become the ideal format for structured text documents, especially in software engineering. MDRFC brings RFCs into 2026 by providing a simple-yet-extensible template for hosting Markdown-formatted RFCs, either within an organization or open to the public.

## Architectural Overview

MDRFC follows a client-server architecture model, using HTTP(S) for network transport. An MDRFC server hosts RFC documents, their associated revisions, and comments from authorized users. An MDRFC client can connect to an MDRFC server, fetch existing RFCs/revisions/comments, and enable authorized clients to post new RFC documents or revisions. 

## Data Models

This section describes the various object schemas used in MDRFC.

### RFC Documents

Documents in MDRFC are core Markdown documents and their associated metadata--title, author, revisions, etc. An individual RFC document MUST be representable by the following Python-style schema:

```python
{
  "id": int, # the unique ID of this RFC
  "author_name_last": str,
  "author_name_first": str,
  "created_at": datetime,
  "updated_at": datetime,
  "title": str,
  "slug": str,
  "status": Literal["draft", "open", "accepted", "rejected"],
  "content": str, # the Markdown document content itself
  "summary": str,
  "revisions": list[UUID],
  "current_revision": UUID, 
  "agent_contributions": dict[UUID, str]
}
```

### RFC Comments

Comments in MDRFC are associated with a specific RFC document, and can be posted by any authorized user of the server. Comments MAY contain replies, and any comment MAY be replied to. An individual comment MUST be representable by the following Python-style schema:

```python
{
  "id": int, # the unique ID of this comment
  "parent_id": int | None, # the ID of the comment this is a reply to, if applicable
  "rfc_id": int, # the ID of the RFC this is a comment on
  "created_at": datetime, 
  "content": str, # the comment content itself
  "author_name_last": str,
  "author_name_first": str
}
```

### RFC Revisions

Revisions in MDRFC are specific snapshots of an RFC document in its current state. Each document MUST have at least one associated revision (the initial version). The corresponding document MUST be equal to its most recent revision. An individual revision MUST be representable by the following Python-style schema:

```python
{
  "id": UUID, # unique ID of this revision
  "rfc_id": int, # the ID of the RFC this is a revision of
  "created_at": datetime,
  "author_name_last": str,
  "author_name_first": str,
  "agent_contributors": list[str],
  "title": str,
  "slug": str,
  "status": Literal["draft", "open", "accepted", "rejected"],
  "content": str, # the Markdown document content itself
  "summary": str,
  "message": str # the message associated with this revision
}
```

### Users

An MDRFC user is an authorized client for a given server with permission to post documents, comments, and revisions. An individual user MUST be representable by the following Python-style schema:

```python
{
  "id": int, # the unique ID of this user
  "username": str, # the unique username of this user
  "email": str, # user's email address
  "name_last": str,
  "name_first": str,
  "created_at": datetime,
  "is_admin": bool,
}
```

## RFC Lifecycle

The general lifecycle for a given RFC is the following:
1. A user posts a new RFC with status `draft` or `open`
2. Other users provide feedback on the RFC through comments
3. The original user revises the RFC using the received feedback
4. Repeat steps 2 and 3 *x* times
5. After review, A server administrator updates the RFC status to `accepted` or `rejected`

### Posting an RFC

Any authenticated user MAY upload a new RFC document to the server. The client's request MUST include the following body parameters:
- `title` (string): The title for this RFC.
- `slug` (string): The slug-style string for this RFC.
- `status` (`draft`|`open`): The initial status of this RFC.
- `content` (string): The raw Markdown content of the RFC document.
- `summary` (string): A short description of this RFC.

Slugs MUST be unique to a single RFC; titles SHOULD be unique (though this is not enforced).

### Feedback

After a new RFC is posted, any authenticated user MAY post a comment. Said comment MAY be a reply to another existing comment on the same RFC. Any given user MAY comment on their own RFC.

Feedback provided in comments SHOULD be helpful and productive, and said feedback SHOULD inform future revision(s) to the original RFC.

### Revising an RFC

An authenticated user MAY revise an existing RFC that they previously posted. Revisions MAY be used to update an RFC's `title`, `slug`, `status`, `content`, or `summary`. All revisions MUST include a `message` (string) describing the actions performed in this revision.

Non-admin users MAY NOT update an RFC's status to `accepted` or `rejected`.

### Admin Review

Once an author believes their RFC is ready for final review, they SHOULD request a formal final review from a server administrator. The reviewing admin MUST change the RFC's status to either `accepted` or `rejected`, depending on whether is deemed acceptable. 

Once an RFC's status is `accepted` or `rejected`, it MAY NOT be revised; any follow-up content SHOULD be submitted in a new RFC.

## Client Interfacing

MDRFC expects three discrete types of client end-users: 
1. Server administrators
2. Human users
3. Agentic assistants

### Server Administrators

Server administrators are clients of an MDRFC server with explicit permissions beyond those of the standard user. Admins SHOULD have the final say in updating an RFC's status to `accepted` or `rejected`. Admins SHOULD have access to soft-deleted RFC documents and comments, either to restore or permanently delete them.

### Human Users

Human users are the primary intended target of MDRFC. They SHOULD obtain credentials from an MDRFC server in the form of a bearer token. This bearer token MUST encode the user's username and MAY encode other associated information. To post a new RFC, comment, or revision, users SHOULD be required to include this token in their request.

Unauthenticated human users MAY access RFC documents set to `public`, but MAY NOT post new RFCs, comments, or revisions.

### Agentic Assistants

MDRFC allows for agentic contributions on individual RFC documents and revisions. Human users MAY list contributing agents by name in any given revision.

Non-human AI users MUST NOT impersonate human users; the [User](#users) schema is intended for humans and includes fields such as email, first name, and last name.

## Acknowledgements

I would like to thank Ryan Heaton (ryan@charon-labs.com) and Will Hahn (will@charon-labs.com), who were instrumental in helping me develop and formalize the MDRFC specification.

## References

- GitHub repository: https://github.com/addisonkline/mdrfc