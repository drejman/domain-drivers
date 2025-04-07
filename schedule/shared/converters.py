from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def iterable_to_list[T](values: Iterable[T]) -> list[T]:
    return list(values)


def iterable_to_tuple[T](values: Iterable[T]) -> tuple[T, ...]:
    return tuple(values)
