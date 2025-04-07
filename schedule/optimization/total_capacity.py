from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

from schedule.shared.converters import iterable_to_tuple

if TYPE_CHECKING:
    from .capacity_dimension import CapacityDimension


@a.define(frozen=True)
class TotalCapacity[T: CapacityDimension]:
    capacities: tuple[T, ...] = a.field(converter=iterable_to_tuple)

    @classmethod
    def of(cls, *capacities: T) -> TotalCapacity[T]:
        return TotalCapacity[T](capacities)

    @classmethod
    def zero(cls) -> TotalCapacity[T]:
        return TotalCapacity[T]([])

    def add(self, *capacities: T) -> TotalCapacity[T]:
        return TotalCapacity[T](capacities=list(self.capacities) + list(capacities))

    def __len__(self) -> int:
        return len(self.capacities)
