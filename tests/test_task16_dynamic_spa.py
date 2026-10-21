"""Task 16 - Dynamic waits for SPA / dynamic content (ASYNC).

Why wait on a condition instead of sleep(): a fixed delay is either too short (flaky) or too
long (slow suite). Waiting for "indicator hidden / text changed / URL changed" continues the
instant the app is ready and fails fast with a clear message if it never is.
"""
import re

import pytest
from playwright.async_api import expect

pytestmark = pytest.mark.dynamic


async def test_loading_indicator_disappears_then_content_appears(page):
    await page.goto("https://the-internet.herokuapp.com/dynamic_loading/2")
    await page.get_by_role("button", name="Start").click()            # triggers the dynamic update
    await expect(page.locator("#loading")).to_be_visible()
    await expect(page.locator("#loading")).to_be_hidden(timeout=15000)   # wait for indicator to go
    await expect(page.locator("#finish h4")).to_have_text("Hello World!")


async def test_spa_state_and_url_change(page):
    await page.goto("https://demo.playwright.dev/todomvc")            # React SPA
    new_todo = page.get_by_placeholder("What needs to be done?")
    for text in ("write tests", "run tests", "fix tests"):
        await new_todo.fill(text)
        await new_todo.press("Enter")
    await expect(page.locator(".todo-count")).to_contain_text("3 items left")

    await page.locator(".todo-list li").first.get_by_role("checkbox").check()
    await expect(page.locator(".todo-count")).to_contain_text("2 items left")   # text changes

    await page.get_by_role("link", name="Active").click()
    await page.wait_for_url(re.compile(r"#/active$"))                           # URL/state change
    await expect(page.locator(".todo-list li")).to_have_count(2)
