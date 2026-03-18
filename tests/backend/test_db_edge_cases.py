from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException

from mdrfc.backend import db
from mdrfc.backend.comment import RFCCommentInDB
from mdrfc.backend.document import RFCDocumentInDB, RFCRevisionInDB


def _naive(dt):
    return dt.replace(tzinfo=None)


def _register_verified_user(
    run_db,
    user_in_db_factory,
    user_factory,
    *,
    fixed_timestamp,
    username: str,
    email: str,
    is_admin: bool = False,
):
    timestamp = _naive(fixed_timestamp)
    user_in_db = user_in_db_factory(
        username=username,
        email=email,
        is_verified=True,
        created_at=timestamp,
        verified_at=timestamp,
        is_admin=is_admin,
    )
    user_id = run_db(db.register_user_in_db(user_in_db))
    return user_id, user_factory(
        id=user_id,
        username=username,
        email=email,
        created_at=timestamp,
        verified_at=timestamp,
        is_admin=is_admin,
    )


def _register_rfc(run_db, fixed_timestamp, *, created_by: int, slug: str) -> int:
    first_revision_id = uuid4()
    document = RFCDocumentInDB(
        id=-1,
        created_by=created_by,
        created_at=fixed_timestamp,
        updated_at=fixed_timestamp,
        title=f"Testing RFC {slug}",
        slug=slug,
        status="draft",
        content="Content for testing RFC behavior.",
        summary="Summary for testing RFC behavior.",
        revisions=[first_revision_id],
        current_revision=first_revision_id,
        agent_contributions={first_revision_id: ["codex@openai"]},
        public=True,
    )
    return run_db(db.register_rfc_in_db(document))


def test_register_user_in_db_rejects_duplicate_identity(
    run_db,
    user_in_db_factory,
    fixed_timestamp,
) -> None:
    timestamp = _naive(fixed_timestamp)
    first_user = user_in_db_factory(
        username="alice",
        email="alice@example.com",
        is_verified=True,
        created_at=timestamp,
        verified_at=timestamp,
    )
    duplicate_user = user_in_db_factory(
        username="alice",
        email="another@example.com",
        is_verified=True,
        created_at=timestamp,
        verified_at=timestamp,
    )

    run_db(db.register_user_in_db(first_user))

    with pytest.raises(HTTPException) as excinfo:
        run_db(db.register_user_in_db(duplicate_user))

    assert excinfo.value.status_code == 409
    assert excinfo.value.detail == "account could not be created"


def test_verify_user_by_token_in_db_returns_none_for_expired_token(
    run_db,
    user_in_db_factory,
    fixed_timestamp,
) -> None:
    user = user_in_db_factory(
        username="alice",
        email="alice@example.com",
        is_verified=False,
        created_at=_naive(fixed_timestamp),
        verification_token_hash="verification-token-hash",
        verification_token_expires_at=_naive(fixed_timestamp) + timedelta(minutes=5),
    )
    run_db(db.register_user_in_db(user))

    verified = run_db(
        db.verify_user_by_token_in_db(
            verification_token_hash="verification-token-hash",
            verified_at=_naive(fixed_timestamp) + timedelta(minutes=10),
        )
    )

    assert verified is None


def test_register_revision_in_db_rejects_non_author(
    run_db,
    fixed_timestamp,
    user_in_db_factory,
    user_factory,
) -> None:
    owner_id, _ = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
        username="owner",
        email="owner@example.com",
    )
    outsider_id, outsider = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
        username="outsider",
        email="outsider@example.com",
    )
    rfc_id = _register_rfc(
        run_db, fixed_timestamp, created_by=owner_id, slug="owner-rfc"
    )
    revision = RFCRevisionInDB(
        id=uuid4(),
        rfc_id=rfc_id,
        created_at=fixed_timestamp + timedelta(minutes=5),
        created_by=outsider_id,
        agent_contributors=[],
        title="Updated RFC",
        slug="owner-rfc",
        status="open",
        content="Updated content for testing RFC behavior.",
        summary="Updated summary for testing RFC behavior.",
        message="Attempt unauthorized revision",
        public=True,
    )

    with pytest.raises(HTTPException) as excinfo:
        run_db(
            db.register_revision_in_db(
                rfc_id=rfc_id,
                user=outsider,
                request=revision,
                new_revisions=[revision.id],
                new_contributions={revision.id: []},
            )
        )

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "unauthorized to revise this RFC"


def test_quarantine_rfc_in_db_rejects_non_owner_non_admin(
    run_db,
    fixed_timestamp,
    user_in_db_factory,
    user_factory,
) -> None:
    owner_id, _ = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
        username="owner",
        email="owner@example.com",
    )
    _, outsider = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
        username="outsider",
        email="outsider@example.com",
    )
    rfc_id = _register_rfc(
        run_db, fixed_timestamp, created_by=owner_id, slug="owner-rfc"
    )

    with pytest.raises(HTTPException) as excinfo:
        run_db(
            db.quarantine_rfc_in_db(
                rfc_id=rfc_id,
                reason="RFC violates moderation policy.",
                user=outsider,
            )
        )

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "cannot delete this RFC"


def test_register_comment_in_db_rejects_reply_to_comment_on_other_rfc(
    run_db,
    fixed_timestamp,
    user_in_db_factory,
    user_factory,
) -> None:
    owner_id, _ = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
        username="owner",
        email="owner@example.com",
    )
    rfc_one_id = _register_rfc(
        run_db, fixed_timestamp, created_by=owner_id, slug="rfc-one"
    )
    rfc_two_id = _register_rfc(
        run_db, fixed_timestamp, created_by=owner_id, slug="rfc-two"
    )
    parent_comment_id = run_db(
        db.register_comment_in_db(
            RFCCommentInDB(
                id=-1,
                parent_id=None,
                rfc_id=rfc_one_id,
                created_by=owner_id,
                created_at=fixed_timestamp,
                content="This is a valid test comment.",
            )
        )
    )

    with pytest.raises(HTTPException) as excinfo:
        run_db(
            db.register_comment_in_db(
                RFCCommentInDB(
                    id=-1,
                    parent_id=parent_comment_id,
                    rfc_id=rfc_two_id,
                    created_by=owner_id,
                    created_at=fixed_timestamp,
                    content="This is a valid reply comment.",
                )
            )
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "can't reply to a comment on another RFC"


def test_quarantine_comment_in_db_rejects_non_owner_non_admin(
    run_db,
    fixed_timestamp,
    user_in_db_factory,
    user_factory,
) -> None:
    owner_id, _ = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
        username="owner",
        email="owner@example.com",
    )
    _, outsider = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
        username="outsider",
        email="outsider@example.com",
    )
    rfc_id = _register_rfc(
        run_db, fixed_timestamp, created_by=owner_id, slug="owner-rfc"
    )
    comment_id = run_db(
        db.register_comment_in_db(
            RFCCommentInDB(
                id=-1,
                parent_id=None,
                rfc_id=rfc_id,
                created_by=owner_id,
                created_at=fixed_timestamp,
                content="This is a valid test comment.",
            )
        )
    )

    with pytest.raises(HTTPException) as excinfo:
        run_db(
            db.quarantine_comment_in_db(
                rfc_id=rfc_id,
                comment_id=comment_id,
                reason="Comment violates moderation policy.",
                user=outsider,
            )
        )

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "cannot delete this comment"
