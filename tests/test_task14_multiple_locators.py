"""Task 14 - Multiple locators / collections (ASYNC)."""
import json
from pathlib import Path

from playwright.async_api import expect

DATA = json.loads((Path(__file__).resolve().parents[1] / "test_data" / "data.json").read_text())


async def test_collections_first_last_nth_and_loop(inventory_page):
    items = inventory_page.items
    count = await items.count()
    print(f"matching items: {count}")
    await expect(items).to_have_count(DATA["expected_product_count"])

    first, last, third = items.first, items.last, items.nth(2)
    print("first:", await first.locator(".inventory_item_name").inner_text())
    print("last :", await last.locator(".inventory_item_name").inner_text())
    print("nth(2):", await third.locator(".inventory_item_name").inner_text())
    assert await first.locator(".inventory_item_name").inner_text() == DATA["first_product"]

    await first.get_by_role("button", name="Add to cart").click()     # interact with first
    await last.get_by_role("button", name="Add to cart").click()      # interact with last
    await third.get_by_role("button", name="Add to cart").click()     # interact with nth
    await expect(inventory_page.cart_badge).to_have_text("3")

    for i in range(count):                                            # loop through all
        print(f"{i + 1}. {await items.nth(i).locator('.inventory_item_name').inner_text()}")
    assert len(await inventory_page.item_names()) == count
