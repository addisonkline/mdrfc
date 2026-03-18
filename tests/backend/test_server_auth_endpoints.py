from datetime import datetime

import pytest

from mdrfc import server
from mdrfc.backend import auth


def test_login_returns_bearer_token(
    client,
    monkeypatch: pytest.MonkeyPatch,
    user_factory,
) -> None:
    async def fake_authenticate_user(username: str, password: str):
        assert username == "Alice"
        assert password == "StrongPassword1"
        return user_factory(username="alice")

    monkeypatch.setattr(server, "authenticate_user", fake_authenticate_user)
    monkeypatch.setattr(
        server, "create_access_token", lambda data, expires_delta: "jwt-token"
    )

    response = client.post(
        "/login",
        data={
            "username": "Alice",
            "password": "StrongPassword1",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "jwt-token",
        "token_type": "bearer",
    }


def test_login_returns_401_for_invalid_credentials(
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_authenticate_user(username: str, password: str):
        return False

    monkeypatch.setattr(server, "authenticate_user", fake_authenticate_user)

    response = client.post(
        "/login",
        data={
            "username": "Alice",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "incorrect username or password"


def test_signup_returns_debug_verification_token_and_normalized_identity(
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    async def fake_create_new_user(**kwargs):
        captured.update(kwargs)
        return auth.SignupResult(
            created_at=datetime(2026, 3, 9, 12, 0, 0),
            verification_expires_at=datetime(2026, 3, 9, 13, 0, 0),
            verification_token="raw-token",
        )

    monkeypatch.setattr(server, "create_new_user", fake_create_new_user)
    monkeypatch.setattr(server, "DEBUG_RETURN_VERIFICATION_TOKEN", True)

    response = client.post(
        "/signup",
        json={
            "username": "Alice.Admin",
            "email": "Alice@Example.com",
            "name_first": "Alice",
            "name_last": "Smith",
            "password": "StrongPassword1",
        },
    )

    assert response.status_code == 200
    assert captured["username"] == "alice.admin"
    assert captured["email"] == "alice@example.com"
    assert response.json()["username"] == "alice.admin"
    assert response.json()["email"] == "alice@example.com"
    assert response.json()["metadata"]["verification_token"] == "raw-token"


def test_signup_returns_429_when_rate_limited(
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLimiter:
        async def check_and_record(self, *args, **kwargs):
            return 9

    monkeypatch.setattr(server, "signup_rate_limiter", FakeLimiter())

    response = client.post(
        "/signup",
        json={
            "username": "Alice",
            "email": "alice@example.com",
            "name_first": "Alice",
            "name_last": "Smith",
            "password": "StrongPassword1",
        },
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "too many signup attempts"
    assert response.headers["Retry-After"] == "9"


def test_verify_email_rejects_short_token(client) -> None:
    response = client.post(
        "/verify-email",
        json={"token": "short"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "verification token is invalid"


def test_verify_email_returns_payload(
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_verify_user_email(token: str):
        assert token == "a" * 32
        return auth.EmailVerificationResult(
            username="alice",
            email="alice@example.com",
            verified_at=datetime(2026, 3, 9, 12, 0, 0),
        )

    monkeypatch.setattr(server, "verify_user_email", fake_verify_user_email)

    response = client.post(
        "/verify-email",
        json={"token": "a" * 32},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "alice"
    assert response.json()["email"] == "alice@example.com"


def test_get_users_me_requires_authentication(client) -> None:
    response = client.get("/users/me")

    assert response.status_code == 401


def test_get_users_me_returns_current_user(
    client,
    auth_overrides,
    user_factory,
) -> None:
    auth_overrides(current_user=user_factory())

    response = client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["username"] == "alice"
