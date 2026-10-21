"""Task 17 - custom ASYNC wait condition."""
import asyncio
import inspect
import time


class ConditionTimeoutError(TimeoutError):
    """Raised when a custom wait condition is not met in time."""


async def wait_until(condition, *, timeout_ms: int = 5000, poll_ms: int = 200,
                     message: str = "Condition was not met"):
    """Poll `condition()` until truthy; stops immediately when it is.

    `condition` may be a normal function or an async function / lambda returning a coroutine.
    Raises ConditionTimeoutError with a useful message (incl. the last exception).
    """
    deadline = time.monotonic() + timeout_ms / 1000
    last_error = None
    while True:
        try:
            result = condition()
            if inspect.isawaitable(result):
                result = await result
            if result:
                return True
        except Exception as exc:          # DOM may change while polling
            last_error = exc
        if time.monotonic() >= deadline:
            detail = f" | last error: {last_error!r}" if last_error else ""
            raise ConditionTimeoutError(f"{message} (waited {timeout_ms} ms){detail}")
        await asyncio.sleep(poll_ms / 1000)
