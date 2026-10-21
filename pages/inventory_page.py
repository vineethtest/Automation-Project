import re

from playwright.async_api import Page, expect


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        self.items = page.locator(".inventory_item")
        self.names = page.locator(".inventory_item_name")
        self.prices = page.locator(".inventory_item_price")
        self.add_buttons = page.get_by_role("button", name="Add to cart")
        self.cart_badge = page.locator(".shopping_cart_badge")
        self.cart_link = page.locator(".shopping_cart_link")
        self.sort = page.locator('[data-test="product-sort-container"]')

    async def expect_loaded(self):
        await expect(self.page).to_have_url(re.compile(r"/inventory\.html$"))
        await expect(self.items.first).to_be_visible()
        return self

    async def item_names(self) -> list[str]:
        return await self.names.all_inner_texts()

    async def item_prices(self) -> list[float]:
        return [float(t.replace("$", "")) for t in await self.prices.all_inner_texts()]
