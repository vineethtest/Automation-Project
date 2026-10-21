"""Task 10 - Typing, filling and keyboard actions (ASYNC)."""
import re

from playwright.async_api import expect


async def test_fill_clear_replace_and_validate(page, settings):
    await page.goto(settings.base_url)
    user = page.get_by_placeholder("Username")
    await user.fill("first_value")
    await expect(user).to_have_value("first_value")
    await user.clear()
    await expect(user).to_have_value("")
    await user.fill("replacement")
    assert await user.input_value() == "replacement"


async def test_press_sequentially_and_keyboard_shortcut(page, settings):
    await page.goto(settings.base_url)
    user = page.get_by_placeholder("Username")
    await user.press_sequentially("typed_slowly")
    await expect(user).to_have_value("typed_slowly")
    await user.press("ControlOrMeta+A")        # keyboard shortcut: select all
    await user.press("Backspace")
    await expect(user).to_have_value("")


async def test_tab_moves_focus_and_enter_submits(page, settings, credentials):
    user, pwd = credentials
    await page.goto(settings.base_url)
    username = page.get_by_placeholder("Username")
    await username.fill(user)
    await username.press("Tab")
    await expect(page.get_by_placeholder("Password")).to_be_focused()
    await page.get_by_placeholder("Password").fill(pwd)
    await page.get_by_placeholder("Password").press("Enter")           # submit with keyboard
    await expect(page).to_have_url(re.compile(r"/inventory\.html$"))
