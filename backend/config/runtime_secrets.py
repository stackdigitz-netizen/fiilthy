"""Helpers for restart-stable local runtime secrets.

These fallbacks are only used when explicit environment variables are missing.
The generated values are persisted to a git-ignored file so local sessions and
encrypted key storage remain stable across backend restarts.
"""

import json
import os
import secrets
import warnings
from pathlib import Path
from typing import Callable


STORAGE_PATH = Path(__file__).resolve().parent / '.runtime_secrets.json'


def _read_runtime_secrets() -> dict[str, str]:
    if not STORAGE_PATH.exists():
        return {}

    try:
        with STORAGE_PATH.open('r', encoding='utf-8') as storage_file:
            stored = json.load(storage_file)
    except Exception:
        return {}

    return stored if isinstance(stored, dict) else {}


def _write_runtime_secrets(secrets_map: dict[str, str]) -> None:
    with STORAGE_PATH.open('w', encoding='utf-8') as storage_file:
        json.dump(secrets_map, storage_file, indent=2)


def get_runtime_secret(
    secret_name: str,
    *,
    warning_message: str,
    length: int = 48,
    generator: Callable[[], str] | None = None,
    validator: Callable[[str], bool] | None = None,
) -> str:
    env_value = os.environ.get(secret_name)
    if env_value:
        return env_value

    stored_secrets = _read_runtime_secrets()
    stored_value = stored_secrets.get(secret_name)
    if stored_value and (validator is None or validator(stored_value)):
        warnings.warn(f"{warning_message} Using persisted local fallback.")
        return stored_value

    if generator is None:
        generator = lambda: secrets.token_urlsafe(length)

    generated_value = generator()
    stored_secrets[secret_name] = generated_value
    _write_runtime_secrets(stored_secrets)
    warnings.warn(f"{warning_message} Generated and persisted a local fallback.")
    return generated_value