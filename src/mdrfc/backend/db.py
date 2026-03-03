from os import getenv

from fastapi import HTTPException
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
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
    RFCDocumentSummary,
)
from mdrfc.backend.comment import RFCComment


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
    Column("password_argon2", String(consts.LEN_PASSWORD_ARGON2), nullable=False),
    Column("created_at", DateTime, nullable=False)
)

rfcs = Table(
    "rfcs",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime, nullable=False),
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
            result = await connection.fetchval("SELECT id FROM users WHERE username = $1", username)
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
            result = await connection.fetchrow("SELECT * FROM users WHERE username = $1", username)
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
                result = await connection.fetchval(
                    "INSERT INTO users(username, email, password_argon2, created_at) VALUES($1, $2, $3, $4) RETURNING id",
                    user.username,
                    user.email,
                    user.password_argon2,
                    user.created_at
                )
                return result
            except asyncpg.UniqueViolationError as e:
                if e.constraint_name == "uq_users_username":
                    raise HTTPException(status_code=409, detail="username already taken")
                elif e.constraint_name == "uq_users_email":
                    raise HTTPException(status_code=409, detail="email already taken")
                raise


async def get_rfcs_from_db() -> list[RFCDocumentSummary] | None:
    """
    Get all RFCs from the database, or `None` if there are none.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch(
                "SELECT id, created_by, created_at, summary FROM rfcs"
            )
            if result is None:
                return None
            else:
                summaries: list[RFCDocumentSummary] = []
                for summary in result:
                    summaries.append(RFCDocumentSummary(**summary))
                return summaries



async def register_rfc_in_db(
    document: RFCDocument
) -> int:
    """
    Attempt to register a new RFC document in the database.
    Returns the ID of the new RFC.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            return await connection.fetchval(
                "INSERT INTO rfcs(created_by, created_at, content, summary) VALUES($1, $2, $3, $4) RETURNING id",
                document.created_by,
                document.created_at,
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
            result = await connection.fetchrow(
                "SELECT * FROM rfcs WHERE id = $1",
                rfc_id
            )
            if result is None:
                return None
            return RFCDocument(**result)
        

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
) -> list[RFCComment]:
    """
    Attempt to fetch all comments on the RFC with the given ID from the database.
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
            else:
                comments: list[RFCComment] = []
                for comment in result:
                    comments.append(RFCComment(**comment))
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