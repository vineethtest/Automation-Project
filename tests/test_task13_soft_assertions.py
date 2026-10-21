"""Task 13 - Soft assertions (ASYNC).

Hard assertion : raises immediately -> the rest of the test is skipped.
Soft assertion : failure is recorded, test continues; all failures reported at the end.
Use soft checks for independent UI properties (validating a whole page) where seeing every
defect at once helps; keep hard asserts for preconditions (e.g. 'am I logged in?').
"""
import pytest
from playwright.async_api import expect

from utils.soft_assert import SoftAssert


@pytest.mark.regression
async def test_soft_assertions_all_pass(login_page):
    await login_page.open()
    page = login_page.page
    soft = SoftAssert()
    await soft.check("title", lambda: expect(page).to_have_title("Swag Labs"))
    await soft.check("username visible", lambda: expect(login_page.username).to_be_visible())
    await soft.check("password visible", lambda: expect(login_page.password).to_be_visible())
    await soft.check("login enabled", lambda: expect(login_page.login_button).to_be_enabled())
    soft.assert_all()


async def test_one_failure_does_not_stop_the_rest(login_page):
    await login_page.open()
    page = login_page.page
    soft = SoftAssert()
    await soft.check("title", lambda: expect(page).to_have_title("Swag Labs"))
    await soft.check("WRONG placeholder (expected failure)",
                     lambda: expect(login_page.username).to_have_attribute("placeholder", "Email", timeout=1000))
    await soft.check("password visible (runs AFTER the failure)", lambda: expect(login_page.password).to_be_visible())
    await soft.check("login enabled (runs AFTER the failure)", lambda: expect(login_page.login_button).to_be_enabled())

    assert len(soft.passed) == 3          # remaining checks still executed
    assert len(soft.failures) == 1
    with pytest.raises(AssertionError, match="1 soft assertion"):
        soft.assert_all()                 # failures reported together at the end
