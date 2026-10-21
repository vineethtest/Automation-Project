"""Task 2 - Browser, Context and Page fixtures (ASYNC).

Browser  : one real browser process. Expensive -> session scope.
Context  : isolated "incognito-like" profile inside a browser (own cookies/storage). Cheap ->
           function scope so every test is isolated.
Page     : a single tab inside a context.
Hierarchy: Browser -> BrowserContext -> Page
"""
import pytest
from playwright.async_api import expect

KEY = "student_session_token"


@pytest.mark.smoke
async def test_navigate_with_plugin_page_fixture(page, settings):
    await page.goto(settings.base_url)
    await expect(page).to_have_title("Swag Labs")


async def test_custom_context_and_page_fixture(custom_page, custom_context, settings):
    await custom_page.goto(settings.base_url)
    await expect(custom_page).to_have_title("Swag Labs")
    assert custom_page in custom_context.pages


# --- Two tests proving isolation (run in this order, same browser) -------------
async def test_isolation_a_writes_state(custom_page, custom_context, settings):
    await custom_page.goto(settings.base_url)
    await custom_page.evaluate(f"localStorage.setItem('{KEY}', 'abc123')")
    await custom_context.add_cookies([{"name": "demo_cookie", "value": "1", "url": settings.origin}])
    assert await custom_page.evaluate(f"localStorage.getItem('{KEY}')") == "abc123"


async def test_isolation_b_sees_clean_state(custom_page, custom_context, settings):
    await custom_page.goto(settings.base_url)
    assert await custom_page.evaluate(f"localStorage.getItem('{KEY}')") is None
    assert [c for c in await custom_context.cookies() if c["name"] == "demo_cookie"] == []


@pytest.mark.regression
async def test_two_contexts_in_one_test_are_isolated(browser, settings):
    ctx1, ctx2 = await browser.new_context(), await browser.new_context()
    try:
        p1, p2 = await ctx1.new_page(), await ctx2.new_page()
        for p in (p1, p2):
            await p.goto(settings.base_url)
        await p1.evaluate(f"localStorage.setItem('{KEY}', 'only-in-context-1')")
        assert await p1.evaluate(f"localStorage.getItem('{KEY}')") == "only-in-context-1"
        assert await p2.evaluate(f"localStorage.getItem('{KEY}')") is None
    finally:
        await ctx1.close()
        await ctx2.close()
