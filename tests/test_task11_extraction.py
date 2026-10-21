"""Task 11 - Extracting text and attributes (ASYNC)."""
from playwright.async_api import expect


async def test_extract_text_value_and_attributes(login_page, credentials):
    await login_page.open()
    page = login_page.page

    await login_page.username.fill("extract_me")
    value = await login_page.username.input_value()
    placeholder = await login_page.username.get_attribute("placeholder")
    input_class = await login_page.username.get_attribute("class")
    print(f"value={value!r} placeholder={placeholder!r} class={input_class!r}")
    assert value == "extract_me"
    assert placeholder == "Username"
    assert "input_error" in input_class

    await login_page.login(*credentials)

    heading = await page.locator(".app_logo").text_content()
    print(f"heading={heading!r}")
    assert heading == "Swag Labs"

    container_text = await page.locator(".inventory_list").inner_text()
    print(f"container text (first 80 chars): {container_text[:80]!r}")
    assert "Sauce Labs Backpack" in container_text

    twitter = page.locator('[data-test="social-twitter"]')
    href = await twitter.get_attribute("href")
    print(f"twitter href={href}")
    assert "saucelabs" in href
    await expect(twitter).to_have_attribute("target", "_blank")
