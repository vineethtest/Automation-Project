"""Task 7 - Secrets management (ASYNC login test).

CI/CD: never store secrets in the repo. Use the platform's secret store (GitHub Actions
Secrets, GitLab masked variables, Jenkins Credentials, Azure Key Vault, HashiCorp Vault) and
expose them as environment variables at runtime. Restrict access, rotate, keep masked in logs.
"""
import re
from pathlib import Path

import pytest
from playwright.async_api import expect

from utils.secrets import mask

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".venv", "venv", ".git", ".idea", "__pycache__", ".pytest_cache"}


def _files(patterns):
    for pattern in patterns:
        for f in ROOT.rglob(pattern):
            if not (set(f.parts) & SKIP_DIRS) and f.name != ".env":
                yield f


@pytest.mark.smoke
async def test_login_with_credentials_from_environment(login_page, credentials):
    user, pwd = credentials
    await login_page.open()
    await login_page.login(user, pwd)
    await expect(login_page.page).to_have_url(re.compile(r"/inventory\.html$"))
    print(f"[secrets] logged in as {mask(user)} with password {mask(pwd)}")


def test_no_password_in_source_or_reports(credentials):
    _, pwd = credentials
    leaks = [str(f.relative_to(ROOT)) for f in _files(["*.py", "*.md", "*.ini", "*.txt", "*.example",
                                                       "*.html", "*.xml", "*.json"])
             if pwd in f.read_text(errors="ignore")]
    assert not leaks, f"password found in: {leaks}"


def test_env_is_gitignored_and_example_has_placeholders_only():
    ignore_lines = (ROOT / ".gitignore").read_text().splitlines()
    assert ".env" in [line.strip() for line in ignore_lines]
    example = (ROOT / ".env.example").read_text()
    assert "your_password_here" in example and "your_username_here" in example
