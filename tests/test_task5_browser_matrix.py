"""Task 5 - Browser matrix (ASYNC). The SAME tests run on every browser:
  pytest tests/test_task5_browser_matrix.py --browser chromium
  pytest tests/test_task5_browser_matrix.py --browser firefox
  pytest tests/test_task5_browser_matrix.py --browser webkit
  pytest tests/test_task5_browser_matrix.py --browser chromium --browser firefox   # one execution
  python run_matrix.py                                                           # builds the table
"""
import re

import pytest
from playwright.async_api import expect

pytestmark = pytest.mark.matrix


@pytest.mark.smoke
async def test_login(login_page, credentials):
    await login_page.open()
    await login_page.login(*credentials)
    await expect(login_page.page).to_have_url(re.compile(r"/inventory\.html$"))
    await expect(login_page.page.locator(".app_logo")).to_have_text("Swag Labs")


async def test_search(inventory_page):
    """SauceDemo has no search box, so 'search' = find a product by name + sort."""
    matches = inventory_page.items.filter(has_text="Backpack")
    await expect(matches).to_have_count(1)
    await inventory_page.sort.select_option("za")
    names = await inventory_page.item_names()
    assert names == sorted(names, reverse=True)


async def test_navigation(inventory_page):
    page = inventory_page.page
    await inventory_page.names.first.click()
    await expect(page).to_have_url(re.compile(r"/inventory-item\.html"))
    await page.go_back()
    await expect(page).to_have_url(re.compile(r"/inventory\.html$"))


async def test_form_validation(login_page, browser_name):
    await login_page.open()
    await login_page.login_button.click()
    await expect(login_page.error).to_contain_text("Username is required")
    await login_page.username.fill("someone")
    await login_page.login_button.click()
    await expect(login_page.error).to_contain_text("Password is required")
    print(f"[matrix] form validation verified on {browser_name}")
