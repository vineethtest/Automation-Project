"""Task 18 - Integrated mini project (ASYNC): end-to-end SauceDemo purchase.

Uses: pytest + pytest-playwright-asyncio fixtures, page objects, env-specific BASE_URL,
credentials from env vars, CSS / XPath / role / placeholder / text locators, expect() + pytest
assert, first/last/nth, dynamic waits, a custom wait condition and error/timeout handling.
Run on two browsers:  pytest tests/test_task18_mini_project.py --browser chromium --browser firefox
"""
import json
import re
from pathlib import Path

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import expect

from utils.wait_utils import ConditionTimeoutError, wait_until

DATA = json.loads((Path(__file__).resolve().parents[1] / "test_data" / "data.json").read_text())


@pytest.mark.smoke
@pytest.mark.regression
async def test_end_to_end_purchase(inventory_page):
    page = inventory_page.page

    # 1) sort by price (CSS locator) and verify with pytest assert
    await inventory_page.sort.select_option("lohi")
    prices = await inventory_page.item_prices()
    assert prices == sorted(prices)

    # 2) add first, nth and last item (collection handling; role locator)
    items = inventory_page.items
    chosen = [items.first, items.nth(2), items.last]
    expected_total = 0.0
    for item in chosen:
        price_text = await item.locator(".inventory_item_price").inner_text()
        expected_total += float(price_text.replace("$", ""))
        await item.get_by_role("button", name="Add to cart").click()

    # 3) custom wait condition for the dynamic cart badge
    async def badge_shows_three():
        return await inventory_page.cart_badge.inner_text() == "3"

    try:
        await wait_until(badge_shows_three, timeout_ms=5000, message="cart badge did not show 3 items")
    except ConditionTimeoutError as exc:
        pytest.fail(str(exc))
    await expect(inventory_page.cart_badge).to_have_text("3")

    # 4) cart page (CSS) and checkout form (placeholder + XPath locators)
    await inventory_page.cart_link.click()
    await expect(page).to_have_url(re.compile(r"/cart\.html$"))
    await expect(page.locator(".cart_item")).to_have_count(3)
    await page.get_by_role("button", name="Checkout").click()

    form = DATA["checkout"]
    await page.get_by_placeholder("First Name").fill(form["first_name"])
    await page.get_by_placeholder("Last Name").fill(form["last_name"])
    await page.get_by_placeholder("Zip/Postal Code").fill(form["postal_code"])
    await page.locator("xpath=//input[@data-test='continue']").click()

    # 5) overview: subtotal must match what we added (pytest assert on extracted value)
    await expect(page).to_have_url(re.compile(r"/checkout-step-two\.html$"))
    subtotal_text = await page.locator(".summary_subtotal_label").inner_text()
    assert float(subtotal_text.split("$")[1]) == pytest.approx(round(expected_total, 2))

    # 6) finish and confirm with visible-text locator
    await page.get_by_role("button", name="Finish").click()
    await expect(page.get_by_text("Thank you for your order!")).to_be_visible()
    await expect(page).to_have_url(re.compile(r"/checkout-complete\.html$"))


@pytest.mark.regression
async def test_timeout_is_handled_for_missing_element(inventory_page):
    """Error/timeout handling: a missing element produces a controlled outcome."""
    with pytest.raises(PlaywrightTimeoutError):
        await inventory_page.page.locator("#promo-popup").wait_for(state="visible", timeout=1000)
