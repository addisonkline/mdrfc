import asyncio
from datetime import datetime
import os

import pytest
from fastapi import BackgroundTasks, HTTPException, Request


os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("AUTH_DEBUG_RETURN_VERIFICATION_TOKEN", "true")
os.environ.setdefault("APP_BASE_URL", "https://mdrfc.example.com")
os.environ.setdefault("EMAIL_FROM", "noreply@mdrfc.example.com")
os.environ.setdefault("SMTP_HOST", "smtp.example.com")
os.environ.setdefault("SMTP_PORT", "587")
os.environ.setdefault("SMTP_USERNAME", "smtp-user")
os.environ.setdefault("SMTP_PASSWORD", "smtp-password")
os.environ.setdefault("SMTP_STARTTLS", "true")

from mdrfc.backend import auth
from mdrfc.backend import email as email_backend
from mdrfc.backend.rate_limit import SlidingWindowRateLimiter
from mdrfc.backend.users import UserInDB
from mdrfc.requests import PostSignupRequest
from mdrfc import server


def test_post_signup_request_normalizes_identity_fields() -> None:
    payload = PostSignupRequest(
        username="  Alice.Admin  ",
        email="  Alice@example.COM ",
        name_first=" Alice ",
        name_last=" Smith ",
        password="StrongPassword1",
    )

    assert payload.username == "alice.admin"
    assert payload.email == "alice@example.com"
    assert payload.name_first == "Alice"
    assert payload.name_last == "Smith"
    assert payload.password.get_secret_value() == "StrongPassword1"


def test_post_signup_request_rejects_short_password() -> None:
    with pytest.raises(HTTPException) as excinfo:
        PostSignupRequest(
            username="alice",
            email="alice@example.com",
            name_first="Alice",
            name_last="Smith",
            password="short",
        )

    assert excinfo.value.status_code == 422
    assert "password must be at least" in str(excinfo.value.detail)


def test_create_new_user_persists_unverified_account(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, UserInDB] = {}

    async def fake_register_user_in_db(user: UserInDB) -> int:
        captured["user"] = user
        return 1

    monkeypatch.setattr(auth, "register_user_in_db", fake_register_user_in_db)

    result = asyncio.run(
        auth.create_new_user(
            username="Alice",
            email="Alice@example.com",
            name_first="Alice",
            name_last="Smith",
            password="StrongPassword1",
        )
    )

    saved_user = captured["user"]
    assert saved_user.username == "alice"
    assert saved_user.email == "alice@example.com"
    assert saved_user.is_verified is False
    assert saved_user.verified_at is None
    assert saved_user.verification_token_hash is not None
    assert saved_user.verification_token_expires_at is not None
    assert saved_user.verification_token_expires_at > saved_user.created_at
    assert result.verification_token is not None


def test_authenticate_user_blocks_unverified_accounts(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_get_user_from_db(_: str) -> UserInDB:
        return UserInDB(
            id=1,
            username="alice",
            email="alice@example.com",
            name_first="Alice",
            name_last="Smith",
            is_verified=False,
            verified_at=None,
            password_argon2=auth.get_password_hash("StrongPassword1"),
            verification_token_hash="token-hash",
            verification_token_expires_at=None,
            created_at=auth._utcnow(),
        )

    monkeypatch.setattr(auth, "get_user_from_db", fake_get_user_from_db)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(auth.authenticate_user("Alice", "StrongPassword1"))

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "email address not verified"


def test_verify_user_email_rejects_invalid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_verify_user_by_token_in_db(*, verification_token_hash: str, verified_at):
        return None

    monkeypatch.setattr(auth, "verify_user_by_token_in_db", fake_verify_user_by_token_in_db)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(auth.verify_user_email("invalid-token"))

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "verification token is invalid or expired"


def test_signup_rate_limiter_enforces_window() -> None:
    limiter = SlidingWindowRateLimiter()

    assert asyncio.run(limiter.check_and_record("ip:127.0.0.1", limit=2, window_seconds=60)) is None
    assert asyncio.run(limiter.check_and_record("ip:127.0.0.1", limit=2, window_seconds=60)) is None

    retry_after = asyncio.run(limiter.check_and_record("ip:127.0.0.1", limit=2, window_seconds=60))

    assert retry_after is not None
    assert retry_after > 0


def test_build_verification_url_includes_token() -> None:
    url = email_backend.build_verification_url("abc123")

    assert url == "https://mdrfc.example.com/verify-email?token=abc123"


def test_send_verification_email_uses_smtp(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeSMTP:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            captured["host"] = host
            captured["port"] = port
            captured["timeout"] = timeout
            captured["started_tls"] = False
            captured["logged_in"] = None
            captured["message"] = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def starttls(self, context) -> None:
            captured["started_tls"] = True

        def login(self, username: str, password: str) -> None:
            captured["logged_in"] = (username, password)

        def send_message(self, message) -> None:
            captured["message"] = message

    monkeypatch.setattr(email_backend, "SMTP", FakeSMTP)

    email_backend.send_verification_email(
        to_email="alice@example.com",
        username="alice",
        verification_token="abc123",
        expires_at=datetime(2026, 3, 9, 12, 0, 0),
    )

    assert captured["host"] == "smtp.example.com"
    assert captured["port"] == 587
    assert captured["started_tls"] is True
    assert captured["logged_in"] == ("smtp-user", "smtp-password")

    message = captured["message"]
    assert message is not None
    assert message["To"] == "alice@example.com"
    assert "https://mdrfc.example.com/verify-email?token=abc123" in message.as_string()


def test_post_new_user_queues_verification_email(monkeypatch: pytest.MonkeyPatch) -> None:
    background_tasks = BackgroundTasks()
    server.signup_rate_limiter = SlidingWindowRateLimiter()

    async def fake_create_new_user(**kwargs):
        return auth.SignupResult(
            created_at=datetime(2026, 3, 9, 12, 0, 0),
            verification_expires_at=datetime(2026, 3, 9, 13, 0, 0),
            verification_token="raw-token",
        )

    def fake_send_verification_email_task(**kwargs) -> None:
        return None

    monkeypatch.setattr(server, "create_new_user", fake_create_new_user)
    monkeypatch.setattr(server, "send_verification_email_task", fake_send_verification_email_task)

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/signup",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "app": server.app,
    }
    request = Request(scope)
    payload = PostSignupRequest(
        username="Alice",
        email="alice@example.com",
        name_first="Alice",
        name_last="Smith",
        password="StrongPassword1",
    )

    response = asyncio.run(server.post_new_user(background_tasks, request, payload))

    assert response.metadata["verification_required"] is True
    assert response.metadata["verification_token"] == "raw-token"
    assert len(background_tasks.tasks) == 1
    assert background_tasks.tasks[0].func is fake_send_verification_email_task
    assert background_tasks.tasks[0].kwargs["verification_token"] == "raw-token"
