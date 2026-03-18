import asyncio
from argparse import Namespace
import os
from pathlib import Path
import subprocess
import sys

import pytest

from mdrfc.setup import run_setup as setup_runner


def test_cli_module_imports_without_server_env(monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_root = repo_root / "src"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_root)
    for key in setup_runner.KNOWN_ENV_KEYS:
        env.pop(key, None)

    result = subprocess.run(
        [sys.executable, "-c", "import mdrfc.cli"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert result.stderr == ""


def test_validate_env_allows_debug_mode_without_email_settings() -> None:
    setup_runner._validate_env_values(
        {
            "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/mdrfc",
            "SECRET_KEY": "secret",
            "JWT_ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "AUTH_DEBUG_RETURN_VERIFICATION_TOKEN": "true",
        }
    )


def test_validate_env_requires_email_settings_when_debug_mode_disabled() -> None:
    with pytest.raises(setup_runner.SetupError) as excinfo:
        setup_runner._validate_env_values(
            {
                "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/mdrfc",
                "SECRET_KEY": "secret",
                "JWT_ALGORITHM": "HS256",
                "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
                "AUTH_DEBUG_RETURN_VERIFICATION_TOKEN": "false",
            }
        )

    assert "APP_BASE_URL" in str(excinfo.value)
    assert "EMAIL_FROM" in str(excinfo.value)
    assert "SMTP_HOST" in str(excinfo.value)


def test_ensure_dev_defaults_writes_missing_values(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    written = setup_runner._ensure_dev_defaults(env_path)
    contents = env_path.read_text(encoding="utf-8")

    assert written == [
        "SECRET_KEY",
        "JWT_ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "AUTH_DEBUG_RETURN_VERIFICATION_TOKEN",
    ]
    assert "JWT_ALGORITHM=HS256" in contents
    assert "ACCESS_TOKEN_EXPIRE_MINUTES=30" in contents
    assert "AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true" in contents
    assert "SECRET_KEY=" in contents


def test_run_setup_checks_db_and_runs_migrations(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    for key in setup_runner.KNOWN_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mdrfc",
                "SECRET_KEY=test-secret",
                "JWT_ALGORITHM=HS256",
                "ACCESS_TOKEN_EXPIRE_MINUTES=30",
                "AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    alembic_ini_path = tmp_path / "alembic.ini"
    alembic_ini_path.write_text(
        "[alembic]\nscript_location = alembic\n", encoding="utf-8"
    )

    calls: list[tuple[str, str]] = []

    async def fake_check_database_connectivity(database_url: str) -> None:
        calls.append(("db", database_url))

    def fake_apply_migrations(path: Path) -> None:
        calls.append(("migrations", str(path)))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        setup_runner, "_check_database_connectivity", fake_check_database_connectivity
    )
    monkeypatch.setattr(setup_runner, "_apply_migrations", fake_apply_migrations)

    asyncio.run(
        setup_runner.run_setup(
            Namespace(
                verbose=False,
                dev_defaults=False,
            )
        )
    )

    assert calls == [
        ("db", "postgresql://postgres:postgres@localhost:5432/mdrfc"),
        ("migrations", str(alembic_ini_path)),
    ]
