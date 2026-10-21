"""Task 8 - Core navigation & web automation (ASYNC, SauceDemo)."""
import re

import pytest
from playwright.async_api import expect


@pytest.mark.smoke
async def test_login_and_browser_navigation(page, settings, credentials):
    user, pwd = credentials
    await page.goto(settings.base_url)
    await expect(page).to_have_url(re.compile(r"saucedemo\.com"))
    await expect(page).to_have_title("Swag Labs")

    await page.get_by_placeholder("Username").fill(user)
    await page.get_by_placeholder("Password").fill(pwd)
    await page.get_by_role("button", name="Login").click()

    await expect(page).to_have_url(re.compile(r"/inventory\.html$"))
    await expect(page.locator(".inventory_list")).to_be_visible()

    await page.locator(".inventory_item_name").first.click()
    await expect(page).to_have_url(re.compile(r"/inventory-item\.html\?id="))
    await expect(page.locator(".inventory_details_name")).to_be_visible()

    await page.go_back()
    await expect(page).to_have_url(re.compile(r"/inventory\.html$"))

    await page.go_forward()
    await expect(page).to_have_url(re.compile(r"/inventory-item\.html"))

    await page.reload()
    await expect(page).to_have_url(re.compile(r"/inventory-item\.html"))
    await expect(page.locator(".inventory_details_name")).to_be_visible()
