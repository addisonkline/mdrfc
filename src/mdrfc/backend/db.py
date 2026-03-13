from datetime import datetime
import json
from os import getenv
from typing import Any
import uuid

from fastapi import HTTPException
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    Boolean,
    String,
    DateTime,
    ForeignKey,
    UUID,
    ARRAY,
    JSON
)
import asyncpg # type: ignore
import dotenv

from mdrfc.backend import constants as consts
from mdrfc.backend.users import (
    User,
    UserInDB
)
from mdrfc.backend.document import (
    RFCDocument,
    RFCDocumentInDB,
    RFCDocumentSummary,
    RFCRevision,
    RFCRevisionInDB,
    RFCRevisionRequest,
    RFCRevisionSummary
)
from mdrfc.backend.comment import RFCComment, RFCCommentInDB


# load DSN from env
dotenv.load_dotenv()
DSN = getenv("DATABASE_URL")
if DSN is None:
    raise RuntimeError("environment variable DATABASE_URL is required but was not found")


# sqlalchemy metadata
metadata_obj = MetaData()

users = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String(consts.LEN_USERNAME_MAX), nullable=False, unique=True),
    Column("email", String(consts.LEN_EMAIL_MAX), nullable=False, unique=True),
    Column("name_last", String(consts.LEN_NAME_LAST_MAX), nullable=False),
    Column("name_first", String(consts.LEN_NAME_FIRST_MAX), nullable=False),
    Column("password_argon2", String(consts.LEN_PASSWORD_ARGON2), nullable=False),
    Column("is_verified", Boolean, nullable=False),
    Column("verified_at", DateTime, nullable=True),
    Column("verification_token_hash", String(consts.LEN_VERIFICATION_TOKEN_HASH), nullable=True),
    Column("verification_token_expires_at", DateTime, nullable=True),
    Column("created_at", DateTime, nullable=False),
    Column("is_admin", Boolean, nullable=True)
)

rfcs = Table(
    "rfcs",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("title", String(consts.LEN_RFC_TITLE_MAX), nullable=False),
    Column("slug", String(consts.LEN_RFC_SLUG_MAX), nullable=False),
    Column("status", String(consts.LEN_RFC_STATUS_MAX), nullable=False),
    Column("content", String(consts.LEN_RFC_CONTENT_MAX), nullable=False),
    Column("summary", String(consts.LEN_RFC_SUMMARY_MAX), nullable=False),
    Column("revisions", ARRAY(UUID), nullable=False),
    Column("current_revision", UUID, ForeignKey("rfc_revisions.id"), nullable=False),
    Column("agent_contributions", JSON, nullable=False),
    Column("is_public", Boolean, nullable=True, default=False)
)

rfc_comments = Table(
    "rfc_comments",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("parent_id", Integer, ForeignKey("rfc_comments.id", ondelete="CASCADE"), nullable=True),
    Column("rfc_id", Integer, ForeignKey("rfcs.id"), nullable=False),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("content", String(consts.LEN_COMMENT_CONTENT_MAX), nullable=False),
)

rfc_revisions = Table(
    "rfc_revisions",
    metadata_obj,
    Column("id", UUID, primary_key=True),
    Column("rfc_id", Integer, ForeignKey("rfcs.id"), nullable=False),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("agent_contributors", ARRAY(String), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("title", String(consts.LEN_RFC_TITLE_MAX), nullable=False),
    Column("slug", String(consts.LEN_RFC_SLUG_MAX), nullable=False),
    Column("status", String(consts.LEN_RFC_STATUS_MAX), nullable=False),
    Column("content", String(consts.LEN_RFC_CONTENT_MAX), nullable=False),
    Column("summary", String(consts.LEN_RFC_SUMMARY_MAX), nullable=False),
    Column("is_public", Boolean, nullable=True, default=False),
    Column("message", String(consts.LEN_REVISION_MSG_MAX), nullable=False)
)


# asyncpg connection pool for this module 
_pool: asyncpg.Pool = None


def _serialize_agent_contributions(
    agent_contributions: dict[uuid.UUID, list[str]],
) -> str:
    return json.dumps(
        {str(revision_id): contributors for revision_id, contributors in agent_contributions.items()}
    )


def _deserialize_agent_contributions(
    agent_contributions: Any,
) -> dict[uuid.UUID, list[str]]:
    if isinstance(agent_contributions, str):
        raw = json.loads(agent_contributions)
    else:
        raw = agent_contributions
    return {
        uuid.UUID(revision_id): contributors
        for revision_id, contributors in raw.items()
    }

async def init_db():
    """
    Initialize the DB connection.
    This is called on server startup.
    """
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=DSN,
    )


async def close_db():
    """
    Close the existing DB connection.
    This is called on server shutdown.
    """
    global _pool
    await _pool.close()


#
# AUTH functions
#
async def user_in_db(
    username: str,
) -> bool:
    """
    Determine if a user with the given username exists in the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchval(
                "SELECT id FROM users WHERE LOWER(username) = LOWER($1)",
                username,
            )
            return (result is not None)
        

async def get_user_from_db(
    username: str,
) -> UserInDB | None:
    """
    Get the user with the given username from the database, or `None` if none exists.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow(
                "SELECT * FROM users WHERE LOWER(username) = LOWER($1)",
                username,
            )
            if result is None:
                return None
            return UserInDB(**result)
        

async def get_user_by_id(
    id: int,
) -> UserInDB | None:
    """
    Get the user with the given ID from the database, or `None` if none exists.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                id,
            )
            if result is None:
                return None
            return UserInDB(**result)
        

async def register_user_in_db(
    user: UserInDB
) -> int:
    """
    Attempt to register the provided user to the database.
    Returns the ID of the new user.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            try:
                existing_user = await connection.fetchval(
                    """
                    SELECT id
                    FROM users
                    WHERE LOWER(username) = LOWER($1)
                       OR LOWER(email) = LOWER($2)
                    """,
                    user.username,
                    user.email,
                )
                if existing_user is not None:
                    raise HTTPException(status_code=409, detail="account could not be created")

                result = await connection.fetchval(
                    "INSERT INTO users(username, email, name_last, name_first, password_argon2, is_verified, verified_at, verification_token_hash, verification_token_expires_at, created_at, is_admin) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING id",
                    user.username,
                    user.email,
                    user.name_last,
                    user.name_first,
                    user.password_argon2,
                    user.is_verified,
                    user.verified_at,
                    user.verification_token_hash,
                    user.verification_token_expires_at,
                    user.created_at,
                    False
                )
                return result
            except asyncpg.UniqueViolationError as e:
                raise HTTPException(status_code=409, detail="account could not be created") from e


async def verify_user_by_token_in_db(
    verification_token_hash: str,
    verified_at: datetime,
) -> UserInDB | None:
    """
    Verify a user identified by a pending email verification token.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow(
                """
                UPDATE users
                SET is_verified = TRUE,
                    verified_at = $2,
                    verification_token_hash = NULL,
                    verification_token_expires_at = NULL
                WHERE verification_token_hash = $1
                  AND is_verified = FALSE
                  AND verification_token_expires_at IS NOT NULL
                  AND verification_token_expires_at >= $2
                RETURNING *
                """,
                verification_token_hash,
                verified_at,
            )
            if result is None:
                return None
            return UserInDB(**result)

#
# RFC functions
#
async def get_rfcs_from_db() -> list[RFCDocumentSummary] | None:
    """
    Get all RFCs from the database, or `None` if there are none.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            rfcs_in_db = await connection.fetch(
                "SELECT * FROM rfcs"
            )
            if rfcs_in_db is None:
                return None
            else:
                summaries: list[RFCDocumentSummary] = []
                for rfc in rfcs_in_db:
                    user = await get_user_by_id(rfc.get("created_by"))
                    if user is None:
                        continue
                    summary = RFCDocumentSummary(
                        id=rfc.get("id"),
                        author_name_last=user.name_last,
                        author_name_first=user.name_first,
                        created_at=rfc.get("created_at"),
                        updated_at=rfc.get("updated_at"),
                        title=rfc.get("title"),
                        slug=rfc.get("slug"),
                        status=rfc.get("status"),
                        summary=rfc.get("summary"),
                        public=rfc.get("is_public") or False,
                    )
                    summaries.append(summary)
                return summaries



async def register_rfc_in_db(
    document: RFCDocumentInDB
) -> int:
    """
    Attempt to register a new RFC document in the database.
    Returns the ID of the new RFC.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query = """
            WITH rfc_insert AS (
                INSERT INTO rfcs (
                    created_by, created_at, updated_at,
                    title, slug, status, content, summary,
                    revisions, current_revision, agent_contributions
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id
            ), revision_insert AS (
                INSERT INTO rfc_revisions (
                    id, rfc_id, created_by, agent_contributors, created_at,
                    title, slug, status, content, summary, message
                )
                SELECT
                    $10, id, $1, $12, $2,
                    $4, $5, $6, $7, $8, $13
                FROM rfc_insert
                RETURNING rfc_id
            )
            SELECT id FROM rfc_insert;
            """
            rfc_id = await connection.fetchval(
                query,
                document.created_by,
                document.created_at,
                document.updated_at,
                document.title,
                document.slug,
                document.status,
                document.content,
                document.summary,
                document.revisions,
                document.current_revision,
                _serialize_agent_contributions(document.agent_contributions),
                document.agent_contributions.get(document.current_revision, []),
                "First revision"
            )
            if rfc_id is None:
                raise HTTPException(
                    status_code=500,
                    detail="got rfc_id = None"
                )
            return rfc_id
        

async def get_rfc_from_db(
    rfc_id: int
) -> RFCDocument | None:
    """
    Attempt to fetch the RFC document with the given ID from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            rfc = await connection.fetchrow(
                "SELECT * FROM rfcs WHERE id = $1",
                rfc_id
            )
            if rfc is None:
                return None
            creator = await get_user_by_id(rfc.get("created_by"))
            if creator is None:
                return None
            return RFCDocument(
                id=rfc.get("id"),
                author_name_last=creator.name_last,
                author_name_first=creator.name_first,
                created_at=rfc.get("created_at"),
                updated_at=rfc.get("updated_at"),
                title=rfc.get("title"),
                slug=rfc.get("slug"),
                status=rfc.get("status"),
                summary=rfc.get("summary"),
                content=rfc.get("content"),
                revisions=rfc.get("revisions"),
                current_revision=rfc.get("current_revision"),
                agent_contributions=_deserialize_agent_contributions(rfc.get("agent_contributions")),
                public=rfc.get("is_public") or False,
            )


#
# REVISION functions
#
async def get_revisions_from_db(
    rfc_id: int
) -> list[RFCRevisionSummary] | None:
    """
    Attempt to get a list of all revisions for the existing RFC from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            revisions_in_db = await connection.fetch(
                "SELECT * FROM rfc_revisions WHERE rfc_id = $1",
                rfc_id
            )
            if revisions_in_db is None:
                return None
            summaries: list[RFCRevisionSummary] = []
            for rev in revisions_in_db:
                user = await get_user_by_id(rev.get("created_by"))
                if user is None:
                    continue
                summary = RFCRevisionSummary(
                    id=rev.get("id"),
                    rfc_id=rev.get("rfc_id"),
                    created_at=rev.get("created_at"),
                    author_name_last=user.name_last,
                    author_name_first=user.name_first,
                    agent_contributors=rev.get("agent_contributors"),
                    message=rev.get("message")
                )
                summaries.append(summary)
            return summaries
        

async def get_revision_from_db(
    rfc_id: int,
    revision_id: str,
) -> RFCRevision | None:
    """
    Attempt to fetch the specified revision from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            rev = await connection.fetchrow(
                "SELECT * FROM rfc_revisions WHERE id = $1 AND rfc_id = $2",
                revision_id,
                rfc_id
            )
            if rev is None:
                return None
            creator = await get_user_by_id(rev.get("created_by"))
            if creator is None:
                return None
            return RFCRevision(
                id=rev.get("id"),
                rfc_id=rev.get("rfc_id"),
                created_at=rev.get("created_at"),
                author_name_last=creator.name_last,
                author_name_first=creator.name_first,
                agent_contributors=rev.get("agent_contributors"),
                title=rev.get("title"),
                slug=rev.get("slug"),
                status=rev.get("status"),
                content=rev.get("content"),
                summary=rev.get("summary"),
                message=rev.get("message")
            )
        

async def register_revision_in_db(
    rfc_id: int,
    user: User,
    request: RFCRevisionInDB,
    new_revisions: list[uuid.UUID],
    new_contributions: dict[uuid.UUID, list[str]]
) -> RFCRevision | None:
    """
    Attempt to register a new revision for the specified, existing RFC document in the database.
    """
    if not await check_user_created_rfc(user, rfc_id):
        raise HTTPException(
            status_code=401,
            detail="unauthorized to revise this RFC"
        )

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query = """
            WITH revision_insert AS (
                INSERT INTO rfc_revisions (
                    id, rfc_id, created_at, created_by, agent_contributors,
                    title, slug, status, content, summary, message
                )
                VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
            ), rfc_update AS (
                UPDATE rfcs
                SET updated_at = $3,
                    title = $6,
                    slug = $7,
                    status = $8,
                    content = $9,
                    summary = $10,
                    revisions = $12,
                    current_revision = $1,
                    agent_contributions = $13
                WHERE id = $2
                RETURNING id
            )
            SELECT * FROM revision_insert;
            """
            rev = await connection.fetchrow(
                query,
                request.id,
                rfc_id,
                request.created_at,
                request.created_by,
                request.agent_contributors,
                request.title,
                request.slug,
                request.status,
                request.content,
                request.summary,
                request.message,
                new_revisions,
                _serialize_agent_contributions(new_contributions)
            )
            if rev is None:
                return None
            creator = await get_user_by_id(request.created_by)
            if creator is None:
                return None
            return RFCRevision(
                id=rev.get("id"),
                rfc_id=rev.get("rfc_id"),
                created_at=rev.get("created_at"),
                author_name_last=creator.name_last,
                author_name_first=creator.name_first,
                agent_contributors=rev.get("agent_contributors"),
                title=rev.get("title"),
                slug=rev.get("slug"),
                status=rev.get("status"),
                content=rev.get("content"),
                summary=rev.get("summary"),
                message=rev.get("message")
            )


#
# COMMENT functions
#
async def register_comment_in_db(
    comment: RFCCommentInDB,
) -> int:
    """
    Attempt to register a new comment on an existing RFC document in the database.
    Returns the ID of the new comment.
    """
    if await get_rfc_from_db(comment.rfc_id) is None:
        raise HTTPException(
            status_code=400,
            detail="can't comment on a nonexistent RFC"
        )
    
    if comment.parent_id is not None:
        if not await check_comment_is_on_rfc(comment.parent_id, comment.rfc_id):
            raise HTTPException(
                status_code=400,
                detail="can't reply to a comment on another RFC"
            )
    
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            try:
                return await connection.fetchval(
                    "INSERT INTO rfc_comments(rfc_id, created_by, created_at, content, parent_id) VALUES($1, $2, $3, $4, $5) RETURNING id",
                    comment.rfc_id,
                    comment.created_by,
                    comment.created_at,
                    comment.content,
                    comment.parent_id
                )
            except asyncpg.ForeignKeyViolationError as e:
                if e.constraint_name == "fk_rfc_comments_parent_id":
                    raise HTTPException(status_code=400, detail="parent comment does not exist")
                raise
        

async def get_comment_from_db(
    comment_id: int,
) -> RFCComment | None:
    """
    Attempt to fetch the comment with the given ID from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow(
                "SELECT * FROM rfc_comments WHERE id = $1",
                comment_id
            )
            if result is None:
                return None
            creator = await get_user_by_id(result.get("created_by"))
            if creator is None:
                return None
            return RFCComment(
                id=result.get("id"),
                parent_id=result.get("parent_id"),
                rfc_id=result.get("rfc_id"),
                created_at=result.get("created_at"),
                content=result.get("content"),
                author_name_last=creator.name_last,
                author_name_first=creator.name_first
            )
        

async def get_rfc_comments_from_db(
    rfc_id: int,
) -> list[RFCComment]:
    """
    Attempt to fetch all comments on the RFC with the given ID from the database,
    including author names.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch(
                "SELECT * FROM rfc_comments WHERE rfc_id = $1",
                rfc_id
            )
            if result is None:
                return []
            comments: list[RFCComment] = []
            for comment in result:
                creator = await get_user_by_id(comment.get("created_by"))
                if creator is None:
                    continue
                comment_obj = RFCComment(
                    id=comment.get("id"),
                    rfc_id=comment.get("rfc_id"),
                    parent_id=comment.get("parent_id"),
                    created_at=comment.get("created_at"),
                    content=comment.get("content"),
                    author_name_last=creator.name_last,
                    author_name_first=creator.name_first
                )
                comments.append(comment_obj)
            return comments

#
# Utility functions         
#
async def check_comment_is_on_rfc(
    comment_id: int,
    rfc_id: int,
) -> bool:
    """
    Check that the comment with the given ID is on the given RFC.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchval(
                "SELECT rfc_id FROM rfc_comments WHERE id = $1",
                comment_id
            )
            if result is None:
                return False
            return (result == rfc_id)


async def check_user_created_rfc(
    user: User,
    rfc_id: int,
) -> bool:
    """
    Check that this user created the RFC with the given ID.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            rfc_author = await connection.fetchval(
                "SELECT created_by FROM rfcs WHERE id = $1",
                rfc_id
            )
            if rfc_author != user.id:
                return False
            return True
