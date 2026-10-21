"""Task 7 - helpers for secure credential handling."""
import os


def get_credentials():
    """Return (username, password) from environment variables, or None."""
    user = os.environ.get("SAUCE_USERNAME")
    pwd = os.environ.get("SAUCE_PASSWORD")
    if user and pwd:
        return user, pwd
    return None


def mask(value: str) -> str:
    """Never log secrets - use this when something must be displayed."""
    return "*" * 8 if value else ""
