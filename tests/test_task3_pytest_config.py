"""Task 3 - pytest configuration checks (no browser needed, so plain sync tests are fine).

  pytest -m smoke
  pytest tests/test_task3_pytest_config.py
  pytest tests/test_task3_pytest_config.py::test_markers_are_registered
"""
import pytest


@pytest.mark.smoke
def test_markers_are_registered(pytestconfig):
    markers = " ".join(pytestconfig.getini("markers"))
    for name in ("smoke", "regression"):
        assert name in markers, f"marker '{name}' missing from pytest.ini"


@pytest.mark.smoke
def test_test_directory_is_configured(pytestconfig):
    assert "tests" in pytestconfig.getini("testpaths")


@pytest.mark.regression
def test_default_cli_options_and_async_mode(pytestconfig):
    assert "--strict-markers" in pytestconfig.getini("addopts")
    assert pytestconfig.getini("asyncio_mode") == "auto"
