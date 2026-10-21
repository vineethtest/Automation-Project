# Playwright Python – Assignment 2 (ASYNC version)
Pytest framework, configuration, browser matrix, locators, assertions & waits.
Trainer: Ashwini K | Nexus Software Services

Practice site: https://www.saucedemo.com/ (plus the-internet.herokuapp.com and demo.playwright.dev/todomvc for dynamic/SPA tasks). Style: **async API** (`playwright.async_api`, `async def` tests, `await`) used consistently everywhere.

## 0. Async stack - read first
* Plugin: **pytest-playwright-asyncio** (async twin of pytest-playwright) + **pytest-asyncio**.
* **Do not install `pytest-playwright` (sync) in the same virtual environment** - the two plugins clash. Use a NEW `.venv` for this project.
* `pytest.ini` sets `asyncio_mode = auto` and a session-wide event loop (`asyncio_default_*_loop_scope = session`) so the session-scoped `browser` and the function-scoped `context/page` share one loop. Tests are plain `async def` - no decorator needed.
* Async helpers: `utils/wait_utils.py` (`await wait_until(...)`) and `utils/soft_assert.py` (`await soft.check(...)`).
* Custom fixtures are named `custom_context` / `custom_page` (NOT `new_context`, which the plugin already owns).

## 1. Setup (Task 1)
```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate        macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
playwright install            # chromium, firefox, webkit
cp .env.example .env          # Windows: copy .env.example .env   -> then fill in credentials
```
SauceDemo's public demo login is shown on https://www.saucedemo.com/ – put those values in your local `.env` (never in code).

**PyCharm:** File → Open this folder → Settings → Python Interpreter → select `.venv` → Tools → Python Integrated Tools → Default test runner = *pytest*.

## 2. Project structure
```
tests/        test cases (one file per task: test_task1_... test_task18_...)
pages/        Page Object classes (LoginPage, InventoryPage)
utils/        soft_assert.py, wait_utils.py (custom wait), secrets.py
config/       settings.py + environments/{dev,qa,staging}.env (non-secret)
test_data/    data.json (non-sensitive)
conftest.py   fixtures: settings, base_url, context, new_context, custom_page, credentials ...
pytest.ini    pytest configuration
run_matrix.py runs matrix tests on 3 browsers and writes reports/browser_matrix.md
.env.example  placeholders only    .gitignore  ignores .env, .venv, reports
```

## 3. Task → file map
| Task | File |
|---|---|
| 1 Setup | tests/test_task1_setup.py, requirements.txt |
| 2 Browser/Context/Page | tests/test_task2_fixtures.py, conftest.py |
| 3 pytest config | pytest.ini, tests/test_task3_pytest_config.py |
| 4 Config layer | config/settings.py, tests/test_task4_configuration.py |
| 5 Browser matrix | tests/test_task5_browser_matrix.py, run_matrix.py |
| 6 Environments | config/environments/*.env, tests/test_task6_environments.py |
| 7 Secrets | .env.example, .gitignore, utils/secrets.py, tests/test_task7_secrets.py |
| 8 Navigation | tests/test_task8_navigation.py |
| 9 Locators | tests/test_task9_locators.py |
| 10 Keyboard | tests/test_task10_keyboard.py |
| 11 Extraction | tests/test_task11_extraction.py |
| 12 Assertions | tests/test_task12_assertions.py |
| 13 Soft assertions | utils/soft_assert.py, tests/test_task13_soft_assertions.py |
| 14 Multiple locators | tests/test_task14_multiple_locators.py |
| 15 Built-in waits | tests/test_task15_builtin_waits.py |
| 16 Dynamic/SPA waits | tests/test_task16_dynamic_spa.py |
| 17 Timeouts/custom waits | utils/wait_utils.py, tests/test_task17_timeouts.py |
| 18 Mini project | tests/test_task18_mini_project.py, pages/ |

## 4. Running tests
```bash
pytest                                              # everything (uses pytest.ini defaults)
pytest -m smoke                                     # only smoke tests
pytest -m "regression and not slow"
pytest tests/test_task9_locators.py                 # one file
pytest tests/test_task9_locators.py::test_get_by_role   # one function
pytest --headed                                     # visible browser
pytest --browser firefox                            # one browser
pytest --browser chromium --browser firefox         # several browsers in one run
pytest --env qa                                     # choose environment (dev | qa | staging)
DEFAULT_TIMEOUT_MS=1500 pytest tests/test_task4_configuration.py -k timeout_follows   # config changes behaviour
python run_matrix.py                                # Task 5 matrix table
```
(PowerShell for env vars: `$env:DEFAULT_TIMEOUT_MS=1500; pytest ...`)

### pytest.ini options
| Option | Meaning |
|---|---|
| `testpaths = tests` | default test directory |
| `pythonpath = .` | lets tests import `config`, `pages`, `utils` |
| `asyncio_mode = auto` | pytest-asyncio runs every `async def` test/fixture |
| `asyncio_default_fixture_loop_scope / test_loop_scope = session` | one event loop for the whole session |
| `-ra -v` | short summary of non-passing tests, verbose names |
| `--strict-markers` | unregistered markers are errors |
| `--screenshot only-on-failure` | pytest-playwright screenshot on failure |
| `--tracing retain-on-failure` | keep Playwright trace on failure |
| `--output reports/artifacts` | artifacts folder |
| `--html=reports/report.html --self-contained-html` | HTML execution report |
| markers `smoke`, `regression`, `matrix`, `dynamic`, `slow` | test selection with `-m` |
| custom `--env` (conftest.py) | selects environment file |

## 5. Configuration (Tasks 4 & 6)
`config/settings.py` loads `config/environments/<env>.env` (BASE_URL, DEFAULT_TIMEOUT_MS, NAVIGATION_TIMEOUT_MS, EXPECT_TIMEOUT_MS, HEADLESS, SLOW_MO_MS). Real environment variables override file values. Fixtures in `conftest.py` apply default timeout (5 s), navigation timeout (30 s) and headless mode, so changing config never requires editing tests. The selected environment/base URL is printed in the pytest header; secrets are never printed.

## 6. Concepts (explanations required by the tasks)
* **Browser vs Context vs Page** – Browser = the browser process; BrowserContext = isolated profile (cookies, storage) inside it; Page = one tab in a context. *Scope choice:* browser is session-scoped (slow to launch), context/page are function-scoped so each test is isolated (see `test_isolation_a/b`).
* **Most maintainable locator** – `get_by_role()` (with `get_by_label/placeholder/test-id`): based on user-visible semantics, not DOM structure or dynamic CSS classes. XPath/CSS chains are most brittle.
* **expect() vs assert** – `expect()` retries until timeout (UI is async); plain `assert` checks an already-computed Python value once.
* **Hard vs soft assertions** – hard stops the test at first failure; soft records failures, continues and reports all at the end (`utils/soft_assert.py`).
* **Why condition waits beat sleep()** – they proceed the moment the app is ready and fail with a clear reason; a fixed delay is flaky or wasteful.
* **Timeouts** – use a sensible default (5 s) and a separate navigation timeout; fix flakiness by waiting for the right condition, not by raising timeouts.

## 7. Secrets (Task 7)
* `.env.example` contains placeholders only; `.env` is git-ignored; credentials read via `os.environ` (`SAUCE_USERNAME`, `SAUCE_PASSWORD`).
* `tests/test_task7_secrets.py` verifies the password is absent from source files and generated reports.
* **CI/CD:** store secrets in the platform's secret store (GitHub Actions Secrets, GitLab masked variables, Jenkins Credentials, Azure Key Vault), inject them as environment variables at runtime, restrict access, rotate regularly, never echo them in logs.

## 8. Browser execution matrix (Task 5) – fill from your own run
Run `python run_matrix.py` (writes `reports/browser_matrix.md`) and paste the result here:

| Test | Chromium | Firefox | WebKit |
|---|---|---|---|
| Login | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| Search | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| Navigation | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| Form Validation | PASS/FAIL | PASS/FAIL | PASS/FAIL |

*Note:* SauceDemo has no search box, so "Search" = find a product by name and sort.

## 9. Submission checklist
Project folder ✔ requirements.txt ✔ pytest.ini ✔ .env.example (placeholders only) ✔ README ✔ screenshots/report (`reports/report.html`, `reports/report_<browser>.html`) ✔ matrix results ✔ no secrets (**delete your local `.env` before zipping/submitting**).
# Automation-Project
