"""Task 6 - Environment files (ASYNC).
  pytest tests/test_task6_environments.py --env dev | qa | staging
Only non-secret values are printed.
"""
import re

import pytest
from playwright.async_api import expect

from config.settings import get_settings


@pytest.mark.smoke
async def test_selected_environment_url_is_used(page, settings):
    print(f"[env] running against {settings.env.upper()} -> {settings.base_url}")
    await page.goto(settings.base_url)
    await expect(page).to_have_url(re.compile(re.escape(settings.origin.split("://")[1])))
    await expect(page).to_have_title("Swag Labs")


def test_environments_have_different_urls():
    urls = {env: get_settings(env).base_url for env in ("dev", "qa", "staging")}
    assert len(set(urls.values())) == 3, f"each environment needs its own BASE_URL: {urls}"


def test_cli_env_option_matches_settings(settings, pytestconfig):
    cli = pytestconfig.getoption("--env")
    if cli:
        assert settings.env == cli.lower()
