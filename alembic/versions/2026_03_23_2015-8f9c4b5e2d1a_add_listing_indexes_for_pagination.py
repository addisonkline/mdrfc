"""add listing indexes for pagination

Revision ID: 8f9c4b5e2d1a
Revises: 67d3110610bf
Create Date: 2026-03-23 20:15:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8f9c4b5e2d1a"
down_revision: Union[str, None] = "67d3110610bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_rfcs_listing_updated_at_id",
        "rfcs",
        ["is_quarantined", "updated_at", "id"],
        unique=False,
    )
    op.create_index(
        "ix_rfcs_listing_created_at_id",
        "rfcs",
        ["is_quarantined", "created_at", "id"],
        unique=False,
    )
    op.create_index("ix_rfcs_status", "rfcs", ["status"], unique=False)
    op.create_index("ix_rfcs_created_by", "rfcs", ["created_by"], unique=False)
    op.create_index(
        "ix_rfcs_review_requested",
        "rfcs",
        ["review_requested"],
        unique=False,
    )
    op.create_index("ix_rfcs_is_public", "rfcs", ["is_public"], unique=False)
    op.create_index(
        "ix_rfc_comments_listing_parent_created_at_id",
        "rfc_comments",
        ["rfc_id", "parent_id", "is_quarantined", "created_at", "id"],
        unique=False,
    )
    op.create_index(
        "ix_rfc_comments_parent_id",
        "rfc_comments",
        ["parent_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_rfc_comments_parent_id", table_name="rfc_comments")
    op.drop_index(
        "ix_rfc_comments_listing_parent_created_at_id",
        table_name="rfc_comments",
    )
    op.drop_index("ix_rfcs_is_public", table_name="rfcs")
    op.drop_index("ix_rfcs_review_requested", table_name="rfcs")
    op.drop_index("ix_rfcs_created_by", table_name="rfcs")
    op.drop_index("ix_rfcs_status", table_name="rfcs")
    op.drop_index("ix_rfcs_listing_created_at_id", table_name="rfcs")
    op.drop_index("ix_rfcs_listing_updated_at_id", table_name="rfcs")
