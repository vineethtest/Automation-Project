"""Runs the matrix tests on Chromium, Firefox and WebKit and writes reports/browser_matrix.md"""
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
BROWSERS = ["chromium", "firefox", "webkit"]
LABELS = {"test_login": "Login", "test_search": "Search",
          "test_navigation": "Navigation", "test_form_validation": "Form Validation"}


def run(browser: str) -> dict:
    xml = REPORTS / f"junit_{browser}.xml"
    subprocess.run([sys.executable, "-m", "pytest", "tests/test_task5_browser_matrix.py",
                    "--browser", browser, f"--junitxml={xml}",
                    f"--html=reports/report_{browser}.html"], cwd=ROOT)
    results = {}
    if xml.exists():
        for case in ET.parse(xml).getroot().iter("testcase"):
            name = case.get("name").split("[")[0]
            if case.find("failure") is not None or case.find("error") is not None:
                results[name] = "FAIL"
            elif case.find("skipped") is not None:
                results[name] = "SKIP"
            else:
                results[name] = "PASS"
    return results


def main():
    REPORTS.mkdir(exist_ok=True)
    data = {b: run(b) for b in BROWSERS}
    lines = ["| Test | Chromium | Firefox | WebKit |", "|---|---|---|---|"]
    for key, label in LABELS.items():
        row = [data[b].get(key, "N/A") for b in BROWSERS]
        lines.append(f"| {label} | " + " | ".join(row) + " |")
    table = "\n".join(lines)
    (REPORTS / "browser_matrix.md").write_text(table + "\n")
    print("\n" + table)


if __name__ == "__main__":
    main()
