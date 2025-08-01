import time
from collections.abc import Callable


def timeout(milliseconds: int, callable: Callable[[], None]) -> None:  # noqa: A002
    start = time.monotonic()
    end = start + milliseconds / 1000
    while time.monotonic() <= end:
        try:
            callable()
        except AssertionError:
            time.sleep(0.05)
        else:
            return

    raise TimeoutError("Timeout reached")  # noqa: EM101, TRY003


def timeout_never(milliseconds: int, callable: Callable[[], None]) -> None:  # noqa: A002
    __tracebackhide__ = True

    start = time.monotonic()
    end = start + milliseconds / 1000
    while time.monotonic() <= end:
        try:
            callable()
        except AssertionError:
            time.sleep(0.05)
        else:
            raise AssertionError("Condition should never be met")  # noqa: EM101, TRY003
