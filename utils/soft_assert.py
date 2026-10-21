"""Task 13 - soft (non-blocking) assertions, async version."""
import inspect


class SoftAssert:
    def __init__(self):
        self.failures: list[str] = []
        self.passed: list[str] = []

    async def check(self, label: str, assertion):
        """`assertion` is a callable returning an awaitable (e.g. lambda: expect(x).to_be_visible())."""
        try:
            result = assertion()
            if inspect.isawaitable(result):
                await result
            self.passed.append(label)
        except AssertionError as exc:
            text = str(exc).strip()
            self.failures.append(f"{label}: {text.splitlines()[0] if text else 'assertion failed'}")

    def assert_all(self):
        """Raise ONE AssertionError listing every collected failure."""
        if self.failures:
            body = "\n  - ".join(self.failures)
            raise AssertionError(f"{len(self.failures)} soft assertion(s) failed:\n  - {body}")
