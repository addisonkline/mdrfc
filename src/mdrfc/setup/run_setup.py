from argparse import Namespace
from collections.abc import Mapping
from sys import exit
import asyncio
import os
from pathlib import Path
import secrets

from alembic import command
from alembic.config import Config
import asyncpg # type: ignore
from dotenv import dotenv_values, load_dotenv


LOCAL_DEV_DEFAULTS = {
    "SECRET_KEY": lambda: secrets.token_hex(32),
    "JWT_ALGORITHM": lambda: "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": lambda: "30",
    "AUTH_DEBUG_RETURN_VERIFICATION_TOKEN": lambda: "true",
}

REQUIRED_ENV_KEYS = (
    "DATABASE_URL",
    "SECRET_KEY",
    "JWT_ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
)

KNOWN_ENV_KEYS = REQUIRED_ENV_KEYS + (
    "APP_BASE_URL",
    "EMAIL_FROM",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_STARTTLS",
    "SMTP_USE_SSL",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "REQUIRED_EMAIL_SUFFIX",
    "RESEND_API_KEY",
    "EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES",
    "AUTH_DEBUG_RETURN_VERIFICATION_TOKEN",
)


class SetupError(RuntimeError):
    """
    User-facing setup failure.
    """


def _log(message: str, *, verbose: bool = True) -> None:
    if verbose:
        print(message)


def _read_env_file(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        return {}

    raw_values = dotenv_values(env_path)
    return {
        key: value
        for key, value in raw_values.items()
        if value is not None
    }


def _load_effective_env(env_path: Path) -> dict[str, str]:
    file_values = _read_env_file(env_path)
    effective_env: dict[str, str] = {}
    for key in KNOWN_ENV_KEYS:
        if key in os.environ:
            effective_env[key] = os.environ[key]
        elif key in file_values:
            effective_env[key] = file_values[key]
    return effective_env


def _apply_env_to_process(env_values: Mapping[str, str]) -> None:
    for key, value in env_values.items():
        os.environ[key] = value


def _parse_bool(name: str, value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise SetupError(f"{name} must be a boolean value")


def _require_int(name: str, value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise SetupError(f"{name} must be an integer") from exc

    if parsed <= 0:
        raise SetupError(f"{name} must be greater than zero")
    return parsed


def _validate_env_values(env_values: Mapping[str, str]) -> None:
    missing = [
        key
        for key in REQUIRED_ENV_KEYS
        if not env_values.get(key, "").strip()
    ]

    debug_mode_value = env_values.get("AUTH_DEBUG_RETURN_VERIFICATION_TOKEN", "false")
    debug_mode = _parse_bool("AUTH_DEBUG_RETURN_VERIFICATION_TOKEN", debug_mode_value)

    if not debug_mode:
        for key in ("APP_BASE_URL", "EMAIL_FROM", "SMTP_HOST"):
            if not env_values.get(key, "").strip():
                missing.append(key)

    if missing:
        missing_str = ", ".join(sorted(set(missing)))
        raise SetupError(f"missing required environment values: {missing_str}")

    _require_int("ACCESS_TOKEN_EXPIRE_MINUTES", env_values["ACCESS_TOKEN_EXPIRE_MINUTES"])

    if "SMTP_PORT" in env_values and env_values["SMTP_PORT"].strip():
        _require_int("SMTP_PORT", env_values["SMTP_PORT"])

    if "EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES" in env_values and env_values["EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES"].strip():
        _require_int(
            "EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES",
            env_values["EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES"],
        )

    for bool_key in ("SMTP_STARTTLS", "SMTP_USE_SSL"):
        if bool_key in env_values and env_values[bool_key].strip():
            _parse_bool(bool_key, env_values[bool_key])


def _ensure_dev_defaults(env_path: Path) -> list[str]:
    existing_values = _read_env_file(env_path)
    missing_defaults = [
        key
        for key in LOCAL_DEV_DEFAULTS
        if not existing_values.get(key, "").strip()
    ]

    if not missing_defaults:
        return []

    lines_to_append: list[str] = []
    if env_path.exists():
        existing_text = env_path.read_text(encoding="utf-8")
        if existing_text and not existing_text.endswith("\n"):
            lines_to_append.append("")
        lines_to_append.append("")
        lines_to_append.append("# Added by `mdrfc setup --dev-defaults`")
    else:
        lines_to_append.append("# Local development defaults for MDRFC")

    for key in missing_defaults:
        lines_to_append.append(f"{key}={LOCAL_DEV_DEFAULTS[key]()}")

    rendered = "\n".join(lines_to_append) + "\n"
    with env_path.open("a", encoding="utf-8") as env_file:
        env_file.write(rendered)

    return missing_defaults


async def _check_database_connectivity(database_url: str) -> None:
    connection = None
    try:
        connection = await asyncpg.connect(dsn=database_url)
    except Exception as exc:
        raise SetupError(f"database connectivity check failed: {exc}") from exc
    finally:
        if connection is not None:
            await connection.close()


def _apply_migrations(alembic_ini_path: Path) -> None:
    if not alembic_ini_path.exists():
        raise SetupError(f"Alembic config not found at {alembic_ini_path}")

    try:
        config = Config(str(alembic_ini_path))
        command.upgrade(config, "head")
    except Exception as exc:
        raise SetupError(f"failed to apply Alembic migrations: {exc}") from exc


async def run_setup(args: Namespace) -> None:
    verbose = bool(getattr(args, "verbose", False))
    write_dev_defaults = bool(getattr(args, "dev_defaults", False))
    project_root = Path.cwd()
    env_path = project_root / ".env"
    alembic_ini_path = project_root / "alembic.ini"

    _log("Starting MDRFC setup", verbose=True)

    if write_dev_defaults:
        written_defaults = _ensure_dev_defaults(env_path)
        if written_defaults:
            _log(
                "Wrote local development defaults for: "
                + ", ".join(written_defaults),
                verbose=True,
            )
        else:
            _log("Local development defaults already present", verbose=verbose)

    if not env_path.exists():
        raise SetupError(
            ".env was not found in the current directory; create it first or rerun with --dev-defaults"
        )

    _log(f"Loading environment from {env_path}", verbose=verbose)
    load_dotenv(dotenv_path=env_path, override=False)
    env_values = _load_effective_env(env_path)

    _log("Validating environment configuration", verbose=True)
    _validate_env_values(env_values)
    _apply_env_to_process(env_values)

    _log("Checking database connectivity", verbose=True)
    await _check_database_connectivity(env_values["DATABASE_URL"])

    _log("Applying Alembic migrations", verbose=True)
    _apply_migrations(alembic_ini_path)

    _log("Setup complete", verbose=True)


def run_setup_sync(
    args: Namespace,
) -> None:
    """
    Run the async setup process (postgres, etc) using asyncio.
    """
    try:
        asyncio.run(run_setup(args))
    except SetupError as exc:
        print(f"setup failed: {exc}")
        exit(1)
