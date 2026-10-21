"""Task 4 / Task 6 - Configuration layer.

Precedence (highest first):
  1. real process environment variables (e.g. DEFAULT_TIMEOUT_MS=2000 pytest ...)
  2. config/environments/<env>.env  (non-secret settings)
Secrets (SAUCE_USERNAME / SAUCE_PASSWORD) come from the local .env file or the
CI secret store and are NEVER stored in Settings.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import dotenv_values, load_dotenv

ROOT = Path(__file__).resolve().parent.parent
ENV_DIR = Path(__file__).resolve().parent / "environments"
VALID_ENVS = ("dev", "qa", "staging")


@dataclass(frozen=True)
class Settings:
    env: str
    base_url: str
    default_timeout_ms: int
    navigation_timeout_ms: int
    expect_timeout_ms: int
    headless: bool
    slow_mo_ms: int

    @property
    def origin(self) -> str:
        p = urlparse(self.base_url)
        return f"{p.scheme}://{p.netloc}"


def _to_bool(value: str) -> bool:
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _clean_url(url: str) -> str:
    if not url:
        raise ValueError("BASE_URL is not configured for this environment")
    return url if "?" in url else url.rstrip("/")


def get_settings(env: str | None = None) -> Settings:
    env = (env or os.environ.get("TEST_ENV") or "dev").lower()
    if env not in VALID_ENVS:
        raise ValueError(f"Unknown environment '{env}'. Use one of {VALID_ENVS}")

    # local secrets file -> os.environ (never overrides real env vars)
    load_dotenv(ROOT / ".env", override=False)
    file_values = dotenv_values(ENV_DIR / f"{env}.env")

    def get(key: str, default: str | None = None) -> str:
        return os.environ.get(key, file_values.get(key, default))

    return Settings(
        env=env,
        base_url=_clean_url(get("BASE_URL")),
        default_timeout_ms=int(get("DEFAULT_TIMEOUT_MS", "5000")),
        navigation_timeout_ms=int(get("NAVIGATION_TIMEOUT_MS", "30000")),
        expect_timeout_ms=int(get("EXPECT_TIMEOUT_MS", "5000")),
        headless=_to_bool(get("HEADLESS", "true")),
        slow_mo_ms=int(get("SLOW_MO_MS", "0")),
    )
