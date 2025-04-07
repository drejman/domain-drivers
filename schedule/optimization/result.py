from decimal import Decimal
from typing import override

import attrs as a

from .capacity_dimension import CapacityDimension
from .item import Item

Number = Decimal | float | int | str


def number_to_decimal(value: Number) -> Decimal:
    return Decimal(value)


@a.define(frozen=True)
class OptimizationResult[T: CapacityDimension]:
    profit: Decimal = a.field(converter=number_to_decimal)
    chosen_items: list[Item[T]]
    item_to_capacities: dict[Item[T], set[T]]

    @override
    def __str__(self) -> str:
        return f"Result{{profit={self.profit}, chosen_items={self.chosen_items}}}"
