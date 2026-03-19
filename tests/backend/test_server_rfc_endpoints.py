from datetime import datetime

import pytest

from mdrfc import server
from mdrfc.backend.comment import build_comment_threads
import mdrfc.responses as res_types


def test_get_rfcs_returns_api_payload_for_anonymous_user(
    client,
    monkeypatch: pytest.MonkeyPatch,
    rfc_summary_factory,
) -> None:
    async def fake_get_rfcs(*, current_user):
        assert current_user is None
        return res_types.GetRfcsResponse(
            rfcs=[rfc_summary_factory(id=2, public=True, slug="public-rfc")],
            metadata={"source": "stub"},
        )

    monkeypatch.setattr(server.api, "get_rfcs", fake_get_rfcs)

    response = client.get("/rfcs")

    assert response.status_code == 200
    assert response.json()["rfcs"][0]["id"] == 2
    assert response.json()["metadata"] == {"source": "stub"}


def test_get_quarantined_rfcs_returns_admin_payload(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
    rfc_document_factory,
) -> None:
    async def fake_get_rfcs_quarantined():
        return res_types.GetQuarantinedRfcsResponse(
            quarantined_rfcs=[],
            metadata={"admin": True},
        )

    auth_overrides(admin_user=user_factory(is_admin=True))
    monkeypatch.setattr(server.api, "get_rfcs_quarantined", fake_get_rfcs_quarantined)

    response = client.get("/rfcs/quarantined")

    assert response.status_code == 200
    assert response.json()["metadata"] == {"admin": True}


def test_post_rfc_requires_authentication(client) -> None:
    response = client.post(
        "/rfcs",
        json={
            "title": "Testing RFC",
            "slug": "testing-rfc",
            "status": "draft",
            "summary": "Summary for testing RFC behavior.",
            "content": "Content for testing RFC behavior.",
            "agent_contributors": ["codex@openai"],
            "public": True,
        },
    )

    assert response.status_code == 401


def test_post_rfc_passes_validated_request_to_api(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
) -> None:
    captured: dict[str, object] = {}

    async def fake_post_rfc(*, user, request):
        captured["user"] = user
        captured["request"] = request
        return res_types.PostRfcResponse(
            rfc_id=17,
            created_at=datetime(2026, 3, 9, 12, 0, 0),
            metadata={"created": True},
        )

    auth_overrides(current_user=user_factory(id=7))
    monkeypatch.setattr(server.api, "post_rfc", fake_post_rfc)

    response = client.post(
        "/rfcs",
        json={
            "title": "Testing RFC",
            "slug": "testing-rfc",
            "status": "draft",
            "summary": "Summary for testing RFC behavior.",
            "content": "Content for testing RFC behavior.",
            "agent_contributors": ["codex@openai"],
            "public": True,
        },
    )

    request = captured["request"]
    assert response.status_code == 200
    assert captured["user"].id == 7
    assert request.agent_contributors == ["codex@openai"]
    assert request.public is True
    assert response.json()["rfc_id"] == 17


def test_post_rfc_rejects_invalid_payload(client, auth_overrides, user_factory) -> None:
    auth_overrides(current_user=user_factory())

    response = client.post(
        "/rfcs",
        json={
            "title": "short",
            "slug": "bad",
            "status": "draft",
            "summary": "Summary for testing RFC behavior.",
            "content": "Content for testing RFC behavior.",
            "agent_contributors": ["codex@openai"],
            "public": True,
        },
    )

    assert response.status_code == 422


def test_get_rfc_returns_api_payload(
    client,
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
) -> None:
    async def fake_get_rfc(*, rfc_id, current_user):
        assert rfc_id == 11
        assert current_user is None
        return res_types.GetRfcResponse(
            rfc=rfc_document_factory(id=11, public=True),
            metadata={"loaded": True},
        )

    monkeypatch.setattr(server.api, "get_rfc", fake_get_rfc)

    response = client.get("/rfcs/11")

    assert response.status_code == 200
    assert response.json()["rfc"]["id"] == 11
    assert response.json()["metadata"] == {"loaded": True}


def test_legacy_get_rfc_sets_deprecation_headers(
    client,
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
) -> None:
    async def fake_get_rfc(*, rfc_id, current_user):
        assert rfc_id == 11
        assert current_user is None
        return res_types.GetRfcResponse(
            rfc=rfc_document_factory(id=11, public=True),
            metadata={"loaded": True},
        )

    monkeypatch.setattr(server.api, "get_rfc", fake_get_rfc)

    response = client.get("/rfc/11")

    assert response.status_code == 200
    assert response.headers["deprecation"] == "true"
    assert response.headers["link"] == '</rfcs/11>; rel="alternate"'


def test_canonical_get_rfc_omits_deprecation_headers(
    client,
    monkeypatch: pytest.MonkeyPatch,
    rfc_document_factory,
) -> None:
    async def fake_get_rfc(*, rfc_id, current_user):
        assert rfc_id == 11
        assert current_user is None
        return res_types.GetRfcResponse(
            rfc=rfc_document_factory(id=11, public=True),
            metadata={"loaded": True},
        )

    monkeypatch.setattr(server.api, "get_rfc", fake_get_rfc)

    response = client.get("/rfcs/11")

    assert response.status_code == 200
    assert "deprecation" not in response.headers
    assert "link" not in response.headers


def test_post_rfc_revision_passes_nested_update_to_api(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
    revision_factory,
) -> None:
    captured: dict[str, object] = {}

    async def fake_post_rfc_revision(*, rfc_id, user, request):
        captured["rfc_id"] = rfc_id
        captured["user"] = user
        captured["request"] = request
        return res_types.PostRfcRevisionResponse(
            revision=revision_factory(
                rfc_id=rfc_id,
                title="Updated RFC",
                message=request.message,
            ),
            metadata={},
        )

    auth_overrides(current_user=user_factory(id=5))
    monkeypatch.setattr(server.api, "post_rfc_revision", fake_post_rfc_revision)

    response = client.post(
        "/rfcs/9/revs",
        json={
            "update": {
                "title": "Updated RFC",
                "public": True,
            },
            "message": "Publish the revision",
        },
    )

    request = captured["request"]
    assert response.status_code == 200
    assert captured["rfc_id"] == 9
    assert captured["user"].id == 5
    assert request.update.title == "Updated RFC"
    assert request.update.public is True
    assert request.message == "Publish the revision"


def test_post_rfc_comment_passes_validated_request_to_api(
    client,
    monkeypatch: pytest.MonkeyPatch,
    auth_overrides,
    user_factory,
) -> None:
    captured: dict[str, object] = {}

    async def fake_post_rfc_comment(*, rfc_id, user, request):
        captured["rfc_id"] = rfc_id
        captured["user"] = user
        captured["request"] = request
        return res_types.PostRfcCommentResponse(
            comment_id=23,
            created_at=datetime(2026, 3, 9, 12, 0, 0),
            metadata={},
        )

    auth_overrides(current_user=user_factory(id=3))
    monkeypatch.setattr(server.api, "post_rfc_comment", fake_post_rfc_comment)

    response = client.post(
        "/rfcs/9/comments",
        json={
            "parent_comment_id": None,
            "content": "This is a valid test comment.",
        },
    )

    assert response.status_code == 200
    assert captured["rfc_id"] == 9
    assert captured["user"].id == 3
    assert captured["request"].content == "This is a valid test comment."
    assert response.json()["comment_id"] == 23


def test_get_rfc_comment_returns_api_payload(
    client,
    monkeypatch: pytest.MonkeyPatch,
    comment_factory,
) -> None:
    comment_thread = build_comment_threads([comment_factory(id=4, rfc_id=11)])[0]

    async def fake_get_rfc_comment(*, rfc_id, comment_id, current_user):
        assert (rfc_id, comment_id, current_user) == (11, 4, None)
        return res_types.GetRfcCommentResponse(
            comment=comment_thread,
            metadata={"loaded": True},
        )

    monkeypatch.setattr(server.api, "get_rfc_comment", fake_get_rfc_comment)

    response = client.get("/rfcs/11/comments/4")

    assert response.status_code == 200
    assert response.json()["comment"]["id"] == 4
    assert response.json()["metadata"] == {"loaded": True}


def test_legacy_get_comment_sets_deprecation_headers(
    client,
    monkeypatch: pytest.MonkeyPatch,
    comment_factory,
) -> None:
    comment_thread = build_comment_threads([comment_factory(id=4, rfc_id=11)])[0]

    async def fake_get_rfc_comment(*, rfc_id, comment_id, current_user):
        assert (rfc_id, comment_id, current_user) == (11, 4, None)
        return res_types.GetRfcCommentResponse(
            comment=comment_thread,
            metadata={"loaded": True},
        )

    monkeypatch.setattr(server.api, "get_rfc_comment", fake_get_rfc_comment)

    response = client.get("/rfc/11/comment/4")

    assert response.status_code == 200
    assert response.headers["deprecation"] == "true"
    assert response.headers["link"] == '</rfcs/11/comments/4>; rel="alternate"'


@pytest.mark.parametrize(
    ("path", "method"),
    [
        ("/rfc", "post"),
        ("/rfc/{rfc_id}/rev/current", "get"),
        ("/rfc/{rfc_id}", "get"),
        ("/rfc/{rfc_id}", "delete"),
        ("/rfc/{rfc_id}/revs", "get"),
        ("/rfc/{rfc_id}/rev/{rev_id}", "get"),
        ("/rfc/{rfc_id}/rev", "post"),
        ("/rfc/{rfc_id}/comment", "post"),
        ("/rfc/{rfc_id}/comments", "get"),
        ("/rfc/{rfc_id}/comments/quarantined", "get"),
        ("/rfc/{rfc_id}/comments/quarantined/{quarantine_id}", "delete"),
        ("/rfc/{rfc_id}/comments/quarantined/{quarantine_id}", "post"),
        ("/rfc/{rfc_id}/comment/{comment_id}", "get"),
        ("/rfc/{rfc_id}/comment/{comment_id}", "delete"),
    ],
)
def test_legacy_routes_are_marked_deprecated_in_openapi(path: str, method: str) -> None:
    server.app.openapi_schema = None
    schema = server.app.openapi()

    assert schema["paths"][path][method]["deprecated"] is True


@pytest.mark.parametrize(
    ("path", "method"),
    [
        ("/rfcs", "post"),
        ("/rfcs/{rfc_id}", "get"),
        ("/rfcs/{rfc_id}", "delete"),
        ("/rfcs/{rfc_id}/revs", "get"),
        ("/rfcs/{rfc_id}/revs/{rev_id}", "get"),
        ("/rfcs/{rfc_id}/revs", "post"),
        ("/rfcs/{rfc_id}/comments", "post"),
        ("/rfcs/{rfc_id}/comments", "get"),
        ("/rfcs/{rfc_id}/comments/quarantined", "get"),
        ("/rfcs/{rfc_id}/comments/quarantined/{quarantine_id}", "delete"),
        ("/rfcs/{rfc_id}/comments/quarantined/{quarantine_id}", "post"),
        ("/rfcs/{rfc_id}/comments/{comment_id}", "get"),
        ("/rfcs/{rfc_id}/comments/{comment_id}", "delete"),
    ],
)
def test_canonical_routes_are_not_marked_deprecated_in_openapi(
    path: str, method: str
) -> None:
    server.app.openapi_schema = None
    schema = server.app.openapi()

    assert schema["paths"][path][method].get("deprecated") is not True
