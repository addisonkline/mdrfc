from datetime import datetime, timezone
import json
from os import getenv
from typing import Any, Literal
import uuid

from fastapi import HTTPException
import asyncpg  # type: ignore
import dotenv

from mdrfc.backend import constants as consts
from mdrfc.backend import schema
from mdrfc.backend.users import User, UserInDB
from mdrfc.backend.document import (
    QuarantinedRFCSummary,
    RFCDocument,
    RFCDocumentInDB,
    RFCDocumentSummary,
    RFCReadme,
    RFCReadmeRevision,
    RFCReadmeRevisionInDB,
    RFCReadmeRevisionSummary,
    RFCRevision,
    RFCRevisionInDB,
    RFCRevisionSummary,
)
from mdrfc.backend.comment import QuarantinedComment, RFCComment, RFCCommentInDB


# load DSN from env
dotenv.load_dotenv()
DSN = getenv("DATABASE_URL")
if DSN is None:
    raise RuntimeError(
        "environment variable DATABASE_URL is required but was not found"
    )

metadata_obj = schema.metadata_obj


# asyncpg connection pool for this module
_pool: asyncpg.Pool = None


def _serialize_agent_contributions(
    agent_contributions: dict[uuid.UUID, list[str]],
) -> str:
    return json.dumps(
        {
            str(revision_id): contributors
            for revision_id, contributors in agent_contributions.items()
        }
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
            return result is not None


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


async def register_user_in_db(user: UserInDB) -> int:
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
                    raise HTTPException(
                        status_code=409, detail="account could not be created"
                    )

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
                    False,
                )
                return result
            except asyncpg.UniqueViolationError as e:
                raise HTTPException(
                    status_code=409, detail="account could not be created"
                ) from e


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
async def get_rfcs_readme_in_db() -> RFCReadme | None:
    """
    Get the current RFC README file from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            revisions_in_db = await connection.fetch(
                """
                SELECT id, created_at, content, COALESCE(is_public, FALSE) AS is_public
                FROM readme_revisions
                ORDER BY created_at ASC, id ASC
                """
            )
            if len(revisions_in_db) == 0:
                return None
            first_revision = revisions_in_db[0]
            latest_revision = revisions_in_db[-1]
            return RFCReadme(
                content=latest_revision.get("content"),
                created_at=first_revision.get("created_at"),
                updated_at=latest_revision.get("created_at"),
                current_revision=latest_revision.get("id"),
                revisions=[rev.get("id") for rev in revisions_in_db],
                public=latest_revision.get("is_public") or False,
            )


async def get_rfcs_readme_revs_in_db() -> list[RFCReadmeRevisionSummary]:
    """
    Get all revisions on the RFC README file from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            revs_in_db = await connection.fetch(
                """
                SELECT
                    rr.id AS revision_id,
                    rr.created_at,
                    rr.reason,
                    COALESCE(rr.is_public, FALSE) AS is_public,
                    u.name_last AS created_by_name_last,
                    u.name_first AS created_by_name_first
                FROM readme_revisions AS rr
                JOIN users AS u ON u.id = rr.created_by
                ORDER BY rr.created_at ASC, rr.id ASC
                """
            )
            summaries: list[RFCReadmeRevisionSummary] = []
            for rev in revs_in_db:
                summary = RFCReadmeRevisionSummary(
                    revision_id=rev.get("revision_id"),
                    created_by_name_last=rev.get("created_by_name_last"),
                    created_by_name_first=rev.get("created_by_name_first"),
                    created_at=rev.get("created_at"),
                    reason=rev.get("reason"),
                    public=rev.get("is_public") or False,
                )
                summaries.append(summary)
            return summaries



async def get_rfcs_readme_rev_in_db(
    revision_id: uuid.UUID,
) -> RFCReadmeRevision | None:
    """
    Get a specific revision on the RFC README file from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            rev_in_db = await connection.fetchrow(
                """
                SELECT
                    rr.id AS revision_id,
                    rr.created_at,
                    rr.reason,
                    rr.content,
                    COALESCE(rr.is_public, FALSE) AS is_public,
                    u.name_last AS created_by_name_last,
                    u.name_first AS created_by_name_first
                FROM readme_revisions AS rr
                JOIN users AS u ON u.id = rr.created_by
                WHERE rr.id = $1
                """,
                revision_id,
            )
            if rev_in_db is None:
                return None
            return RFCReadmeRevision(
                revision_id=rev_in_db.get("revision_id"),
                created_at=rev_in_db.get("created_at"),
                created_by_name_last=rev_in_db.get("created_by_name_last"),
                created_by_name_first=rev_in_db.get("created_by_name_first"),
                reason=rev_in_db.get("reason"),
                content=rev_in_db.get("content"),
                public=rev_in_db.get("is_public") or False,
            )


async def register_rfcs_readme_rev_in_db(
    admin: User,
    revision: RFCReadmeRevisionInDB,
) -> RFCReadmeRevision:
    """
    Post a new revision for the RFC README file.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query = """
            INSERT INTO readme_revisions (
                id, created_at, created_by, reason, content, is_public
            )
            VALUES ($1, $2, $3, $4, $5, $6);
            """
            await connection.execute(
                query,
                revision.revision_id,
                revision.created_at,
                revision.created_by,
                revision.reason,
                revision.content,
                revision.public,
            )
            return RFCReadmeRevision(
                revision_id=revision.revision_id,
                created_at=revision.created_at,
                created_by_name_last=admin.name_last,
                created_by_name_first=admin.name_first,
                reason=revision.reason,
                content=revision.content,
                public=revision.public,
            )


async def get_rfcs_from_db(
    quarantine_ok: bool = False,
) -> list[RFCDocumentSummary] | None:
    """
    Get all RFCs from the database, or `None` if there are none.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            rfcs_in_db = await connection.fetch("SELECT * FROM rfcs")
            if rfcs_in_db is None:
                return None
            else:
                summaries: list[RFCDocumentSummary] = []
                for rfc in rfcs_in_db:
                    if rfc.get("is_quarantined") and not quarantine_ok:
                        continue
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


async def get_rfcs_quarantined_from_db() -> list[QuarantinedRFCSummary]:
    """
    Get all RFCs marked as quarantined in the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            quarantined_rfcs = await connection.fetch(
                "SELECT * FROM quarantined_rfcs",
            )
            if quarantined_rfcs is None:
                return []
            else:
                summaries: list[QuarantinedRFCSummary] = []
                for rfc in quarantined_rfcs:
                    rfc_in_db = await get_rfc_from_db(
                        rfc.get("rfc_id"), quarantine_ok=True
                    )
                    if rfc_in_db is None:
                        continue
                    quarantiner = await get_user_by_id(rfc.get("quarantined_by"))
                    if quarantiner is None:
                        continue
                    summary = QuarantinedRFCSummary(
                        quarantine_id=rfc.get("quarantine_id"),
                        quarantined_by_name_last=quarantiner.name_last,
                        quarantined_by_name_first=quarantiner.name_first,
                        quarantined_at=rfc.get("quarantined_at"),
                        reason=rfc.get("reason"),
                        rfc_id=rfc_in_db.id,
                        rfc_title=rfc_in_db.title,
                        rfc_slug=rfc_in_db.slug,
                        rfc_status=rfc_in_db.status,
                        rfc_summary=rfc_in_db.summary,
                    )
                    summaries.append(summary)
                return summaries


async def delete_rfc_from_db(
    quarantine_id: int,
) -> None:
    """
    Fully delete a quarantined RFC from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query = """
            WITH deleted_quarantine AS (
                DELETE FROM quarantined_rfcs
                WHERE quarantine_id = $1
                RETURNING rfc_id
            ), deleted_quarantined_comments AS (
                DELETE FROM quarantined_comments
                WHERE comment_id IN (
                    SELECT id FROM rfc_comments
                    WHERE rfc_id = (SELECT rfc_id FROM deleted_quarantine)
                )
            ), deleted_comments AS (
                DELETE FROM rfc_comments
                WHERE rfc_id = (SELECT rfc_id FROM deleted_quarantine)
            ), deleted_revisions AS (
                DELETE FROM rfc_revisions
                WHERE rfc_id = (SELECT rfc_id FROM deleted_quarantine)
            ), deleted_rfc AS (
                DELETE FROM rfcs
                WHERE id = (SELECT rfc_id FROM deleted_quarantine)
                RETURNING id
            )
            SELECT id FROM deleted_rfc;
            """
            deleted_rfc_id = await connection.fetchval(
                query,
                quarantine_id,
            )
            if deleted_rfc_id is None:
                raise HTTPException(status_code=404, detail="quarantined RFC not found")


async def unquarantine_rfc_in_db(
    quarantine_id: int,
) -> None:
    """
    Unquarantine and republish an RFC in the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query_quarantine = """
            DELETE FROM quarantined_rfcs
            WHERE quarantine_id = $1
            RETURNING rfc_id;
            """
            rfc_id = await connection.fetchval(query_quarantine, quarantine_id)
            if rfc_id is None:
                raise HTTPException(status_code=404, detail="quarantined RFC not found")
            query_rfc = """
            UPDATE rfcs
            SET is_quarantined = FALSE
            WHERE id = $1;
            """
            await connection.execute(
                query_rfc,
                rfc_id,
            )


async def register_rfc_in_db(document: RFCDocumentInDB) -> int:
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
                    revisions, current_revision, agent_contributions, is_public,
                    review_requested, is_reviewed
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $15, $16)
                RETURNING id
            ), revision_insert AS (
                INSERT INTO rfc_revisions (
                    id, rfc_id, created_by, agent_contributors, created_at,
                    title, slug, status, content, summary, is_public, message
                )
                SELECT
                    $10, id, $1, $13, $2,
                    $4, $5, $6, $7, $8, $12, $14
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
                document.public,
                document.agent_contributions.get(document.current_revision, []),
                "First revision",
                False,
                False
            )
            if rfc_id is None:
                raise HTTPException(status_code=500, detail="got rfc_id = None")
            return rfc_id


async def get_rfc_from_db(
    rfc_id: int, quarantine_ok: bool = False
) -> RFCDocument | None:
    """
    Attempt to fetch the RFC document with the given ID from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            rfc = await connection.fetchrow("SELECT * FROM rfcs WHERE id = $1", rfc_id)
            if rfc is None:
                return None
            if rfc.get("is_quarantined") and not quarantine_ok:
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
                agent_contributions=_deserialize_agent_contributions(
                    rfc.get("agent_contributions")
                ),
                public=rfc.get("is_public") or False,
                review_requested=rfc.get("review_requested") or False,
                reviewed=rfc.get("is_reviewed") or False,
                review_reason=rfc.get("review_reason"),
            )


async def quarantine_rfc_in_db(
    rfc_id: int,
    reason: str,
    user: User,
) -> None:
    """
    Soft-delete (quarantine) an existing RFC in the database.
    """
    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(status_code=404, detail="RFC not found")

    if await check_rfc_is_quarantined(rfc_id):
        raise HTTPException(status_code=404, detail="RFC not found")

    if not await check_user_created_rfc(user, rfc_id):
        if not user.is_admin:
            raise HTTPException(status_code=401, detail="cannot delete this RFC")

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query_rfcs = """
            UPDATE rfcs
            SET is_quarantined = TRUE
            WHERE id = $1;
            """
            await connection.execute(query_rfcs, rfc_id)
            query_quarantined = """
            INSERT INTO quarantined_rfcs (
                quarantined_by, quarantined_at, reason, rfc_id
            )
            VALUES($1, $2, $3, $4);
            """
            await connection.execute(
                query_quarantined, user.id, datetime.now(timezone.utc), reason, rfc_id
            )


async def get_rfcs_review_needed_from_db() -> list[RFCDocumentSummary]:
    """
    Fetch all RFC documents from the database where the author has requested admin review.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query = """
            SELECT *
            FROM rfcs
            WHERE review_requested = TRUE;
            """
            rfcs_in_db = await connection.fetch(query)
            if rfcs_in_db is None:
                return []
            summaries: list[RFCDocumentSummary] = []
            for rfc in rfcs_in_db:
                if rfc.get("is_quarantined"):
                    continue
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


async def post_rfc_review_req_in_db(
    rfc_id: int,
    user: User,
) -> None:
    """
    Request that an existing RFC in the database gets admin review.
    """
    if not await check_user_created_rfc(
        user=user,
        rfc_id=rfc_id
    ):
        raise HTTPException(
            status_code=401,
            detail="unauthorized to request review on this RFC"
        )
    
    if not await check_rfc_not_already_requested_review(
        rfc_id=rfc_id
    ):
        raise HTTPException(
            status_code=400,
            detail="RFC already requested review"
        )
    
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query = """
            UPDATE rfcs
            SET review_requested = TRUE
            WHERE id = $1;
            """
            await connection.execute(
                query,
                rfc_id
            )


async def update_rfc_status_in_db(
    rfc_id: int,
    new_status: Literal["accepted", "rejected"],
    reason: str
) -> None:
    """
    Attempt to update an RFC's status to either `accepted` or `rejected` after admin review.
    """
    if await check_rfc_not_already_requested_review(
        rfc_id=rfc_id
    ):
        raise HTTPException(
            status_code=400,
            detail="RFC not open to review"
        )

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query = """
            UPDATE rfcs
            SET status = $1, is_reviewed = TRUE, review_reason = $2
            WHERE id = $3;
            """
            await connection.execute(
                query,
                new_status,
                reason,
                rfc_id
            )


#
# REVISION functions
#
async def get_revisions_from_db(rfc_id: int) -> list[RFCRevisionSummary] | None:
    """
    Attempt to get a list of all revisions for the existing RFC from the database.
    """
    if await check_rfc_is_quarantined(rfc_id):
        return None

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            revisions_in_db = await connection.fetch(
                "SELECT * FROM rfc_revisions WHERE rfc_id = $1", rfc_id
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
                    message=rev.get("message"),
                    public=rev.get("is_public") or False,
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
    if await check_rfc_is_quarantined(rfc_id):
        return None

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            rev = await connection.fetchrow(
                "SELECT * FROM rfc_revisions WHERE id = $1 AND rfc_id = $2",
                revision_id,
                rfc_id,
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
                message=rev.get("message"),
                public=rev.get("is_public") or False,
            )


async def register_revision_in_db(
    rfc_id: int,
    user: User,
    request: RFCRevisionInDB,
    new_revisions: list[uuid.UUID],
    new_contributions: dict[uuid.UUID, list[str]],
) -> RFCRevision | None:
    """
    Attempt to register a new revision for the specified, existing RFC document in the database.
    """
    if await check_rfc_is_quarantined(rfc_id):
        return None

    if not await check_user_created_rfc(user, rfc_id):
        raise HTTPException(status_code=401, detail="unauthorized to revise this RFC")

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            rfc_state = await connection.fetchrow(
                "SELECT review_requested, status FROM rfcs WHERE id = $1 FOR UPDATE",
                rfc_id,
            )
            if rfc_state is None:
                raise HTTPException(status_code=404, detail="RFC not found")
            if rfc_state.get("review_requested") or rfc_state.get("status") in {
                "accepted",
                "rejected",
            }:
                raise HTTPException(
                    status_code=400,
                    detail="RFC is no longer open for revisions",
                )

            query = """
            WITH revision_insert AS (
                INSERT INTO rfc_revisions (
                    id, rfc_id, created_at, created_by, agent_contributors,
                    title, slug, status, content, summary, is_public, message
                )
                VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING *
            ), rfc_update AS (
                UPDATE rfcs
                SET updated_at = $3,
                    title = $6,
                    slug = $7,
                    status = $8,
                    content = $9,
                    summary = $10,
                    is_public = $11,
                    revisions = $13,
                    current_revision = $1,
                    agent_contributions = $14
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
                request.public,
                request.message,
                new_revisions,
                _serialize_agent_contributions(new_contributions),
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
                message=rev.get("message"),
                public=rev.get("is_public") or False,
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
    if await check_rfc_is_quarantined(comment.rfc_id):
        raise HTTPException(status_code=404, detail="RFC not found")

    if await get_rfc_from_db(comment.rfc_id) is None:
        raise HTTPException(
            status_code=400, detail="can't comment on a nonexistent RFC"
        )

    if comment.parent_id is not None:
        if not await check_comment_is_on_rfc(comment.parent_id, comment.rfc_id):
            raise HTTPException(
                status_code=400, detail="can't reply to a comment on another RFC"
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
                    comment.parent_id,
                )
            except asyncpg.ForeignKeyViolationError as e:
                if e.constraint_name == "fk_rfc_comments_parent_id":
                    raise HTTPException(
                        status_code=400, detail="parent comment does not exist"
                    )
                raise


async def get_comment_from_db(
    rfc_id: int,
    comment_id: int,
    quarantine_ok: bool = False,
) -> RFCComment | None:
    """
    Attempt to fetch the comment with the given ID from the database.
    """
    if (
        await check_rfc_is_quarantined(
            rfc_id=rfc_id,
        )
        and not quarantine_ok
    ):
        return None

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow(
                "SELECT * FROM rfc_comments WHERE id = $1", comment_id
            )
            if result is None:
                return None
            if result.get("is_quarantined") and not quarantine_ok:
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
                author_name_first=creator.name_first,
            )


async def get_rfc_comments_from_db(
    rfc_id: int,
    quarantine_ok: bool = False,
) -> list[RFCComment]:
    """
    Attempt to fetch all comments on the RFC with the given ID from the database,
    including author names.
    """
    if await check_rfc_is_quarantined(
        rfc_id=rfc_id,
    ):
        return []

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch(
                "SELECT * FROM rfc_comments WHERE rfc_id = $1", rfc_id
            )
            if result is None:
                return []
            comments: list[RFCComment] = []
            for comment in result:
                if comment.get("is_quarantined") and not quarantine_ok:
                    continue
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
                    author_name_first=creator.name_first,
                )
                comments.append(comment_obj)
            return comments


async def get_comments_quarantined_in_db(
    rfc_id: int,
) -> list[QuarantinedComment]:
    """
    Get all quarantined (soft-deleted) comments on a given RFC in the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            quarantined_comments = await connection.fetch(
                "SELECT * FROM quarantined_comments",
            )
            if quarantined_comments is None:
                return []
            summaries: list[QuarantinedComment] = []
            for comment in quarantined_comments:
                if not await check_comment_is_on_rfc(comment.get("comment_id"), rfc_id):
                    continue
                quarantiner = await get_user_by_id(comment.get("quarantined_by"))
                if quarantiner is None:
                    continue
                comment_from_db = await get_comment_from_db(
                    rfc_id=rfc_id,
                    comment_id=comment.get("comment_id"),
                    quarantine_ok=True,
                )
                if comment_from_db is None:
                    continue
                summary = QuarantinedComment(
                    quarantine_id=comment.get("quarantine_id"),
                    quarantined_by_name_last=quarantiner.name_last,
                    quarantined_by_name_first=quarantiner.name_first,
                    quarantined_at=comment.get("quarantined_at"),
                    reason=comment.get("reason"),
                    comment=comment_from_db,
                )
                summaries.append(summary)
            return summaries


async def delete_comment_from_db(
    rfc_id: int,
    quarantine_id: int,
) -> None:
    """
    Fully delete a quarantined comment from the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query_quarantine = """
            DELETE FROM quarantined_comments
            WHERE quarantine_id = $1
            RETURNING comment_id;
            """
            comment_id = await connection.fetchval(query_quarantine, quarantine_id)
            if comment_id is None:
                raise HTTPException(
                    status_code=404, detail="quarantined comment not found"
                )
            query_comment = """
            DELETE FROM rfc_comments
            WHERE id = $1 AND rfc_id = $2;
            """
            await connection.execute(
                query_comment,
                comment_id,
                rfc_id,
            )


async def unquarantine_comment_in_db(
    rfc_id: int,
    quarantine_id: int,
) -> None:
    """
    Unquarantine and reupload a comment in the database.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query_quarantine = """
            DELETE FROM quarantined_comments
            WHERE quarantine_id = $1
            RETURNING comment_id;
            """
            comment_id = await connection.fetchval(
                query_quarantine,
                quarantine_id,
            )
            if comment_id is None:
                raise HTTPException(
                    status_code=404, detail="quarantined comment not found"
                )
            query_comment = """
            UPDATE rfc_comments
            SET is_quarantined = FALSE
            WHERE id = $1 AND rfc_id = $2;
            """
            await connection.execute(
                query_comment,
                comment_id,
                rfc_id,
            )


async def quarantine_comment_in_db(
    rfc_id: int,
    comment_id: int,
    reason: str,
    user: User,
) -> None:
    """
    Soft-delete (quarantine) an existing comment in the database.
    """
    rfc = await get_rfc_from_db(rfc_id)
    if rfc is None:
        raise HTTPException(status_code=404, detail="RFC not found")

    if await check_comment_is_quarantined(rfc_id, comment_id):
        raise HTTPException(status_code=404, detail="RFC not found")

    if not await check_user_created_comment(user, rfc_id, comment_id):
        if not user.is_admin:
            raise HTTPException(status_code=401, detail="cannot delete this comment")

    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            query_comments = """
            UPDATE rfc_comments
            SET is_quarantined = TRUE
            WHERE id = $1 AND rfc_id = $2;
            """
            await connection.execute(query_comments, comment_id, rfc_id)
            query_quarantined = """
            INSERT INTO quarantined_comments (
                quarantined_by, quarantined_at, reason, comment_id
            )
            VALUES($1, $2, $3, $4);
            """
            await connection.execute(
                query_quarantined,
                user.id,
                datetime.now(timezone.utc),
                reason,
                comment_id,
            )


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
                "SELECT rfc_id FROM rfc_comments WHERE id = $1", comment_id
            )
            if result is None:
                return False
            return result == rfc_id


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
                "SELECT created_by FROM rfcs WHERE id = $1", rfc_id
            )
            if rfc_author != user.id:
                return False
            return True


async def check_user_created_comment(
    user: User,
    rfc_id: int,
    comment_id: int,
) -> bool:
    """
    Check that this user created the specified comment.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            comment_author = await connection.fetchval(
                "SELECT created_by FROM rfc_comments WHERE id = $1 AND rfc_id = $2",
                comment_id,
                rfc_id,
            )
            if comment_author != user.id:
                return False
            return True


async def check_rfc_is_quarantined(
    rfc_id: int,
) -> bool:
    """
    Check if the RFC with the given ID is quarantined.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            is_quarantined = await connection.fetchval(
                "SELECT is_quarantined FROM rfcs WHERE id = $1", rfc_id
            )
            if is_quarantined:
                return True
            return False


async def check_comment_is_quarantined(
    rfc_id: int,
    comment_id: int,
) -> bool:
    """
    Check if the specified comment is quarantined.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            is_quarantined = await connection.fetchval(
                "SELECT is_quarantined FROM rfc_comments WHERE rfc_id = $1 AND id = $2",
                rfc_id,
                comment_id,
            )
            if is_quarantined:
                return True
            return False


async def check_rfc_not_already_requested_review(
    rfc_id: int,
) -> bool:
    """
    Check that this RFC does not already have review requested.
    """
    global _pool
    async with _pool.acquire() as connection:
        async with connection.transaction():
            review_requested = await connection.fetchval(
                "SELECT review_requested FROM rfcs WHERE id = $1",
                rfc_id
            )
            if review_requested:
                return False
            return True
        
