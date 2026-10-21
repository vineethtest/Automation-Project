"""Task 12 - expect() vs pytest assert (ASYNC).

Playwright `await expect(...)` AUTO-RETRIES until true or timeout, so it is right for anything
asynchronous in the UI (title, URL, visibility, text, state). A plain pytest assert evaluates
once, immediately - use it for already-extracted/computed Python values (sums, counts, order).
"""
import re

import pytest
from playwright.async_api import expect


@pytest.mark.regression
async def test_expect_assertions(login_page, credentials):
    await login_page.open()
    page = login_page.page
    await expect(page).to_have_title("Swag Labs")                        # title
    await expect(page).to_have_url(re.compile(r"saucedemo\.com"))        # URL
    await expect(login_page.login_button).to_be_visible()                # visibility
    await expect(login_page.login_button).to_be_enabled()                # enabled
    await login_page.username.fill("typed")
    await expect(login_page.username).to_have_value("typed")             # input value
    await login_page.login(*credentials)
    await expect(page.locator(".title")).to_have_text("Products")        # element text


async def test_disabled_then_enabled_state(page):
    await page.goto("https://the-internet.herokuapp.com/dynamic_controls")
    field = page.locator("#input-example input")
    await expect(field).to_be_disabled()
    await page.get_by_role("button", name="Enable").click()
    await expect(field).to_be_enabled()          # auto-waits for the async enable


async def test_pytest_assert_on_calculated_value(inventory_page):
    prices = await inventory_page.item_prices()
    total = round(sum(prices), 2)
    assert len(prices) == 6
    assert total == pytest.approx(129.94)
    assert min(prices) == 7.99
