"""Shared ASYNC fixtures (Tasks 2, 4, 6, 7).

Uses pytest-playwright-asyncio (async twin of pytest-playwright) + pytest-asyncio.
Do NOT install pytest-playwright (sync) in the same virtual environment.

Fixture scope choices
---------------------
* settings            -> session : configuration is read once, immutable.
* browser (plugin)    -> session : launching a browser is expensive; one process is reused.
* context / page      -> function: every test gets a fresh isolated session (cookies, storage).
* event loop          -> session : required so the session-scoped browser and function-scoped
                                   fixtures/tests share one asyncio loop (see pytest.ini).
"""
import os

import pytest
import pytest_asyncio
from playwright.async_api import Browser, BrowserContext, Page, expect

from config.settings import Settings, get_settings
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.secrets import get_credentials


# ---------------------------------------------------------------- CLI options
def pytest_addoption(parser):
    parser.addoption("--env", action="store", default=None,
                     help="Target environment: dev | qa | staging (default: TEST_ENV or dev)")


def pytest_configure(config):
    env = config.getoption("--env")
    if env:
        os.environ["TEST_ENV"] = env.lower()


def pytest_report_header(config):
    s = get_settings()
    return (f"Environment: {s.env.upper()} | base_url: {s.base_url} | "
            f"timeout: {s.default_timeout_ms}ms | nav-timeout: {s.navigation_timeout_ms}ms | mode: ASYNC")


# ---------------------------------------------------------------- configuration (plain sync fixtures)
@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def base_url(settings):
    return settings.base_url


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, settings, pytestconfig):
    args = dict(browser_type_launch_args)
    args["headless"] = settings.headless and not pytestconfig.getoption("--headed")
    if settings.slow_mo_ms:
        args["slow_mo"] = settings.slow_mo_ms
    return args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, settings):
    return {**browser_context_args, "viewport": {"width": 1366, "height": 768}, "locale": "en-US"}


@pytest.fixture(scope="session", autouse=True)
def _expect_timeout(settings):
    if hasattr(expect, "set_options"):
        expect.set_options(timeout=settings.expect_timeout_ms)


@pytest.fixture(scope="session")
def credentials(settings):
    creds = get_credentials()
    if not creds:
        pytest.skip("SAUCE_USERNAME / SAUCE_PASSWORD not set. Copy .env.example to .env and fill it in.")
    return creds


# ---------------------------------------------------------------- async fixtures
@pytest_asyncio.fixture
async def context(context: BrowserContext, settings) -> BrowserContext:
    """Wraps the plugin's async context fixture to apply default + navigation timeouts."""
    context.set_default_timeout(settings.default_timeout_ms)
    context.set_default_navigation_timeout(settings.navigation_timeout_ms)
    return context


@pytest_asyncio.fixture
async def custom_context(browser: Browser, browser_context_args, settings):
    """Task 2: custom fixture creating a brand-new BrowserContext (function scope = isolated)."""
    ctx = await browser.new_context(**browser_context_args)
    ctx.set_default_timeout(settings.default_timeout_ms)
    ctx.set_default_navigation_timeout(settings.navigation_timeout_ms)
    yield ctx
    await ctx.close()


@pytest_asyncio.fixture
async def custom_page(custom_context: BrowserContext) -> Page:
    """Task 2: a page created from the custom context."""
    return await custom_context.new_page()


@pytest.fixture
def login_page(page: Page, settings) -> LoginPage:
    return LoginPage(page, settings.base_url)


@pytest_asyncio.fixture
async def inventory_page(login_page: LoginPage, credentials) -> InventoryPage:
    await login_page.open()
    await login_page.login(*credentials)
    return await InventoryPage(login_page.page).expect_loaded()
