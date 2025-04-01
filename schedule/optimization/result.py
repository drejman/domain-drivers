import attrs as a

from .capacity_dimension import CapacityDimension
from .item import Item


@a.define(frozen=True)
class OptimizationResult[T: CapacityDimension]:
    profit: float
    chosen_items: list[Item[T]]
    item_to_capacities: dict[Item[T], set[T]]

    def __str__(self) -> str:
        return f"Result{{profit={self.profit}, chosen_items={self.chosen_items}}}"
