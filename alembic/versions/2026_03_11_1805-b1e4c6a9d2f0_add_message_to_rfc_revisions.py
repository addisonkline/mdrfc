"""add message to rfc revisions

Revision ID: b1e4c6a9d2f0
Revises: caa5021323c7
Create Date: 2026-03-11 18:05:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1e4c6a9d2f0"
down_revision: Union[str, None] = "caa5021323c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rfc_revisions",
        sa.Column(
            "message",
            sa.String(length=256),
            nullable=False,
            server_default="Initial revision",
        ),
    )
    op.alter_column("rfc_revisions", "message", server_default=None)


def downgrade() -> None:
    op.drop_column("rfc_revisions", "message")
