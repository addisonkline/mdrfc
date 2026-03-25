"""add signup rate limit states

Revision ID: f2c7a1b9d4e6
Revises: a7b3c9d2e4f1
Create Date: 2026-03-25 16:45:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2c7a1b9d4e6"
down_revision: Union[str, None] = "a7b3c9d2e4f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "signup_rate_limit_states",
        sa.Column("scope", sa.String(length=32), primary_key=True),
        sa.Column("key_hash", sa.String(length=64), primary_key=True),
        sa.Column("attempt_timestamps", sa.ARRAY(sa.DateTime()), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_signup_rate_limit_states_expires_at",
        "signup_rate_limit_states",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_signup_rate_limit_states_expires_at",
        table_name="signup_rate_limit_states",
    )
    op.drop_table("signup_rate_limit_states")
