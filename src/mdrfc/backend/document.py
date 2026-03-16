from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel

import mdrfc.backend.constants as consts
from mdrfc.backend.users import (
    validate_name_last,
    validate_name_first
)

RFCStatus = Literal["draft", "open", "accepted", "rejected"]


def validate_agent_contributor(value: str) -> str:
    if "@" not in value:
        raise ValueError("invalid agent contributor format")
    agent, host = value.split("@", maxsplit=1)
    if len(agent) < consts.LEN_CONTRIB_AGENT_NAME_MIN:
        raise ValueError(f"agent name must be at least {consts.LEN_CONTRIB_AGENT_NAME_MIN} characters long")
    if len(agent) > consts.LEN_CONTRIB_AGENT_NAME_MAX:
        raise ValueError(f"agent name must be no greater than {consts.LEN_CONTRIB_AGENT_NAME_MAX} characters long")
    if len(host) < consts.LEN_CONTRIB_HOST_NAME_MIN:
        raise ValueError(f"host name must be at least {consts.LEN_CONTRIB_HOST_NAME_MIN} characters long")
    if len(host) > consts.LEN_CONTRIB_HOST_NAME_MAX:
        raise ValueError(f"host name must be no greater than {consts.LEN_CONTRIB_HOST_NAME_MAX} characters long")
    return value


AgentContributor = Annotated[str, AfterValidator(validate_agent_contributor)]
AgentContributions = dict[UUID, list[AgentContributor]]


def validate_rfc_title(title: str) -> str:
    if len(title) < consts.LEN_RFC_TITLE_MIN:
        raise ValueError(f"title must be at least {consts.LEN_RFC_TITLE_MIN} characters long")
    if len(title) > consts.LEN_RFC_TITLE_MAX:
        raise ValueError(f"title must be no greater than {consts.LEN_RFC_TITLE_MAX} characters long")
    return title


def validate_rfc_slug(slug: str) -> str:
    if len(slug) < consts.LEN_RFC_SLUG_MIN:
        raise ValueError(f"slug must be at least {consts.LEN_RFC_SLUG_MIN} characters long")
    if len(slug) > consts.LEN_RFC_SLUG_MAX:
        raise ValueError(f"slug must be no greater than {consts.LEN_RFC_SLUG_MAX} characters long")
    return slug


def validate_rfc_status(status: str) -> Literal["draft", "open"]:
    if status == "draft":
        return "draft"
    elif status == "open":
        return "open"
    else:
        raise ValueError("invalid status value")


def validate_rfc_summary(summary: str) -> str:
    if len(summary) < consts.LEN_RFC_SUMMARY_MIN:
        raise ValueError(f"summary must be at least {consts.LEN_RFC_SUMMARY_MIN} characters long")
    if len(summary) > consts.LEN_RFC_SUMMARY_MAX:
        raise ValueError(f"summary must be no greater than {consts.LEN_RFC_SUMMARY_MAX} characters long")
    return summary


def validate_rfc_content(content: str) -> str:
    if len(content) < consts.LEN_RFC_CONTENT_MIN:
        raise ValueError(f"content must be at least {consts.LEN_RFC_CONTENT_MIN} characters long")
    if len(content) > consts.LEN_RFC_CONTENT_MAX:
        raise ValueError(f"content must be no greater than {consts.LEN_RFC_CONTENT_MAX} characters long")
    return content


def validate_agent_contributors(contributors: list[str]) -> list[str]:
    for contributor in contributors:
        validate_agent_contributor(contributor)
    return contributors


def validate_revision_message(message: str) -> str:
    if len(message) < consts.LEN_REVISION_MSG_MIN:
        raise ValueError(f"message must be at least {consts.LEN_REVISION_MSG_MIN} characters long")
    if len(message) > consts.LEN_REVISION_MSG_MAX:
        raise ValueError(f"message must be no greater than {consts.LEN_REVISION_MSG_MAX} characters long")
    return message


def validate_quarantine_rfc_reason(message: str) -> str:
    if len(message) < consts.LEN_QUARANTINED_RFC_REASON_MIN:
        raise ValueError(f"message must be at least {consts.LEN_QUARANTINED_COMMENT_REASON_MIN} characters long")
    if len(message) > consts.LEN_QUARANTINED_RFC_REASON_MAX:
        raise ValueError(f"message must be no greater than {consts.LEN_QUARANTINED_COMMENT_REASON_MAX} characters long")
    return message

#
# DOCUMENT types
#
class RFCDocument(BaseModel):
    id: int
    author_name_last: Annotated[str, AfterValidator(validate_name_last)]
    author_name_first: Annotated[str, AfterValidator(validate_name_first)]
    created_at: datetime
    updated_at: datetime
    title: Annotated[str, AfterValidator(validate_rfc_title)]
    slug: Annotated[str, AfterValidator(validate_rfc_slug)]
    status: Annotated[RFCStatus, AfterValidator(validate_rfc_status)]
    content: Annotated[str, AfterValidator(validate_rfc_content)]
    summary: Annotated[str, AfterValidator(validate_rfc_summary)]
    revisions: list[UUID]
    current_revision: UUID
    agent_contributions: AgentContributions
    public: bool


class RFCDocumentSummary(BaseModel):
    id: int
    author_name_last: Annotated[str, AfterValidator(validate_name_last)]
    author_name_first: Annotated[str, AfterValidator(validate_name_first)]
    created_at: datetime
    updated_at: datetime
    title: Annotated[str, AfterValidator(validate_rfc_title)]
    slug: Annotated[str, AfterValidator(validate_rfc_slug)]
    status: Annotated[RFCStatus, AfterValidator(validate_rfc_status)]
    summary: Annotated[str, AfterValidator(validate_rfc_summary)]
    public: bool 


class RFCDocumentInDB(BaseModel):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    title: str
    slug: str
    status: RFCStatus
    content: str
    summary: str
    revisions: list[UUID]
    current_revision: UUID
    agent_contributions: AgentContributions
    public: bool = False
    quarantined: bool = False


class QuarantinedRFC(BaseModel):
    quarantine_id: int
    quarantined_by_name_last: Annotated[str, AfterValidator(validate_name_last)]
    quarantined_by_name_first: Annotated[str, AfterValidator(validate_name_first)]
    quarantined_at: datetime
    reason: Annotated[str, AfterValidator(validate_quarantine_rfc_reason)]
    rfc: RFCDocument


class QuarantinedRFCSummary(BaseModel):
    quarantine_id: int
    quarantined_by_name_last: Annotated[str, AfterValidator(validate_name_last)]
    quarantined_by_name_first: Annotated[str, AfterValidator(validate_name_first)]
    quarantined_at: datetime
    reason: Annotated[str, AfterValidator(validate_quarantine_rfc_reason)]
    rfc_id: int
    rfc_title: Annotated[str, AfterValidator(validate_rfc_title)]
    rfc_slug: Annotated[str, AfterValidator(validate_rfc_content)]
    rfc_status: Annotated[RFCStatus, AfterValidator(validate_rfc_status)]
    rfc_summary: Annotated[str, AfterValidator(validate_rfc_summary)]


class QuarantinedRFCInDB(BaseModel):
    quarantine_id: int
    quarantined_by: int
    quarantined_at: datetime
    reason: str
    rfc_id: int


#
# REVISION types
#
class RFCRevision(BaseModel):
    id: UUID
    rfc_id: int
    created_at: datetime
    author_name_last: Annotated[str, AfterValidator(validate_name_last)]
    author_name_first: Annotated[str, AfterValidator(validate_name_first)]
    agent_contributors: list[AgentContributor]
    title: Annotated[str, AfterValidator(validate_rfc_title)]
    slug: Annotated[str, AfterValidator(validate_rfc_slug)]
    status: Annotated[RFCStatus, AfterValidator(validate_rfc_status)]
    content: Annotated[str, AfterValidator(validate_rfc_content)]
    summary: Annotated[str, AfterValidator(validate_rfc_summary)]
    message: Annotated[str, AfterValidator(validate_revision_message)]
    public: bool = False


class RFCRevisionSummary(BaseModel):
    id: UUID
    rfc_id: int
    created_at: datetime
    author_name_last: Annotated[str, AfterValidator(validate_name_last)]
    author_name_first: Annotated[str, AfterValidator(validate_name_first)]
    agent_contributors: list[AgentContributor]
    message: Annotated[str, AfterValidator(validate_revision_message)]
    public: bool = False


class RFCRevisionInDB(BaseModel):
    id: UUID
    rfc_id: int
    created_at: datetime
    created_by: int
    agent_contributors: list[AgentContributor]
    title: str
    slug: str
    status: RFCStatus
    content: str
    summary: str
    message: str
    public: bool = False


class RFCRevisionRequest(BaseModel):
    title: Annotated[str, AfterValidator(validate_rfc_title)] | None = None
    slug: Annotated[str, AfterValidator(validate_rfc_slug)] | None = None
    status: Annotated[Literal["draft", "open"], AfterValidator(validate_rfc_status)] | None = None
    summary: Annotated[str, AfterValidator(validate_rfc_summary)] | None = None
    content: Annotated[str, AfterValidator(validate_rfc_content)] | None = None
    agent_contributors: Annotated[list[str], AfterValidator(validate_agent_contributors)] | None = None
    public: bool = False
