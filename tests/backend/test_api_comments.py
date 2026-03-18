import asyncio

import pytest
from fastapi import HTTPException

import mdrfc.api as api
from mdrfc.requests import PostRfcCommentRequest


def test_get_rfc_revisions_blocks_anonymous_access_to_private_rfc(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
) -> None:
    async def fake_get_rfc_from_db(_: int):
        return rfc_document_factory(public=False)

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(api.get_rfc_revisions(rfc_id=1, current_user=None))

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "unable to access this RFC"


def test_get_rfc_revision_blocks_anonymous_access_to_private_revision(
    monkeypatch: pytest.MonkeyPatch,
    revision_factory,
) -> None:
    async def fake_get_revision_from_db(*, rfc_id: int, revision_id: str):
        return revision_factory(rfc_id=rfc_id, public=False)

    monkeypatch.setattr(api, "get_revision_from_db", fake_get_revision_from_db)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            api.get_rfc_revision(rfc_id=1, revision_id="abc", current_user=None)
        )

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "unable to get this revision"


def test_get_rfc_comments_blocks_anonymous_access_to_private_rfc(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
) -> None:
    async def fake_get_rfc_from_db(_: int):
        return rfc_document_factory(public=False)

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(api.get_rfc_comments(rfc_id=1, current_user=None))

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "unable to access this RFC"


def test_get_rfc_comments_builds_threads_from_comment_rows(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
    comment_factory,
) -> None:
    comments = [
        comment_factory(id=2, rfc_id=1, parent_id=1),
        comment_factory(id=1, rfc_id=1, parent_id=None),
    ]

    async def fake_get_rfc_from_db(_: int):
        return rfc_document_factory(public=True)

    async def fake_get_rfc_comments_from_db(_: int):
        return comments

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)
    monkeypatch.setattr(api, "get_rfc_comments_from_db", fake_get_rfc_comments_from_db)

    response = asyncio.run(api.get_rfc_comments(rfc_id=1, current_user=None))

    assert len(response.comment_threads) == 1
    assert response.comment_threads[0].id == 1
    assert response.comment_threads[0].replies[0].id == 2


def test_get_rfc_comment_rejects_comment_on_other_rfc(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
) -> None:
    async def fake_get_rfc_from_db(_: int):
        return rfc_document_factory(public=True)

    async def fake_check_comment_is_on_rfc(comment_id: int, rfc_id: int) -> bool:
        return False

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)
    monkeypatch.setattr(api, "check_comment_is_on_rfc", fake_check_comment_is_on_rfc)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(api.get_rfc_comment(rfc_id=1, comment_id=9, current_user=None))

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "comment_id does not match rfc_id"


def test_get_rfc_comment_returns_404_when_comment_thread_missing(
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
    comment_factory,
) -> None:
    async def fake_get_rfc_from_db(_: int):
        return rfc_document_factory(public=True)

    async def fake_check_comment_is_on_rfc(comment_id: int, rfc_id: int) -> bool:
        return True

    async def fake_get_rfc_comments_from_db(_: int):
        return [comment_factory(id=1, rfc_id=1)]

    monkeypatch.setattr(api, "get_rfc_from_db", fake_get_rfc_from_db)
    monkeypatch.setattr(api, "check_comment_is_on_rfc", fake_check_comment_is_on_rfc)
    monkeypatch.setattr(api, "get_rfc_comments_from_db", fake_get_rfc_comments_from_db)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(api.get_rfc_comment(rfc_id=1, comment_id=9, current_user=None))

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "comment with given ID not found"


def test_post_rfc_comment_registers_comment_and_returns_metadata(
    monkeypatch: pytest.MonkeyPatch,
    user_factory,
) -> None:
    captured: dict[str, object] = {}

    async def fake_register_comment_in_db(comment):
        captured["comment"] = comment
        return 55

    monkeypatch.setattr(api, "register_comment_in_db", fake_register_comment_in_db)

    response = asyncio.run(
        api.post_rfc_comment(
            rfc_id=7,
            user=user_factory(id=3),
            request=PostRfcCommentRequest(
                parent_comment_id=None,
                content="This is a valid test comment.",
            ),
        )
    )

    comment = captured["comment"]
    assert comment.rfc_id == 7
    assert comment.created_by == 3
    assert response.comment_id == 55
