"""Task 15 - Built-in waits & load states (ASYNC, no sleep())."""
import re

from playwright.async_api import expect


async def test_auto_waiting_and_explicit_waits(page, settings, credentials):
    await page.goto(settings.base_url)
    await page.wait_for_load_state("domcontentloaded")

    login_btn = page.get_by_role("button", name="Login")
    await login_btn.wait_for(state="visible")            # explicit element wait
    await expect(login_btn).to_be_enabled()              # ready before interaction

    await page.get_by_placeholder("Username").fill(credentials[0])   # auto-waits for actionability
    await page.get_by_placeholder("Password").fill(credentials[1])
    await login_btn.click()

    await page.wait_for_url(re.compile(r"/inventory\.html$"))        # URL condition
    await page.wait_for_load_state("load")
    await page.locator(".inventory_list").wait_for(state="visible")
    await expect(page.locator(".inventory_item").first).to_be_visible()
