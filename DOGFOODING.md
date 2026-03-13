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
  - [Acknowledgements](#acknowledgements)
  - [References](#references)

## Version

0.1.0 (March 12, 2026)

## Abstract

Requests for Comment (RFCs) have been a core part of internet development throughout its entire history. The ability to submit a document for public review by other professionals is a powerful tool in any field, especially technology and software. Though RFCs have been around for decades, the core technology has stayed largely unchanged--documents are stored and rendered mostly as plain text. In recent years--especially since the rise of LLMs--Markdown has become the ideal format for structured text documents, especially in software engineering. MDRFC brings RFCs into 2026 by providing a simple-yet-extensible template for hosting Markdown-formatted RFCs, either within an organization or open to the public.

## Architectural Overview

MDRFC follows a client-server architecture model, using HTTP(S) for network transport. An MDRFC server hosts RFC documents, their associated revisions, and comments from authorized users. An MDRFC client can connect to an MDRFC server, fetch existing RFCs/revisions/comments, and enable authorized clients to post new RFC documents or revisions. 

## Data Models

This section describes the various object schemas used in MDRFC.

### RFC Documents

Documents in MDRFC are core Markdown documents and their associated metadata--title, author, revisions, etc. An individual RFC document MUST be representable by the following JSON schema:

```json
{
  "id": int, // the unique ID of this RFC
  "author_name_last": string,
  "author_name_first": string,
  "created_at": string, // UTC timestamp as string
  "updated_at": string, // UTC timestamp as string
  "title": string,
  "slug": string,
  "status": string, // MUST be one of "draft", "open", "accepted", "rejected"
  "content": string, // the Markdown document content itself
  "summary": string,
  "revisions": array, // array of revision UUIDs (string)
  "current_revision": string, // UUID as string
  "agent_contributions": object, // keys are revision IDs (UUID as string), values are arrays of agent contributor names (string)
}
```

### RFC Comments

Comments in MDRFC are associated with a specific RFC document, and can be posted by any authorized user of the server. Comments MAY contain replies, and any comment MAY be replied to. An individual comment MUST be representable by the following JSON schema:

```json
{
  "id": int, // the unique ID of this comment
  "parent_id": int?, // the ID of the comment this is a reply to, if applicable
  "rfc_id": int, // the ID of the RFC this is a comment on
  "created_at": string, // UTC timestamp as string
  "content": string, // the comment content itself
  "author_name_last": string,
  "author_name_first": string
}
```

### RFC Revisions

Revisions in MDRFC are specific snapshots of an RFC document in its current state. Each document MUST have at least one associated revision (the initial version). The corresponding document MUST be equal to its most recent revision. An individual revision MUST be representable by the following JSON schema:

```json
{
  "id": string, // unique ID of this revision (UUID as string)
  "rfc_id": int, // the ID of the RFC this is a revision of
  "created_at": string, // UTC timestamp as string
  "author_name_last": string,
  "author_name_first": string,
  "agent_contributors": array, // array of agent contributor names (string)
  "title": string,
  "slug": string,
  "status": string, // MUST be one of "draft", "open", "accepted", "rejected"
  "content": string, // the Markdown document content itself
  "summary": string,
  "message": string // the message associated with this revision
}
```

### Users

An MDRFC user is an authorized client for a given server with permission to post documents, comments, and revisions. An individual user MUST be representable by the following JSON schema:

```json
{
  "id": int, // the unique ID of this user
  "username": string, // the unique username of this user
  "email": string, // user's email address
  "name_last": string,
  "name_first": string,
  "created_at": string // UTC timestamp as string
}
```

## Acknowledgements

I would like to thank Ryan Heaton (ryan@charon-labs.com) and Will Hahn (will@charon-labs.com), who were instrumental in helping me develop and formalize the MDRFC specification.

## References

- GitHub repository: https://github.com/addisonkline/mdrfc