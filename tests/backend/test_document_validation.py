import pytest
from pydantic import ValidationError

import mdrfc.backend.constants as consts
from mdrfc.backend.document import (
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
        ("c" * (consts.LEN_CONTRIB_AGENT_NAME_MAX + 1) + "@openai", "agent name must be no greater"),
    ],
)
def test_validate_agent_contributor_rejects_invalid_values(value: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        validate_agent_contributor(value)


def test_validate_agent_contributors_checks_each_value() -> None:
    with pytest.raises(ValueError, match="invalid agent contributor format"):
        validate_agent_contributors(["codex@openai", "invalid"])


@pytest.mark.parametrize("status", ["draft", "open"])
def test_validate_rfc_status_accepts_editable_statuses(status: str) -> None:
    assert validate_rfc_status(status) == status


def test_validate_rfc_status_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="invalid status value"):
        validate_rfc_status("accepted")


def test_validate_quarantine_rfc_reason_enforces_bounds() -> None:
    with pytest.raises(ValueError, match="at least"):
        validate_quarantine_rfc_reason("short")

    with pytest.raises(ValueError, match="no greater"):
        validate_quarantine_rfc_reason("r" * (consts.LEN_QUARANTINED_RFC_REASON_MAX + 1))


def test_rfc_revision_request_accepts_partial_updates() -> None:
    request = RFCRevisionRequest(
        title="Updated RFC",
        public=True,
    )

    assert request.title == "Updated RFC"
    assert request.slug is None
    assert request.public is True


def test_rfc_revision_request_validates_agent_contributors() -> None:
    with pytest.raises(ValidationError, match="invalid agent contributor format"):
        RFCRevisionRequest(agent_contributors=["invalid"])
