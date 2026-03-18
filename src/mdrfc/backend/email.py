from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
import logging
from os import getenv
from smtplib import SMTP, SMTP_SSL
from ssl import create_default_context
from urllib.parse import urlencode

from dotenv import load_dotenv
from fastapi import HTTPException
import resend

import mdrfc.backend.constants as consts


logger = logging.getLogger(__name__)

load_dotenv()
REQUIRED_EMAIL_SUFFIX = getenv("REQUIRED_EMAIL_SUFFIX")


def _get_bool_env(name: str, default: bool) -> bool:
    value = getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class SMTPSettings:
    app_base_url: str
    email_from: str
    smtp_host: str
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    smtp_starttls: bool
    smtp_use_ssl: bool
    resend_api_key: str | None


def load_smtp_settings() -> SMTPSettings:
    app_base_url = getenv("APP_BASE_URL")
    email_from = getenv("EMAIL_FROM")
    smtp_host = getenv("SMTP_HOST")

    if not app_base_url:
        raise RuntimeError(
            "environment variable APP_BASE_URL is required but was not found"
        )
    if not email_from:
        raise RuntimeError(
            "environment variable EMAIL_FROM is required but was not found"
        )
    if not smtp_host:
        raise RuntimeError(
            "environment variable SMTP_HOST is required but was not found"
        )

    smtp_port_raw = getenv("SMTP_PORT", "587")
    try:
        smtp_port = int(smtp_port_raw)
    except ValueError as exc:
        raise RuntimeError("environment variable SMTP_PORT must be an integer") from exc

    return SMTPSettings(
        app_base_url=app_base_url.rstrip("/"),
        email_from=email_from,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=getenv("SMTP_USERNAME"),
        smtp_password=getenv("SMTP_PASSWORD"),
        smtp_starttls=_get_bool_env("SMTP_STARTTLS", True),
        smtp_use_ssl=_get_bool_env("SMTP_USE_SSL", False),
        resend_api_key=getenv("RESEND_API_KEY"),
    )


def build_verification_url(token: str, *, app_base_url: str | None = None) -> str:
    if app_base_url is None:
        app_base_url = load_smtp_settings().app_base_url
    query = urlencode({"token": token})
    return f"{app_base_url.rstrip('/')}/verify-email?{query}"


def _build_verification_message(
    *,
    email_from: str,
    to_email: str,
    username: str,
    verification_url: str,
    expires_at: datetime,
) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = "Verify your MDRFC account"
    message["From"] = email_from
    message["To"] = to_email

    expires_at_display = expires_at.isoformat(timespec="seconds")
    text_body = (
        f"Hi {username},\n\n"
        "Thanks for signing up for MDRFC.\n\n"
        "Verify your email address by opening this link:\n"
        f"{verification_url}\n\n"
        f"This link expires at {expires_at_display} UTC.\n"
    )
    html_body = build_html_body(
        username=username,
        verification_url=verification_url,
        expires_at_display=expires_at_display,
    )

    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")
    return message


def build_html_body(
    username: str,
    verification_url: str,
    expires_at_display: str,
) -> str:
    html_body = (
        f"<p>Hi {username},</p>"
        "<p>Thanks for signing up for MDRFC.</p>"
        f'<p><a href="{verification_url}">Verify your email address</a></p>'
        f"<p>This link expires at {expires_at_display} UTC.</p>"
    )
    return html_body


def check_valid_email(
    email: str,
) -> None:
    if REQUIRED_EMAIL_SUFFIX is not None:
        if not email.endswith(REQUIRED_EMAIL_SUFFIX):
            raise HTTPException(
                status_code=401, detail="cannot make an account with this email"
            )


def send_verification_email(
    *,
    to_email: str,
    username: str,
    verification_token: str,
    expires_at: datetime,
) -> None:
    settings = load_smtp_settings()
    verification_url = build_verification_url(
        verification_token,
        app_base_url=settings.app_base_url,
    )
    message = _build_verification_message(
        email_from=settings.email_from,
        to_email=to_email,
        username=username,
        verification_url=verification_url,
        expires_at=expires_at,
    )
    if settings.resend_api_key is not None:
        params: resend.Emails.SendParams = {
            "from": message.get("From"),  # type: ignore
            "to": [message.get("To")],  # type: ignore
            "subject": message.get("Subject"),  # type: ignore
            "html": build_html_body(
                username=username,
                verification_url=verification_url,
                expires_at_display=expires_at.isoformat(timespec="seconds"),
            ),
        }
        email = resend.Emails.send(params)
    else:
        smtp_cls = SMTP_SSL if settings.smtp_use_ssl else SMTP
        with smtp_cls(
            host=settings.smtp_host,
            port=settings.smtp_port,
            timeout=consts.SMTP_TIMEOUT_SECONDS,
        ) as smtp:
            if settings.smtp_use_ssl:
                pass
            elif settings.smtp_starttls:
                smtp.starttls(context=create_default_context())

            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)

            smtp.send_message(message)


def send_verification_email_task(
    *,
    to_email: str,
    username: str,
    verification_token: str,
    expires_at: datetime,
) -> None:
    try:
        send_verification_email(
            to_email=to_email,
            username=username,
            verification_token=verification_token,
            expires_at=expires_at,
        )
    except Exception:
        logger.exception("failed to send verification email to %s", to_email)
