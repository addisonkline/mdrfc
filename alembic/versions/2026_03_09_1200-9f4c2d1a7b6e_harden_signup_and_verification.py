"""harden signup and add verification fields

Revision ID: 9f4c2d1a7b6e
Revises: d6e1433da3ba
Create Date: 2026-03-09 12:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f4c2d1a7b6e"
down_revision: Union[str, None] = "d6e1433da3ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_verified", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("verified_at", sa.DateTime(), nullable=True))
    op.add_column(
        "users",
        sa.Column("verification_token_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("verification_token_expires_at", sa.DateTime(), nullable=True),
    )

    op.execute("UPDATE users SET username = LOWER(username), email = LOWER(email)")
    op.execute(
        "UPDATE users SET is_verified = TRUE, verified_at = created_at WHERE is_verified IS NULL"
    )

    op.alter_column("users", "is_verified", nullable=False)
    op.create_index(
        "ix_users_username_lower_unique",
        "users",
        [sa.text("LOWER(username)")],
        unique=True,
    )
    op.create_index(
        "ix_users_email_lower_unique", "users", [sa.text("LOWER(email)")], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_users_email_lower_unique", table_name="users")
    op.drop_index("ix_users_username_lower_unique", table_name="users")
    op.drop_column("users", "verification_token_expires_at")
    op.drop_column("users", "verification_token_hash")
    op.drop_column("users", "verified_at")
    op.drop_column("users", "is_verified")
