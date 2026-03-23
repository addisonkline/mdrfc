import asyncio
from uuid import uuid4

import pytest
from fastapi import HTTPException

import mdrfc.api as api
from mdrfc.requests import PostRfcRequest, PostRfcRevisionRequest
from mdrfc.backend.document import RFCRevisionRequest


def test_get_rfcs_filters_private_documents_for_anonymous_users(
    monkeypatch: pytest.MonkeyPatch,
    rfc_summary_factory,
) -> None:
    async def fake_get_rfcs_from_db():
        return [
            rfc_summary_factory(id=1, public=False),
            rfc_summary_factory(id=2, public=True, slug="public-rfc"),
        ]

    monkeypatch.setattr(api, "get_rfcs_from_db", fake_get_rfcs_from_db)

    response = asyncio.run(api.get_rfcs(current_user=None))

    assert [rfc.id for rfc in response.rfcs] == [2]


def test_get_rfcs_returns_private_documents_for_authenticated_users(
    monkeypatch: pytest.MonkeyPatch,
    rfc_summary_factory,
    user_factory,
) -> None:
    async def fake_get_rfcs_from_db():
        return [
            rfc_summary_factory(id=1, public=False),
            rfc_summary_factory(id=2, public=True, slug="public-rfc"),
        ]

    monkeypatch.setattr(api, "get_rfcs_from_db", fake_get_rfcs_from_db)

    response = asyncio.run(api.get_rfcs(current_user=user_factory()))

    assert [rfc.id for rfc in response.rfcs] == [1, 2]


def test_get_rfc_blocks_anonymous_access_to_private_document(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
) -> None:
    async def fake_get_rfc_from_db(_: int):
        return rfc_document_factory(public=False)

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(api.get_rfc(rfc_id=1, current_user=None))

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "unable to get this RFC"


def test_post_rfc_creates_initial_revision_and_agent_contributions(
    monkeypatch: pytest.MonkeyPatch,
    user_factory,
) -> None:
    captured: dict[str, object] = {}

    async def fake_register_rfc_in_db(document):
        captured["document"] = document
        return 42

    monkeypatch.setattr(api, "register_rfc_in_db", fake_register_rfc_in_db)

    response = asyncio.run(
        api.post_rfc(
            user=user_factory(id=7),
            request=PostRfcRequest(
                title="Testing RFC",
                slug="testing-rfc",
                status="draft",
                summary="Summary for testing RFC behavior.",
                content="Content for testing RFC behavior.",
                agent_contributors=["codex@openai"],
                public=True,
            ),
        )
    )

    document = captured["document"]
    assert response.rfc_id == 42
    assert document.created_by == 7
    assert document.public is True
    assert len(document.revisions) == 1
    assert document.current_revision == document.revisions[0]
    assert document.agent_contributions[document.current_revision] == ["codex@openai"]


def test_post_rfc_revision_merges_partial_updates(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
    revision_factory,
    user_factory,
) -> None:
    captured: dict[str, object] = {}
    existing_revision_id = uuid4()
    existing_rfc = rfc_document_factory(
        revisions=[existing_revision_id],
        current_revision=existing_revision_id,
        agent_contributions={existing_revision_id: ["codex@openai"]},
        public=True,
    )

    async def fake_get_rfc_from_db(_: int):
        return existing_rfc

    async def fake_register_revision_in_db(
        *, rfc_id, user, request, new_revisions, new_contributions
    ):
        captured["rfc_id"] = rfc_id
        captured["user"] = user
        captured["request"] = request
        captured["new_revisions"] = new_revisions
        captured["new_contributions"] = new_contributions
        return revision_factory(
            id=request.id,
            rfc_id=rfc_id,
            title=request.title,
            slug=request.slug,
            status=request.status,
            content=request.content,
            summary=request.summary,
            message=request.message,
            public=request.public,
            agent_contributors=request.agent_contributors,
        )

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)
    monkeypatch.setattr(api, "register_revision_in_db", fake_register_revision_in_db)

    response = asyncio.run(
        api.post_rfc_revision(
            rfc_id=existing_rfc.id,
            user=user_factory(id=9),
            request=PostRfcRevisionRequest(
                update=RFCRevisionRequest(title="Updated RFC title"),
                message="Update the RFC title",
            ),
        )
    )

    request = captured["request"]
    new_revisions = captured["new_revisions"]
    new_contributions = captured["new_contributions"]

    assert captured["rfc_id"] == existing_rfc.id
    assert request.title == "Updated RFC title"
    assert request.slug == existing_rfc.slug
    assert request.content == existing_rfc.content
    assert request.summary == existing_rfc.summary
    assert request.public is True
    assert len(new_revisions) == 2
    assert new_revisions[0] == existing_revision_id
    assert new_contributions[existing_revision_id] == ["codex@openai"]
    assert new_contributions[new_revisions[-1]] == []
    assert response.revision.title == "Updated RFC title"


def test_post_rfc_revision_rejects_when_review_requested(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
    user_factory,
) -> None:
    existing_rfc = rfc_document_factory(review_requested=True)
    register_called = False

    async def fake_get_rfc_from_db(_: int):
        return existing_rfc

    async def fake_register_revision_in_db(**kwargs):
        nonlocal register_called
        register_called = True
        raise AssertionError("register_revision_in_db should not be called")

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)
    monkeypatch.setattr(api, "register_revision_in_db", fake_register_revision_in_db)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            api.post_rfc_revision(
                rfc_id=existing_rfc.id,
                user=user_factory(id=9),
                request=PostRfcRevisionRequest(
                    update=RFCRevisionRequest(title="Updated RFC title"),
                    message="Update the RFC title",
                ),
            )
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "RFC is no longer open for revisions"
    assert register_called is False


@pytest.mark.parametrize("status", ["accepted", "rejected"])
def test_post_rfc_revision_rejects_for_terminal_status(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
    user_factory,
    status: str,
) -> None:
    existing_rfc = rfc_document_factory(
        status=status,
        reviewed=True,
        review_reason="Final admin decision recorded.",
    )
    register_called = False

    async def fake_get_rfc_from_db(_: int):
        return existing_rfc

    async def fake_register_revision_in_db(**kwargs):
        nonlocal register_called
        register_called = True
        raise AssertionError("register_revision_in_db should not be called")

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)
    monkeypatch.setattr(api, "register_revision_in_db", fake_register_revision_in_db)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            api.post_rfc_revision(
                rfc_id=existing_rfc.id,
                user=user_factory(id=9),
                request=PostRfcRevisionRequest(
                    update=RFCRevisionRequest(title="Updated RFC title"),
                    message="Update the RFC title",
                ),
            )
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "RFC is no longer open for revisions"
    assert register_called is False


def test_post_rfc_revision_can_explicitly_make_rfc_private(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
    revision_factory,
    user_factory,
) -> None:
    captured: dict[str, object] = {}
    existing_rfc = rfc_document_factory(public=True)

    async def fake_get_rfc_from_db(_: int):
        return existing_rfc

    async def fake_register_revision_in_db(
        *, rfc_id, user, request, new_revisions, new_contributions
    ):
        captured["request"] = request
        return revision_factory(
            id=request.id,
            rfc_id=rfc_id,
            title=request.title,
            slug=request.slug,
            status=request.status,
            content=request.content,
            summary=request.summary,
            message=request.message,
            public=request.public,
            agent_contributors=request.agent_contributors,
        )

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)
    monkeypatch.setattr(api, "register_revision_in_db", fake_register_revision_in_db)

    response = asyncio.run(
        api.post_rfc_revision(
            rfc_id=existing_rfc.id,
            user=user_factory(id=9),
            request=PostRfcRevisionRequest(
                update=RFCRevisionRequest(public=False),
                message="Make the RFC private",
            ),
        )
    )

    request = captured["request"]
    assert request.public is False
    assert response.revision.public is False
