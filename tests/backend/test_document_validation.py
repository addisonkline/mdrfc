from datetime import datetime

import pytest
from pydantic import ValidationError

import mdrfc.backend.constants as consts
from mdrfc.backend.document import (
    QuarantinedRFCSummary,
    RFCRevisionRequest,
    validate_agent_contributor,
    validate_agent_contributors,
    validate_quarantine_rfc_reason,
    validate_rfc_status,
)


def test_validate_agent_contributor_accepts_agent_and_host() -> None:
    assert validate_agent_contributor("codex@openai") == "codex@openai"


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("codex-openai", "invalid agent contributor format"),
        ("@openai", "agent name must be at least"),
        ("codex@", "host name must be at least"),
        (
            "c" * (consts.LEN_CONTRIB_AGENT_NAME_MAX + 1) + "@openai",
            "agent name must be no greater",
        ),
    ],
)
def test_validate_agent_contributor_rejects_invalid_values(
    value: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_agent_contributor(value)


def test_validate_agent_contributors_checks_each_value() -> None:
    with pytest.raises(ValueError, match="invalid agent contributor format"):
        validate_agent_contributors(["codex@openai", "invalid"])


@pytest.mark.parametrize("status", ["draft", "open", "accepted", "rejected"])
def test_validate_rfc_status_accepts_editable_statuses(status: str) -> None:
    assert validate_rfc_status(status) == status


def test_validate_rfc_status_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="invalid status value"):
        validate_rfc_status("invalid")


def test_validate_quarantine_rfc_reason_enforces_bounds() -> None:
    with pytest.raises(
        ValueError,
        match=f"at least {consts.LEN_QUARANTINED_RFC_REASON_MIN} characters long",
    ):
        validate_quarantine_rfc_reason("short")

    with pytest.raises(
        ValueError,
        match=f"no greater than {consts.LEN_QUARANTINED_RFC_REASON_MAX} characters long",
    ):
        validate_quarantine_rfc_reason(
            "r" * (consts.LEN_QUARANTINED_RFC_REASON_MAX + 1)
        )


def test_rfc_revision_request_accepts_partial_updates() -> None:
    request = RFCRevisionRequest(
        title="Updated RFC",
        public=True,
    )

    assert request.title == "Updated RFC"
    assert request.slug is None
    assert request.public is True


def test_rfc_revision_request_defaults_public_to_none() -> None:
    request = RFCRevisionRequest(title="Updated RFC")

    assert request.public is None


def test_rfc_revision_request_validates_agent_contributors() -> None:
    with pytest.raises(ValidationError, match="invalid agent contributor format"):
        RFCRevisionRequest(agent_contributors=["invalid"])


def test_quarantined_rfc_summary_accepts_valid_short_slug() -> None:
    summary = QuarantinedRFCSummary(
        quarantine_id=1,
        quarantined_by_name_last="Smith",
        quarantined_by_name_first="Alice",
        quarantined_at=datetime(2026, 3, 9, 12, 0, 0),
        reason="RFC violates moderation policy.",
        rfc_id=3,
        rfc_title="Testing RFC",
        rfc_slug="slug",
        rfc_status="draft",
        rfc_summary="Summary for testing RFC behavior.",
    )

    assert summary.rfc_slug == "slug"
