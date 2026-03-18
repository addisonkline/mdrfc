import asyncio
from datetime import timedelta

import jwt
import pytest
from fastapi import HTTPException

from mdrfc.backend import auth


def test_normalize_username_strips_and_lowercases() -> None:
    assert auth.normalize_username("  Alice.Admin  ") == "alice.admin"


def test_hash_verification_token_is_deterministic() -> None:
    assert auth.hash_verification_token("token") == auth.hash_verification_token(
        "token"
    )
    assert auth.hash_verification_token("token") != auth.hash_verification_token(
        "other-token"
    )


def test_create_access_token_encodes_subject_and_expiry() -> None:
    token = auth.create_access_token(
        data={"sub": "alice"},
        expires_delta=timedelta(minutes=5),
    )

    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])

    assert payload["sub"] == "alice"
    assert payload["exp"] > 0


def test_authenticate_user_returns_false_for_missing_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_user_from_db(_: str):
        return None

    monkeypatch.setattr(auth, "get_user_from_db", fake_get_user_from_db)

    result = asyncio.run(auth.authenticate_user("alice", "StrongPassword1"))

    assert result is False


def test_get_current_user_rejects_token_without_subject() -> None:
    token = auth.create_access_token(data={})

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(auth.get_current_user(token))

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "could not validate credentials"


def test_get_current_user_if_one_returns_none_without_token() -> None:
    assert asyncio.run(auth.get_current_user_if_one(None)) is None


def test_get_current_active_admin_requires_admin(user_factory) -> None:
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(auth.get_current_active_admin(user_factory(is_admin=False)))

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "unauthorized"
