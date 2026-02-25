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

from mdrfc.backend.users import (
    User,
    UserInDB
)

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
    Column("username", String(16), nullable=False),
    Column("email", String(64), nullable=False),
    Column("password_argon2", String(256), nullable=False),
    Column("created_at", DateTime, nullable=False)
)

rfcs = Table(
    "rfcs",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("content", String(4096), nullable=False)
)

rfc_comments = Table(
    "rfc_comments",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("rfc_id", Integer, ForeignKey("rfcs.id"), nullable=False),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("content", String(2048), nullable=False)
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
) -> None:
    """
    Attempt to register the provided user to the database.
    """
    if await user_in_db(user.username):
        raise HTTPException(
            status_code=400,
            detail="username already taken"
        )

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                "INSERT INTO users(username, email, password_argon2, created_at) VALUES($1, $2, $3, $4)",
                user.username,
                user.email,
                user.password_argon2,
                user.created_at
            )