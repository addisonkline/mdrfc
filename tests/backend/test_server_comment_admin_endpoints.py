from datetime import datetime

import pytest

from mdrfc import server
from mdrfc.backend.comment import build_comment_threads
import mdrfc.responses as res_types


def test_get_quarantined_rfcs_requires_authentication(client) -> None:
    response = client.get("/rfcs/quarantined")

    assert response.status_code == 401


def test_delete_quarantined_rfc_calls_api_for_admin(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
) -> None:
    async def fake_delete_rfc_quarantined(*, quarantine_id: int):
        assert quarantine_id == 7
        return res_types.DeleteQuarantinedRfcResponse(
            message="success",
            deleted_at=datetime(2026, 3, 9, 12, 0, 0),
            metadata={"deleted": True},
        )

    auth_overrides(admin_user=user_factory(is_admin=True))
    monkeypatch.setattr(
        server.api, "delete_rfc_quarantined", fake_delete_rfc_quarantined
    )

    response = client.delete("/rfcs/quarantined/7")

    assert response.status_code == 200
    assert response.json()["metadata"] == {"deleted": True}


def test_unquarantine_rfc_calls_api_for_admin(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
) -> None:
    async def fake_post_rfc_quarantined(*, quarantine_id: int):
        assert quarantine_id == 7
        return res_types.PostQuarantinedRfcResponse(
            message="success",
            unquarantined_at=datetime(2026, 3, 9, 12, 0, 0),
            metadata={"restored": True},
        )

    auth_overrides(admin_user=user_factory(is_admin=True))
    monkeypatch.setattr(server.api, "post_rfc_quarantined", fake_post_rfc_quarantined)

    response = client.post("/rfcs/quarantined/7")

    assert response.status_code == 200
    assert response.json()["metadata"] == {"restored": True}


def test_delete_rfc_route_passes_reason_query_to_api(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
) -> None:
    captured: dict[str, object] = {}

    async def fake_delete_rfc(*, rfc_id: int, reason: str, user):
        captured["rfc_id"] = rfc_id
        captured["reason"] = reason
        captured["user"] = user
        return res_types.DeleteRfcResponse(
            message="success",
            quarantined_at=datetime(2026, 3, 9, 12, 0, 0),
            metadata={"quarantined": True},
        )

    auth_overrides(current_user=user_factory(id=5))
    monkeypatch.setattr(server.api, "delete_rfc", fake_delete_rfc)

    response = client.delete(
        "/rfcs/11",
        params={"reason": "RFC violates moderation policy."},
    )

    assert response.status_code == 200
    assert captured["rfc_id"] == 11
    assert captured["reason"] == "RFC violates moderation policy."
    assert captured["user"].id == 5
    assert response.json()["metadata"] == {"quarantined": True}


def test_get_quarantined_comments_requires_authentication(client) -> None:
    response = client.get("/rfcs/11/comments/quarantined")

    assert response.status_code == 401


def test_get_quarantined_comments_calls_api_for_admin(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
) -> None:
    async def fake_get_rfc_comments_quarantined(*, rfc_id: int):
        assert rfc_id == 11
        return res_types.GetQuarantinedCommentsResponse(
            quarantined_comments=[],
            metadata={"admin": True},
        )

    auth_overrides(admin_user=user_factory(is_admin=True))
    monkeypatch.setattr(
        server.api, "get_rfc_comments_quarantined", fake_get_rfc_comments_quarantined
    )

    response = client.get("/rfcs/11/comments/quarantined")

    assert response.status_code == 200
    assert response.json()["metadata"] == {"admin": True}


def test_delete_quarantined_comment_calls_api_for_admin(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
) -> None:
    async def fake_delete_rfc_comment_quarantined(*, rfc_id: int, quarantine_id: int):
        assert (rfc_id, quarantine_id) == (11, 4)
        return res_types.DeleteQuarantinedCommentResponse(
            message="success",
            deleted_at=datetime(2026, 3, 9, 12, 0, 0),
            metadata={"deleted": True},
        )

    auth_overrides(admin_user=user_factory(is_admin=True))
    monkeypatch.setattr(
        server.api,
        "delete_rfc_comment_quarantined",
        fake_delete_rfc_comment_quarantined,
    )

    response = client.delete("/rfcs/11/comments/quarantined/4")

    assert response.status_code == 200
    assert response.json()["metadata"] == {"deleted": True}


def test_unquarantine_comment_calls_api_for_admin(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
) -> None:
    async def fake_post_rfc_comment_quarantined(*, rfc_id: int, quarantine_id: int):
        assert (rfc_id, quarantine_id) == (11, 4)
        return res_types.PostQuarantinedCommentResponse(
            message="success",
            unquarantined_at=datetime(2026, 3, 9, 12, 0, 0),
            metadata={"restored": True},
        )

    auth_overrides(admin_user=user_factory(is_admin=True))
    monkeypatch.setattr(
        server.api, "post_rfc_comment_quarantined", fake_post_rfc_comment_quarantined
    )

    response = client.post("/rfcs/11/comments/quarantined/4")

    assert response.status_code == 200
    assert response.json()["metadata"] == {"restored": True}


def test_get_rfc_comments_returns_api_payload(
    client,
    monkeypatch: pytest.MonkeyPatch,
    comment_factory,
) -> None:
    comment_thread = build_comment_threads([comment_factory(id=4, rfc_id=11)])[0]

    async def fake_get_rfc_comments(*, rfc_id: int, current_user):
        assert (rfc_id, current_user) == (11, None)
        return res_types.GetRfcCommentsResponse(
            comment_threads=[comment_thread],
            metadata={"loaded": True},
        )

    monkeypatch.setattr(server.api, "get_rfc_comments", fake_get_rfc_comments)

    response = client.get("/rfcs/11/comments")

    assert response.status_code == 200
    assert response.json()["comment_threads"][0]["id"] == 4
    assert response.json()["metadata"] == {"loaded": True}


def test_delete_comment_route_passes_reason_query_to_api(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
) -> None:
    captured: dict[str, object] = {}

    async def fake_delete_rfc_comment(
        *, rfc_id: int, comment_id: int, reason: str, user
    ):
        captured["rfc_id"] = rfc_id
        captured["comment_id"] = comment_id
        captured["reason"] = reason
        captured["user"] = user
        return res_types.DeleteRfcCommentResponse(
            message="success",
            quarantined_at=datetime(2026, 3, 9, 12, 0, 0),
            metadata={"quarantined": True},
        )

    auth_overrides(current_user=user_factory(id=6))
    monkeypatch.setattr(server.api, "delete_rfc_comment", fake_delete_rfc_comment)

    response = client.delete(
        "/rfcs/11/comments/4",
        params={"reason": "Comment violates moderation policy."},
    )

    assert response.status_code == 200
    assert captured["rfc_id"] == 11
    assert captured["comment_id"] == 4
    assert captured["reason"] == "Comment violates moderation policy."
    assert captured["user"].id == 6
    assert response.json()["metadata"] == {"quarantined": True}
