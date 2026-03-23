from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    UUID,
)

from mdrfc.backend import constants as consts


metadata_obj = MetaData()

users = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String(consts.LEN_USERNAME_MAX), nullable=False, unique=True),
    Column("email", String(consts.LEN_EMAIL_MAX), nullable=False, unique=True),
    Column("name_last", String(consts.LEN_NAME_LAST_MAX), nullable=False),
    Column("name_first", String(consts.LEN_NAME_FIRST_MAX), nullable=False),
    Column("password_argon2", String(consts.LEN_PASSWORD_ARGON2), nullable=False),
    Column("is_verified", Boolean, nullable=False),
    Column("verified_at", DateTime, nullable=True),
    Column(
        "verification_token_hash",
        String(consts.LEN_VERIFICATION_TOKEN_HASH),
        nullable=True,
    ),
    Column("verification_token_expires_at", DateTime, nullable=True),
    Column("created_at", DateTime, nullable=False),
    Column("is_admin", Boolean, nullable=True),
)

rfcs = Table(
    "rfcs",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("title", String(consts.LEN_RFC_TITLE_MAX), nullable=False),
    Column("slug", String(consts.LEN_RFC_SLUG_MAX), nullable=False),
    Column("status", String(consts.LEN_RFC_STATUS_MAX), nullable=False),
    Column("content", String(consts.LEN_RFC_CONTENT_MAX), nullable=False),
    Column("summary", String(consts.LEN_RFC_SUMMARY_MAX), nullable=False),
    Column("revisions", ARRAY(UUID), nullable=False),
    Column("current_revision", UUID, ForeignKey("rfc_revisions.id"), nullable=False),
    Column("agent_contributions", JSON, nullable=False),
    Column("is_public", Boolean, nullable=True, default=False),
    Column("is_quarantined", Boolean, nullable=True, default=False),
    Column("review_requested", Boolean, nullable=True, default=False),
    Column("is_reviewed", Boolean, nullable=True, default=False),
    Column("review_reason", String(consts.LEN_PATCH_RFC_STATUS_REASON_MAX), nullable=True)
)

rfc_comments = Table(
    "rfc_comments",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column(
        "parent_id",
        Integer,
        ForeignKey("rfc_comments.id", ondelete="CASCADE"),
        nullable=True,
    ),
    Column("rfc_id", Integer, ForeignKey("rfcs.id"), nullable=False),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("content", String(consts.LEN_COMMENT_CONTENT_MAX), nullable=False),
    Column("is_quarantined", Boolean, nullable=True, default=False),
)

rfc_revisions = Table(
    "rfc_revisions",
    metadata_obj,
    Column("id", UUID, primary_key=True),
    Column("rfc_id", Integer, ForeignKey("rfcs.id"), nullable=False),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("agent_contributors", ARRAY(String), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("title", String(consts.LEN_RFC_TITLE_MAX), nullable=False),
    Column("slug", String(consts.LEN_RFC_SLUG_MAX), nullable=False),
    Column("status", String(consts.LEN_RFC_STATUS_MAX), nullable=False),
    Column("content", String(consts.LEN_RFC_CONTENT_MAX), nullable=False),
    Column("summary", String(consts.LEN_RFC_SUMMARY_MAX), nullable=False),
    Column("is_public", Boolean, nullable=True, default=False),
    Column("message", String(consts.LEN_REVISION_MSG_MAX), nullable=False),
)

quarantined_rfcs = Table(
    "quarantined_rfcs",
    metadata_obj,
    Column("quarantine_id", Integer, primary_key=True),
    Column("quarantined_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("quarantined_at", DateTime(timezone=True), nullable=False),
    Column("reason", String(consts.LEN_QUARANTINED_RFC_REASON_MAX), nullable=False),
    Column("rfc_id", Integer, ForeignKey("rfcs.id"), nullable=False),
)

quarantined_comments = Table(
    "quarantined_comments",
    metadata_obj,
    Column("quarantine_id", Integer, primary_key=True),
    Column("quarantined_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("quarantined_at", DateTime(timezone=True), nullable=False),
    Column("reason", String(consts.LEN_QUARANTINED_RFC_REASON_MAX), nullable=False),
    Column("comment_id", Integer, ForeignKey("rfc_comments.id"), nullable=False),
)

readme_revisions = Table(
    "readme_revisions",
    metadata_obj,
    Column("id", UUID, primary_key=True),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("content", String(consts.LEN_README_PATCH_CONTENT_MAX), nullable=False),
    Column("is_public", Boolean, nullable=True, default=False),
    Column("reason", String(consts.LEN_README_PATCH_REASON_MAX), nullable=False),
)

Index(
    "ix_rfcs_listing_updated_at_id",
    rfcs.c.is_quarantined,
    rfcs.c.updated_at,
    rfcs.c.id,
)
Index(
    "ix_rfcs_listing_created_at_id",
    rfcs.c.is_quarantined,
    rfcs.c.created_at,
    rfcs.c.id,
)
Index("ix_rfcs_status", rfcs.c.status)
Index("ix_rfcs_created_by", rfcs.c.created_by)
Index("ix_rfcs_review_requested", rfcs.c.review_requested)
Index("ix_rfcs_is_public", rfcs.c.is_public)
Index(
    "ix_rfc_comments_listing_parent_created_at_id",
    rfc_comments.c.rfc_id,
    rfc_comments.c.parent_id,
    rfc_comments.c.is_quarantined,
    rfc_comments.c.created_at,
    rfc_comments.c.id,
)
Index("ix_rfc_comments_parent_id", rfc_comments.c.parent_id)
