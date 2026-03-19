from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


REPO_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI_PATH = REPO_ROOT / "alembic.ini"


def _get_current_head_revision() -> str:
    config = Config(str(ALEMBIC_INI_PATH))
    config.set_main_option("script_location", str(REPO_ROOT / "alembic"))
    return ScriptDirectory.from_config(config).get_current_head()


async def _fetch_migration_state(pool):
    async with pool.acquire() as connection:
        version = await connection.fetchval("SELECT version_num FROM alembic_version")
        rows = await connection.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
    return version, {row["tablename"] for row in rows}


def test_fresh_database_upgrades_to_current_head(
    isolated_postgres_db: dict[str, object],
) -> None:
    run = isolated_postgres_db["run"]
    pool = isolated_postgres_db["pool"]

    version, tables = run(_fetch_migration_state(pool))

    assert version == _get_current_head_revision()
    assert {
        "alembic_version",
        "users",
        "rfcs",
        "rfc_comments",
        "rfc_revisions",
        "quarantined_rfcs",
        "quarantined_comments",
    } <= tables
