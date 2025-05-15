from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def iterable_to_list[T](values: Iterable[T]) -> list[T]:
    return list(values)


def iterable_to_tuple[T](values: Iterable[T]) -> tuple[T, ...]:
    return tuple(values)


def to_decimal(value: Decimal | int) -> Decimal:
    return Decimal(value)
