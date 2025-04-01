from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

from .capacity_dimension import CapacityDimension

if TYPE_CHECKING:
    from .weight_dimension import WeightDimension


@a.define(frozen=True)
class TotalWeight[T: CapacityDimension]:
    components: list[WeightDimension[T]]

    @classmethod
    def zero(cls) -> TotalWeight[T]:
        return TotalWeight[T]([])

    @classmethod
    def of(cls, *components: WeightDimension[T]) -> TotalWeight[T]:
        return TotalWeight(list(components))
