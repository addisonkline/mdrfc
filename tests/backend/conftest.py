# ruff: noqa: E402

import importlib
import os
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest


BACKEND_TEST_ENV = {
    "SECRET_KEY": "test-secret-key-for-backend-suite-32",
    "JWT_ALGORITHM": "HS256",
    "DATABASE_URL": "postgresql://test:test@localhost/test",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "AUTH_DEBUG_RETURN_VERIFICATION_TOKEN": "true",
    "EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES": "60",
    "APP_BASE_URL": "https://mdrfc.example.com",
    "EMAIL_FROM": "noreply@mdrfc.example.com",
    "SMTP_HOST": "smtp.example.com",
    "SMTP_PORT": "587",
    "SMTP_USERNAME": "smtp-user",
    "SMTP_PASSWORD": "smtp-password",
    "SMTP_STARTTLS": "true",
}


for key, value in BACKEND_TEST_ENV.items():
    os.environ[key] = value

for key in ("REQUIRED_EMAIL_SUFFIX", "RESEND_API_KEY", "SMTP_USE_SSL"):
    os.environ.pop(key, None)


from mdrfc import server
from mdrfc.backend import auth
from mdrfc.backend import email as email_backend
from mdrfc.backend.comment import RFCComment
from mdrfc.backend.document import RFCDocument, RFCDocumentSummary, RFCRevision, RFCRevisionSummary
from mdrfc.backend.rate_limit import SlidingWindowRateLimiter
from mdrfc.backend.users import User, UserInDB


FIXED_TIMESTAMP = datetime(2026, 3, 9, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def backend_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in BACKEND_TEST_ENV.items():
        monkeypatch.setenv(key, value)

    for key in ("REQUIRED_EMAIL_SUFFIX", "RESEND_API_KEY", "SMTP_USE_SSL"):
        monkeypatch.delenv(key, raising=False)

    monkeypatch.setattr(auth, "DEBUG_RETURN_VERIFICATION_TOKEN", True)
    monkeypatch.setattr(server, "DEBUG_RETURN_VERIFICATION_TOKEN", True)
    monkeypatch.setattr(email_backend, "REQUIRED_EMAIL_SUFFIX", None)
    monkeypatch.setattr(server, "signup_rate_limiter", SlidingWindowRateLimiter())
    server.app.dependency_overrides.clear()


@pytest.fixture
def reload_backend_modules() -> Callable[[], tuple[object, object, object]]:
    def _reload() -> tuple[object, object, object]:
        importlib.reload(email_backend)
        importlib.reload(auth)
        importlib.reload(server)
        return auth, email_backend, server

    return _reload


@pytest.fixture
def fixed_timestamp() -> datetime:
    return FIXED_TIMESTAMP


@pytest.fixture
def user_factory(fixed_timestamp: datetime) -> Callable[..., User]:
    def _make_user(
        *,
        id: int = 1,
        username: str = "alice",
        email: str = "alice@example.com",
        name_first: str = "Alice",
        name_last: str = "Smith",
        is_verified: bool = True,
        verified_at: datetime | None = None,
        created_at: datetime | None = None,
        is_admin: bool = False,
    ) -> User:
        created = created_at or fixed_timestamp
        verified = verified_at
        if is_verified and verified is None:
            verified = created

        return User(
            id=id,
            username=username,
            email=email,
            name_first=name_first,
            name_last=name_last,
            is_verified=is_verified,
            verified_at=verified,
            created_at=created,
            is_admin=is_admin,
        )

    return _make_user


@pytest.fixture
def user_in_db_factory(fixed_timestamp: datetime) -> Callable[..., UserInDB]:
    def _make_user_in_db(
        *,
        id: int = 1,
        username: str = "alice",
        email: str = "alice@example.com",
        name_first: str = "Alice",
        name_last: str = "Smith",
        password: str = "StrongPassword1",
        is_verified: bool = True,
        verified_at: datetime | None = None,
        verification_token_hash: str | None = None,
        verification_token_expires_at: datetime | None = None,
        created_at: datetime | None = None,
        is_admin: bool = False,
    ) -> UserInDB:
        created = created_at or fixed_timestamp
        verified = verified_at
        if is_verified and verified is None:
            verified = created

        token_hash = verification_token_hash
        token_expires = verification_token_expires_at
        if not is_verified:
            token_hash = token_hash or "verification-token-hash"
            token_expires = token_expires or (created + timedelta(hours=1))

        return UserInDB(
            id=id,
            username=username,
            email=email,
            name_first=name_first,
            name_last=name_last,
            is_verified=is_verified,
            verified_at=verified,
            created_at=created,
            is_admin=is_admin,
            password_argon2=auth.get_password_hash(password),
            verification_token_hash=token_hash,
            verification_token_expires_at=token_expires,
        )

    return _make_user_in_db


@pytest.fixture
def rfc_summary_factory(fixed_timestamp: datetime) -> Callable[..., RFCDocumentSummary]:
    def _make_rfc_summary(
        *,
        id: int = 1,
        title: str = "Testing RFC",
        slug: str = "testing-rfc",
        status: str = "draft",
        summary: str = "Summary for testing RFC behavior.",
        public: bool = False,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        author_name_first: str = "Alice",
        author_name_last: str = "Smith",
    ) -> RFCDocumentSummary:
        created = created_at or fixed_timestamp
        updated = updated_at or created
        return RFCDocumentSummary(
            id=id,
            author_name_first=author_name_first,
            author_name_last=author_name_last,
            created_at=created,
            updated_at=updated,
            title=title,
            slug=slug,
            status=status,  # type: ignore[arg-type]
            summary=summary,
            public=public,
        )

    return _make_rfc_summary


@pytest.fixture
def rfc_document_factory(fixed_timestamp: datetime) -> Callable[..., RFCDocument]:
    def _make_rfc_document(
        *,
        id: int = 1,
        title: str = "Testing RFC",
        slug: str = "testing-rfc",
        status: str = "draft",
        summary: str = "Summary for testing RFC behavior.",
        content: str = "Content for testing RFC behavior.",
        public: bool = False,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        author_name_first: str = "Alice",
        author_name_last: str = "Smith",
        revisions: list[UUID] | None = None,
        current_revision: UUID | None = None,
        agent_contributions: dict[UUID, list[str]] | None = None,
    ) -> RFCDocument:
        created = created_at or fixed_timestamp
        updated = updated_at or created
        revision_ids = revisions or [uuid4()]
        current = current_revision or revision_ids[-1]
        contributions = agent_contributions or {revision_id: [] for revision_id in revision_ids}

        return RFCDocument(
            id=id,
            author_name_first=author_name_first,
            author_name_last=author_name_last,
            created_at=created,
            updated_at=updated,
            title=title,
            slug=slug,
            status=status,  # type: ignore[arg-type]
            summary=summary,
            content=content,
            revisions=revision_ids,
            current_revision=current,
            agent_contributions=contributions,
            public=public,
        )

    return _make_rfc_document


@pytest.fixture
def revision_summary_factory(fixed_timestamp: datetime) -> Callable[..., RFCRevisionSummary]:
    def _make_revision_summary(
        *,
        id: UUID | None = None,
        rfc_id: int = 1,
        created_at: datetime | None = None,
        author_name_first: str = "Alice",
        author_name_last: str = "Smith",
        agent_contributors: list[str] | None = None,
        message: str = "Revise RFC content",
        public: bool = False,
    ) -> RFCRevisionSummary:
        return RFCRevisionSummary(
            id=id or uuid4(),
            rfc_id=rfc_id,
            created_at=created_at or fixed_timestamp,
            author_name_first=author_name_first,
            author_name_last=author_name_last,
            agent_contributors=agent_contributors or [],
            message=message,
            public=public,
        )

    return _make_revision_summary


@pytest.fixture
def revision_factory(fixed_timestamp: datetime) -> Callable[..., RFCRevision]:
    def _make_revision(
        *,
        id: UUID | None = None,
        rfc_id: int = 1,
        created_at: datetime | None = None,
        author_name_first: str = "Alice",
        author_name_last: str = "Smith",
        agent_contributors: list[str] | None = None,
        title: str = "Testing RFC",
        slug: str = "testing-rfc",
        status: str = "draft",
        content: str = "Content for testing RFC behavior.",
        summary: str = "Summary for testing RFC behavior.",
        message: str = "Revise RFC content",
        public: bool = False,
    ) -> RFCRevision:
        return RFCRevision(
            id=id or uuid4(),
            rfc_id=rfc_id,
            created_at=created_at or fixed_timestamp,
            author_name_first=author_name_first,
            author_name_last=author_name_last,
            agent_contributors=agent_contributors or [],
            title=title,
            slug=slug,
            status=status,  # type: ignore[arg-type]
            content=content,
            summary=summary,
            message=message,
            public=public,
        )

    return _make_revision


@pytest.fixture
def comment_factory(fixed_timestamp: datetime) -> Callable[..., RFCComment]:
    def _make_comment(
        *,
        id: int = 1,
        rfc_id: int = 1,
        parent_id: int | None = None,
        created_at: datetime | None = None,
        content: str = "Test comment content",
        author_name_first: str = "Alice",
        author_name_last: str = "Smith",
    ) -> RFCComment:
        return RFCComment(
            id=id,
            rfc_id=rfc_id,
            parent_id=parent_id,
            created_at=created_at or fixed_timestamp,
            content=content,
            author_name_first=author_name_first,
            author_name_last=author_name_last,
        )

    return _make_comment
