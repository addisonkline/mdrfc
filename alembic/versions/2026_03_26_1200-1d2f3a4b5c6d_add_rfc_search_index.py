"""add rfc search index

Revision ID: 1d2f3a4b5c6d
Revises: f2c7a1b9d4e6
Create Date: 2026-03-26 12:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1d2f3a4b5c6d"
down_revision: Union[str, None] = "f2c7a1b9d4e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_rfcs_search_vector",
        "rfcs",
        [
            sa.text(
                """
                (
                    setweight(to_tsvector('simple', coalesce(title, '')), 'A') ||
                    setweight(to_tsvector('simple', coalesce(slug, '')), 'A') ||
                    setweight(to_tsvector('simple', coalesce(summary, '')), 'B') ||
                    setweight(to_tsvector('simple', coalesce(content, '')), 'C')
                )
                """
            )
        ],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_rfcs_search_vector", table_name="rfcs")
