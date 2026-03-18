import asyncio

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from mdrfc.requests import (
    PostVerifyEmailRequest,
    validate_post_rfc_comment_request,
    validate_post_signup_request,
    validate_verification_token,
)


class JsonRequest:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    async def json(self) -> dict[str, object]:
        return self._payload


def test_validate_post_signup_request_returns_validated_payload() -> None:
    payload = asyncio.run(
        validate_post_signup_request(
            JsonRequest(
                {
                    "username": "Alice.Admin",
                    "email": "Alice@Example.com",
                    "name_first": "Alice",
                    "name_last": "Smith",
                    "password": "StrongPassword1",
                }
            )
        )
    )

    assert payload.username == "alice.admin"
    assert payload.email == "alice@example.com"


def test_validate_post_signup_request_wraps_validation_errors() -> None:
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            validate_post_signup_request(
                JsonRequest(
                    {
                        "username": "al",
                        "email": "alice@example.com",
                        "name_first": "Alice",
                        "name_last": "Smith",
                        "password": "StrongPassword1",
                    }
                )
            )
        )

    assert excinfo.value.status_code == 422
    assert "request validation failed" in str(excinfo.value.detail)


def test_post_verify_email_request_strips_token_whitespace_and_forbids_extra_fields() -> None:
    payload = PostVerifyEmailRequest.model_validate({"token": "  " + ("a" * 32) + "  "})

    assert payload.token.get_secret_value() == "a" * 32

    with pytest.raises(ValidationError):
        PostVerifyEmailRequest.model_validate(
            {
                "token": "a" * 32,
                "extra": "not-allowed",
            }
        )


def test_validate_verification_token_rejects_short_values() -> None:
    with pytest.raises(HTTPException) as excinfo:
        validate_verification_token(PostVerifyEmailRequest.model_validate({"token": "a" * 32}).token.__class__("short"))

    assert excinfo.value.status_code == 422
    assert excinfo.value.detail == "verification token is invalid"


def test_validate_post_rfc_comment_request_accepts_null_parent_id() -> None:
    payload = asyncio.run(
        validate_post_rfc_comment_request(
            JsonRequest(
                {
                    "parent_comment_id": None,
                    "content": "This is a valid test comment.",
                }
            )
        )
    )

    assert payload.parent_comment_id is None
    assert payload.content == "This is a valid test comment."
