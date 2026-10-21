"""Task 17 - Timeout handling & custom wait conditions (ASYNC).
Do NOT 'fix' timeouts by raising them to huge values: find the real condition to wait for.
"""
import time

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from utils.wait_utils import ConditionTimeoutError, wait_until

pytestmark = pytest.mark.slow


async def test_missing_element_times_out_quickly(page, settings):
    await page.goto(settings.base_url)
    started = time.monotonic()
    with pytest.raises(PlaywrightTimeoutError):
        await page.locator("#no-such-element").wait_for(state="visible", timeout=1500)
    assert time.monotonic() - started < 5


async def test_handle_timeout_gracefully(page, settings):
    """Test design: an optional element - absence is a valid outcome, not a crash."""
    await page.goto(settings.base_url)
    try:
        await page.locator("#optional-banner").wait_for(state="visible", timeout=1000)
        banner_shown = True
    except PlaywrightTimeoutError:
        banner_shown = False
    assert banner_shown is False


async def test_custom_wait_condition_succeeds_when_state_reached(page):
    await page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    await page.get_by_role("button", name="Start").click()
    await wait_until(lambda: page.locator("#finish").is_visible(),
                     timeout_ms=15000, poll_ms=250,
                     message="'Hello World!' did not appear after clicking Start")
    assert await page.locator("#finish h4").inner_text() == "Hello World!"


async def test_custom_wait_condition_fails_with_useful_message(page, settings):
    await page.goto(settings.base_url)

    async def badge_is_five():
        return await page.locator(".shopping_cart_badge").count() == 5

    with pytest.raises(ConditionTimeoutError, match="cart badge never reached 5"):
        await wait_until(badge_is_five, timeout_ms=1000, poll_ms=200,
                         message="cart badge never reached 5")
