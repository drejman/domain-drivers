import attrs as a

from .capacity_dimension import CapacityDimension
from .total_weight import TotalWeight


@a.define(frozen=True)
class Item[T: CapacityDimension]:
    name: str
    value: float
    _total_weight: TotalWeight[T] = a.field(hash=False)

    def is_weight_zero(self) -> bool:
        return len(self._total_weight.components) == 0

    @property
    def total_weight(self) -> TotalWeight[T]:
        return self._total_weight
