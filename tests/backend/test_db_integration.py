from datetime import timedelta
from uuid import uuid4

from mdrfc.backend import db
from mdrfc.backend.comment import RFCCommentInDB
from mdrfc.backend.document import RFCDocumentInDB, RFCRevisionInDB


def _naive(dt):
    return dt.replace(tzinfo=None)


def _register_verified_user(run_db, user_in_db_factory, user_factory, *, fixed_timestamp):
    timestamp = _naive(fixed_timestamp)
    user_in_db = user_in_db_factory(
        is_verified=True,
        created_at=timestamp,
        verified_at=timestamp,
    )
    user_id = run_db(db.register_user_in_db(user_in_db))
    return user_id, user_factory(
        id=user_id,
        created_at=timestamp,
        verified_at=timestamp,
    )


def _register_rfc(
    run_db,
    fixed_timestamp,
    *,
    created_by: int,
    public: bool,
):
    first_revision_id = uuid4()
    document = RFCDocumentInDB(
        id=-1,
        created_by=created_by,
        created_at=fixed_timestamp,
        updated_at=fixed_timestamp,
        title="Testing RFC",
        slug="testing-rfc",
        status="draft",
        content="Content for testing RFC behavior.",
        summary="Summary for testing RFC behavior.",
        revisions=[first_revision_id],
        current_revision=first_revision_id,
        agent_contributions={first_revision_id: ["codex@openai"]},
        public=public,
    )
    rfc_id = run_db(db.register_rfc_in_db(document))
    return rfc_id, first_revision_id


def test_register_user_and_verify_email_round_trip(
    run_db,
    user_in_db_factory,
    fixed_timestamp,
) -> None:
    user = user_in_db_factory(
        is_verified=False,
        verification_token_hash="verification-token-hash",
        created_at=_naive(fixed_timestamp),
        verification_token_expires_at=_naive(fixed_timestamp) + timedelta(hours=1),
    )

    user_id = run_db(db.register_user_in_db(user))
    stored = run_db(db.get_user_from_db("alice"))
    verified = run_db(
        db.verify_user_by_token_in_db(
            verification_token_hash="verification-token-hash",
            verified_at=_naive(fixed_timestamp) + timedelta(minutes=10),
        )
    )

    assert user_id > 0
    assert run_db(db.user_in_db("alice")) is True
    assert stored is not None
    assert stored.id == user_id
    assert stored.is_verified is False
    assert verified is not None
    assert verified.is_verified is True
    assert verified.verification_token_hash is None
    assert verified.verification_token_expires_at is None


def test_register_rfc_round_trip_persists_public_and_initial_revision(
    run_db,
    fixed_timestamp,
    user_in_db_factory,
    user_factory,
) -> None:
    user_id, _ = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
    )
    rfc_id, first_revision_id = _register_rfc(
        run_db,
        fixed_timestamp,
        created_by=user_id,
        public=True,
    )

    stored_rfc = run_db(db.get_rfc_from_db(rfc_id))
    summaries = run_db(db.get_rfcs_from_db())
    revisions = run_db(db.get_revisions_from_db(rfc_id))
    current_revision = run_db(db.get_revision_from_db(rfc_id, str(first_revision_id)))

    assert stored_rfc is not None
    assert stored_rfc.id == rfc_id
    assert stored_rfc.public is True
    assert summaries is not None
    assert summaries[0].public is True
    assert revisions is not None
    assert len(revisions) == 1
    assert revisions[0].public is True
    assert current_revision is not None
    assert current_revision.public is True
    assert current_revision.message == "First revision"


def test_register_revision_updates_current_revision_and_public_flag(
    run_db,
    fixed_timestamp,
    user_in_db_factory,
    user_factory,
) -> None:
    user_id, user = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
    )
    rfc_id, first_revision_id = _register_rfc(
        run_db,
        fixed_timestamp,
        created_by=user_id,
        public=False,
    )
    new_revision_id = uuid4()

    revision = RFCRevisionInDB(
        id=new_revision_id,
        rfc_id=rfc_id,
        created_at=fixed_timestamp + timedelta(minutes=5),
        created_by=user_id,
        agent_contributors=["codex@openai", "gpt@openai"],
        title="Updated RFC",
        slug="updated-rfc",
        status="open",
        content="Updated content for testing RFC behavior.",
        summary="Updated summary for testing RFC behavior.",
        message="Publish updated RFC",
        public=True,
    )

    created_revision = run_db(
        db.register_revision_in_db(
            rfc_id=rfc_id,
            user=user,
            request=revision,
            new_revisions=[first_revision_id, new_revision_id],
            new_contributions={
                first_revision_id: ["codex@openai"],
                new_revision_id: ["codex@openai", "gpt@openai"],
            },
        )
    )
    stored_rfc = run_db(db.get_rfc_from_db(rfc_id))
    stored_revision = run_db(db.get_revision_from_db(rfc_id, str(new_revision_id)))

    assert created_revision is not None
    assert created_revision.public is True
    assert stored_rfc is not None
    assert stored_rfc.current_revision == new_revision_id
    assert stored_rfc.public is True
    assert stored_revision is not None
    assert stored_revision.public is True
    assert stored_revision.agent_contributors == ["codex@openai", "gpt@openai"]


def test_comment_round_trip_and_quarantine_cycle(
    run_db,
    fixed_timestamp,
    user_in_db_factory,
    user_factory,
) -> None:
    user_id, user = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
    )
    rfc_id, _ = _register_rfc(
        run_db,
        fixed_timestamp,
        created_by=user_id,
        public=True,
    )
    comment = RFCCommentInDB(
        id=-1,
        parent_id=None,
        rfc_id=rfc_id,
        created_by=user_id,
        created_at=fixed_timestamp,
        content="This is a valid test comment.",
    )

    comment_id = run_db(db.register_comment_in_db(comment))
    stored_comment = run_db(db.get_comment_from_db(rfc_id, comment_id))
    run_db(
        db.quarantine_comment_in_db(
            rfc_id=rfc_id,
            comment_id=comment_id,
            reason="Comment violates moderation policy.",
            user=user,
        )
    )
    hidden_comment = run_db(db.get_comment_from_db(rfc_id, comment_id))
    quarantined = run_db(db.get_comments_quarantined_in_db(rfc_id))
    run_db(
        db.unquarantine_comment_in_db(
            rfc_id=rfc_id,
            quarantine_id=quarantined[0].quarantine_id,
        )
    )
    restored_comment = run_db(db.get_comment_from_db(rfc_id, comment_id))

    assert stored_comment is not None
    assert stored_comment.content == "This is a valid test comment."
    assert hidden_comment is None
    assert len(quarantined) == 1
    assert quarantined[0].comment.id == comment_id
    assert restored_comment is not None
    assert restored_comment.id == comment_id


def test_rfc_quarantine_and_unquarantine_cycle(
    run_db,
    fixed_timestamp,
    user_in_db_factory,
    user_factory,
) -> None:
    user_id, user = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
    )
    rfc_id, _ = _register_rfc(
        run_db,
        fixed_timestamp,
        created_by=user_id,
        public=True,
    )

    run_db(
        db.quarantine_rfc_in_db(
            rfc_id=rfc_id,
            reason="RFC violates moderation policy.",
            user=user,
        )
    )
    hidden_rfc = run_db(db.get_rfc_from_db(rfc_id))
    quarantined = run_db(db.get_rfcs_quarantined_from_db())
    run_db(db.unquarantine_rfc_in_db(quarantined[0].quarantine_id))
    restored_rfc = run_db(db.get_rfc_from_db(rfc_id))

    assert hidden_rfc is None
    assert len(quarantined) == 1
    assert quarantined[0].rfc_id == rfc_id
    assert restored_rfc is not None
    assert restored_rfc.id == rfc_id


def test_delete_quarantined_rfc_removes_document(
    run_db,
    fixed_timestamp,
    user_in_db_factory,
    user_factory,
) -> None:
    user_id, user = _register_verified_user(
        run_db,
        user_in_db_factory,
        user_factory,
        fixed_timestamp=fixed_timestamp,
    )
    rfc_id, _ = _register_rfc(
        run_db,
        fixed_timestamp,
        created_by=user_id,
        public=True,
    )

    run_db(
        db.quarantine_rfc_in_db(
            rfc_id=rfc_id,
            reason="RFC violates moderation policy.",
            user=user,
        )
    )
    quarantined = run_db(db.get_rfcs_quarantined_from_db())
    run_db(db.delete_rfc_from_db(quarantined[0].quarantine_id))

    assert run_db(db.get_rfc_from_db(rfc_id, quarantine_ok=True)) is None
