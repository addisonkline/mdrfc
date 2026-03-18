from datetime import datetime

import pytest

from mdrfc.backend import email as email_backend


def test_send_verification_email_uses_resend_when_api_key_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_send(params):
        captured["params"] = params
        return {"id": "email_123"}

    monkeypatch.setattr(
        email_backend,
        "load_smtp_settings",
        lambda: email_backend.SMTPSettings(
            app_base_url="https://mdrfc.example.com",
            email_from="noreply@mdrfc.example.com",
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="smtp-user",
            smtp_password="smtp-password",
            smtp_starttls=True,
            smtp_use_ssl=False,
            resend_api_key="resend-key",
        ),
    )
    monkeypatch.setattr(email_backend.resend.Emails, "send", fake_send)

    email_backend.send_verification_email(
        to_email="alice@example.com",
        username="alice",
        verification_token="abc123",
        expires_at=datetime(2026, 3, 9, 12, 0, 0),
    )

    params = captured["params"]
    assert params["to"] == ["alice@example.com"]
    assert "verify-email?token=abc123" in params["html"]


def test_send_verification_email_task_logs_and_swallows_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_send_verification_email(**kwargs) -> None:
        raise RuntimeError("smtp down")

    def fake_logger_exception(message: str, to_email: str) -> None:
        captured["message"] = message
        captured["to_email"] = to_email

    monkeypatch.setattr(
        email_backend, "send_verification_email", fake_send_verification_email
    )
    monkeypatch.setattr(email_backend.logger, "exception", fake_logger_exception)

    email_backend.send_verification_email_task(
        to_email="alice@example.com",
        username="alice",
        verification_token="abc123",
        expires_at=datetime(2026, 3, 9, 12, 0, 0),
    )

    assert captured["message"] == "failed to send verification email to %s"
    assert captured["to_email"] == "alice@example.com"


def test_check_valid_email_rejects_non_matching_suffix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(email_backend, "REQUIRED_EMAIL_SUFFIX", "@openai.com")

    with pytest.raises(Exception) as excinfo:
        email_backend.check_valid_email("alice@example.com")

    assert "cannot make an account with this email" in str(excinfo.value)
