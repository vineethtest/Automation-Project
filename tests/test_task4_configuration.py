"""Task 4 - Configuration layer (ASYNC).
  pytest tests/test_task4_configuration.py -k timeout_follows
  DEFAULT_TIMEOUT_MS=1500 pytest tests/test_task4_configuration.py -k timeout_follows
"""
import time

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from config.settings import get_settings


@pytest.mark.smoke
def test_settings_are_read_from_config(settings):
    assert settings.base_url.startswith("http")
    assert settings.default_timeout_ms > 0
    assert settings.navigation_timeout_ms >= settings.default_timeout_ms
    print(f"[config] env={settings.env} timeout={settings.default_timeout_ms}ms "
          f"nav={settings.navigation_timeout_ms}ms headless={settings.headless}")


def test_environment_variable_overrides_file(monkeypatch):
    monkeypatch.setenv("DEFAULT_TIMEOUT_MS", "1234")
    assert get_settings().default_timeout_ms == 1234


@pytest.mark.slow
async def test_default_timeout_follows_config(page, settings):
    """Clicking a missing element must fail after ~default_timeout_ms (from config)."""
    await page.goto(settings.base_url)
    started = time.monotonic()
    with pytest.raises(PlaywrightTimeoutError):
        await page.locator("#element-that-does-not-exist").click()
    elapsed = time.monotonic() - started
    expected = settings.default_timeout_ms / 1000
    assert expected * 0.8 <= elapsed <= expected + 5, f"elapsed {elapsed:.1f}s vs configured {expected}s"
