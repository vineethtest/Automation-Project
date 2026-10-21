from playwright.async_api import Page, expect


class LoginPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.username = page.get_by_placeholder("Username")
        self.password = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.error = page.locator('[data-test="error"]')

    async def open(self):
        await self.page.goto(self.base_url)
        await expect(self.page).to_have_title("Swag Labs")
        return self

    async def login(self, username: str, password: str):
        await self.username.fill(username)
        await self.password.fill(password)
        await self.login_button.click()
        return self
