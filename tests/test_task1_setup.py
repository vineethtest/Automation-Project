"""Task 1 - Installation & project setup (ASYNC): open a site and validate the title."""
import pytest
from playwright.async_api import Playwright, expect


@pytest.mark.smoke
async def test_open_website_and_validate_title(page, settings):
    await page.goto(settings.base_url)
    await expect(page).to_have_title("Swag Labs")
    assert await page.title() == "Swag Labs"


@pytest.mark.regression
async def test_launch_browser_manually(playwright: Playwright, settings):
    """Launch a browser explicitly (without the page fixture) to see the raw async API."""
    browser = await playwright.chromium.launch(headless=True)
    try:
        page = await browser.new_page()
        await page.goto(settings.base_url)
        await expect(page).to_have_title("Swag Labs")
    finally:
        await browser.close()
