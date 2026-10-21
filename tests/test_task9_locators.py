"""Task 9 - Locator strategies (ASYNC).

Most maintainable: get_by_role() (and get_by_label/placeholder/test-id). They follow what users
and assistive tech see (role + accessible name), survive CSS/DOM refactors and read clearly.
CSS ids are fine when stable; XPath is the most brittle/verbose - use it last.
"""
import re

from playwright.async_api import expect


async def test_css_selector(page, settings):
    await page.goto(settings.base_url)
    await page.locator("#user-name").fill("css_user")                  # CSS (stable id)
    await expect(page.locator("#user-name")).to_have_value("css_user")


async def test_xpath_selector(page, settings):
    await page.goto(settings.base_url)
    field = page.locator("xpath=//input[@data-test='password']")       # XPath
    await field.fill("xpath_value")
    await expect(field).to_have_value("xpath_value")


async def test_get_by_role(page, settings):
    await page.goto(settings.base_url)
    await page.get_by_role("button", name="Login").click()             # role + accessible name
    await expect(page.locator('[data-test="error"]')).to_be_visible()


async def test_get_by_placeholder(page, settings):
    await page.goto(settings.base_url)
    box = page.get_by_placeholder("Username")                          # placeholder
    await box.fill("placeholder_user")
    await expect(box).to_have_value("placeholder_user")


async def test_get_by_label(page):
    await page.goto("https://the-internet.herokuapp.com/login")
    box = page.get_by_label("Username")                                # label
    await box.fill("label_user")
    await expect(box).to_have_value("label_user")


async def test_visible_text(inventory_page):
    page = inventory_page.page
    await page.get_by_text("Sauce Labs Backpack").first.click()        # visible text
    await expect(page).to_have_url(re.compile(r"/inventory-item\.html"))
    await expect(page.get_by_role("button", name="Add to cart")).to_be_visible()
