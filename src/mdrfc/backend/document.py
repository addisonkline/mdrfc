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


class RFCDocumentUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    status: RFCStatus | None = None
    content: str | None = None
    summary: str | None = None
    agent_contributors: list[AgentContributor] | None = None