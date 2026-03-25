"""add comment_references table

Revision ID: a7b3c9d2e4f1
Revises: 8f9c4b5e2d1a
Create Date: 2026-03-25 12:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7b3c9d2e4f1"
down_revision: Union[str, None] = "8f9c4b5e2d1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "comment_references",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "comment_id",
            sa.Integer,
            sa.ForeignKey("rfc_comments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "rfc_id",
            sa.Integer,
            sa.ForeignKey("rfcs.id"),
            nullable=False,
        ),
        sa.Column("section_slug", sa.String(256), nullable=False),
        sa.Column("revision_id", sa.UUID, nullable=False),
    )
    op.create_index(
        "ix_comment_references_rfc_section",
        "comment_references",
        ["rfc_id", "section_slug"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_comment_references_rfc_section",
        table_name="comment_references",
    )
    op.drop_table("comment_references")
