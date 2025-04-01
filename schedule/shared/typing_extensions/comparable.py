from __future__ import annotations

from typing import Any, Protocol


class SupportsDunderLT(Protocol):
    def __lt__(self, __other: Any) -> bool: ...  # noqa: ANN401, PYI063


class SupportsDunderGT(Protocol):
    def __gt__(self, __other: Any) -> bool: ...  # noqa: ANN401, PYI063


Comparable = SupportsDunderLT | SupportsDunderGT
