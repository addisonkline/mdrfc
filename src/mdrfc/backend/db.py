from datetime import datetime
from os import getenv
from typing import Any

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
    RFCDocumentUpdate,
)
from mdrfc.backend.comment import RFCComment, RFCCommentWithAuthor


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
    Column("username", String(consts.LEN_USERNAME), nullable=False, unique=True),
    Column("email", String(consts.LEN_EMAIL), nullable=False, unique=True),
    Column("name_last", String(consts.LEN_NAME_LAST), nullable=False),
    Column("name_first", String(consts.LEN_NAME_FIRST), nullable=False),
    Column("password_argon2", String(consts.LEN_PASSWORD_ARGON2), nullable=False),
    Column("is_verified", Boolean, nullable=False),
    Column("verified_at", DateTime, nullable=True),
    Column("verification_token_hash", String(consts.LEN_VERIFICATION_TOKEN_HASH), nullable=True),
    Column("verification_token_expires_at", DateTime, nullable=True),
    Column("created_at", DateTime, nullable=False)
)

rfcs = Table(
    "rfcs",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    Column("title", String(consts.LEN_RFC_TITLE), nullable=False),
    Column("slug", String(consts.LEN_RFC_SLUG), nullable=False),
    Column("status", String(consts.LEN_RFC_STATUS), nullable=False),
    Column("content", String(consts.LEN_RFC_CONTENT), nullable=False),
    Column("summary", String(consts.LEN_RFC_SUMMARY), nullable=False)
)

rfc_comments = Table(
    "rfc_comments",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("parent_id", Integer, ForeignKey("rfc_comments.id", ondelete="CASCADE"), nullable=True),
    Column("rfc_id", Integer, ForeignKey("rfcs.id"), nullable=False),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("content", String(consts.LEN_COMMENT_CONTENT), nullable=False)
)


# asyncpg connection pool for this module 
_pool: asyncpg.Pool = None

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
                    "INSERT INTO users(username, email, name_last, name_first, password_argon2, is_verified, verified_at, verification_token_hash, verification_token_expires_at, created_at) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING id",
                    user.username,
                    user.email,
                    user.name_last,
                    user.name_first,
                    user.password_argon2,
                    user.is_verified,
                    user.verified_at,
                    user.verification_token_hash,
                    user.verification_token_expires_at,
                    user.created_at
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
                        summary=rfc.get("summary")
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
            return await connection.fetchval(
                "INSERT INTO rfcs(created_by, created_at, updated_at, title, slug, status, content, summary) VALUES($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id",
                document.created_by,
                document.created_at,
                document.updated_at,
                document.title,
                document.slug,
                document.status,
                document.content,
                document.summary
            )
        

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
            )
        

async def patch_rfc_in_db(
    rfc_id: int,
    user: User,
    update: RFCDocumentUpdate
) -> RFCDocument | None:
    """
    Attempt to update an existing RFC document in the database.
    The user updating must be the same as the original author.
    """
    if not await check_user_created_rfc(
        user=user,
        rfc_id=rfc_id,
    ):
        raise HTTPException(
            status_code=401,
            detail="unauthorized to modify this RFC"
        )

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            updates: dict[str, Any] = {}
            if update.title is not None:
                updates["title"] = update.title
            if update.slug is not None:
                updates["slug"] = update.slug
            if update.status is not None:
                updates["status"] = update.status
            if update.content is not None:
                updates["content"] = update.content
            if update.summary is not None:
                updates["summary"] = update.summary
            if not updates:
                return None
            updates["updated_at"] = datetime.now()
            
            set_clauses: list[str] = []
            args: list = []
            param_num = 1
            for column, value in updates.items():
                set_clauses.append(f"{column} = ${param_num}")
                args.append(value)
                param_num += 1

            args.append(rfc_id)
            where_clause = f"WHERE id = ${param_num}"

            query = f"UPDATE rfcs SET {', '.join(set_clauses)} {where_clause} RETURNING *"
            updated_rfc = await connection.fetchrow(
                query, *args
            )

            if updated_rfc is None:
                return None
            creator = await get_user_by_id(updated_rfc.get("created_by"))
            if creator is None:
                return None
            return RFCDocument(
                id=updated_rfc.get("id"),
                author_name_last=creator.name_last,
                author_name_first=creator.name_first,
                created_at=updated_rfc.get("created_at"),
                updated_at=updated_rfc.get("updated_at"),
                title=updated_rfc.get("title"),
                slug=updated_rfc.get("slug"),
                status=updated_rfc.get("status"),
                content=updated_rfc.get("content"),
                summary=updated_rfc.get("summary")
            )
        

async def register_comment_in_db(
    comment: RFCComment,
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
            return RFCComment(**result)
        

async def get_rfc_comments_from_db(
    rfc_id: int,
) -> list[RFCCommentWithAuthor]:
    """
    Attempt to fetch all comments on the RFC with the given ID from the database,
    including author names.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch(
                """
                SELECT
                    c.id,
                    c.parent_id,
                    c.created_at,
                    c.content,
                    u.name_first AS author_name_first,
                    u.name_last AS author_name_last
                FROM rfc_comments AS c
                JOIN users AS u ON c.created_by = u.id
                WHERE c.rfc_id = $1
                ORDER BY c.created_at ASC, c.id ASC
                """,
                rfc_id
            )
            comments: list[RFCCommentWithAuthor] = []
            for comment in result:
                comments.append(RFCCommentWithAuthor(**comment))
            return comments
            

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
