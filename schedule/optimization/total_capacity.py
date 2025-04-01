from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .capacity_dimension import CapacityDimension


@a.define(frozen=True)
class TotalCapacity[T: CapacityDimension]:
    capacities: list[T]

    @classmethod
    def of(cls, *capacities: T) -> TotalCapacity[T]:
        return TotalCapacity[T](list(capacities))

    @classmethod
    def zero(cls) -> TotalCapacity[T]:
        return TotalCapacity[T]([])

    def add(self, capacities: Iterable[T]) -> TotalCapacity[T]:
        return TotalCapacity[T](capacities=self.capacities + list(capacities))

    def __len__(self) -> int:
        return len(self.capacities)
