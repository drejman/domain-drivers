from collections.abc import Callable

from schedule.shared.typing_extensions import Comparable

from .capacity_dimension import CapacityDimension
from .dp_optimization import DpOptimization
from .item import Item
from .result import OptimizationResult
from .total_capacity import TotalCapacity


class OptimizationFacade[T: CapacityDimension]:
    def calculate(
        self,
        items: list[Item[T]],
        total_capacity: TotalCapacity[T],
        loss_function: Callable[[Item[T]], Comparable] | None = None,
    ) -> OptimizationResult[T]:
        sort_key_getter = loss_function or self.default_loss_function
        return DpOptimization[T]().calculate(items, total_capacity, sort_key_getter)

    @staticmethod
    def default_loss_function(x: Item[T]) -> Comparable:
        return -x.value
