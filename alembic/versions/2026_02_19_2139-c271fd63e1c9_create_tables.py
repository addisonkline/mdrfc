"""create tables

Revision ID: c271fd63e1c9
Revises:
Create Date: 2026-02-19 21:39:45.982228+00:00

"""

import os
from typing import Sequence, Union

from dotenv import load_dotenv
from sqlalchemy import create_engine

from mdrfc.backend.db import metadata_obj

# revision identifiers, used by Alembic.
revision: str = "c271fd63e1c9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Build the initial tables
    """
    load_dotenv()

    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL is None:
        raise ValueError("env var DATABASE_URL not detected")

    engine = create_engine(DATABASE_URL)
    metadata_obj.create_all(engine)


def downgrade() -> None:
    pass
