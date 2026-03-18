import pytest

import mdrfc.backend.constants as consts
from mdrfc.backend.users import (
    validate_email,
    validate_name_first,
    validate_name_last,
    validate_password,
    validate_username,
)


def test_validate_username_normalizes_case() -> None:
    assert validate_username("Alice.Admin") == "alice.admin"


@pytest.mark.parametrize(
    ("username", "message"),
    [
        ("ab", "at least"),
        ("alice!", "invalid username schema"),
        ("-alice", "invalid username schema"),
        ("alice-", "invalid username schema"),
        ("a" * (consts.LEN_USERNAME_MAX + 1), "no greater"),
    ],
)
def test_validate_username_rejects_invalid_values(username: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        validate_username(username)


def test_validate_email_normalizes_case() -> None:
    assert validate_email("Alice@Example.COM") == "alice@example.com"


@pytest.mark.parametrize(
    ("email", "message"),
    [
        ("ab", "at least"),
        ("alice.example.com", "invalid email schema"),
        ("alice@", "invalid email schema"),
        ("a" * (consts.LEN_EMAIL_MAX + 1) + "@x.com", "no greater"),
    ],
)
def test_validate_email_rejects_invalid_values(email: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        validate_email(email)


def test_validate_password_rejects_all_whitespace() -> None:
    with pytest.raises(ValueError, match="all whitespace"):
        validate_password(" " * consts.LEN_PASSWORD_PLAIN_MIN)


def test_validate_name_fields_enforce_length_bounds() -> None:
    with pytest.raises(ValueError, match="first name must be at least"):
        validate_name_first("Al")

    with pytest.raises(ValueError, match="last name must be no greater"):
        validate_name_last("S" * (consts.LEN_NAME_LAST_MAX + 1))
