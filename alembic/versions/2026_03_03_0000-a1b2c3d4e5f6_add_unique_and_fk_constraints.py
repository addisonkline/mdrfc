"""add unique and fk constraints

Revision ID: a1b2c3d4e5f6
Revises: 754f4d3232bb
Create Date: 2026-03-03 00:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "754f4d3232bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_users_username", "users", ["username"])
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_foreign_key(
        "fk_rfc_comments_parent_id",
        "rfc_comments",
        "rfc_comments",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_rfc_comments_parent_id", "rfc_comments", type_="foreignkey")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_constraint("uq_users_username", "users", type_="unique")
