from collections.abc import Callable, Iterable, Sequence

from schedule.shared.typing_extensions import Comparable

from .capacity_dimension import CapacityDimension
from .item import Item
from .result import OptimizationResult
from .total_capacity import TotalCapacity
from .total_weight import TotalWeight


class DpOptimization[T: CapacityDimension]:
    def calculate(
        self,
        items: Iterable[Item[T]],
        total_capacity: TotalCapacity[T],
        sort_key_getter: Callable[[Item[T]], Comparable],
    ) -> OptimizationResult[T]:
        capacities_size = len(total_capacity)
        dp = [0] * (capacities_size + 1)
        chosen_items_list: list[list[Item[T]]] = [[] for _ in range(capacities_size + 1)]
        allocated_capacities_list: list[set[CapacityDimension]] = [set() for _ in range(capacities_size + 1)]

        for i in range(capacities_size + 1):
            chosen_items_list[i] = []
            allocated_capacities_list[i] = set()

        all_capacities = total_capacity.capacities
        item_to_capacities_map: dict[Item[T], set[T]] = {}

        for item in sorted(items, key=sort_key_getter):
            chosen_capacities = self._match_capacities(
                item.total_weight,
                all_capacities,
            )
            all_capacities = tuple(capacity for capacity in all_capacities if capacity not in chosen_capacities)

            if not chosen_capacities:
                continue

            sum_value = int(item.value)
            chosen_capacities_count = len(chosen_capacities)

            for j in range(capacities_size, chosen_capacities_count - 1, -1):
                if dp[j] < sum_value + dp[j - chosen_capacities_count]:
                    dp[j] = sum_value + dp[j - chosen_capacities_count]

                    chosen_items_list[j] = chosen_items_list[j - chosen_capacities_count].copy()
                    chosen_items_list[j].append(item)

                    allocated_capacities_list[j].update(chosen_capacities)

            item_to_capacities_map[item] = set(chosen_capacities)

        automatically_included_items = [item for item in items if item.is_weight_zero()]
        guaranteed_value = sum(item.value for item in automatically_included_items)

        chosen_items_list[capacities_size].extend(automatically_included_items)
        return OptimizationResult(
            dp[capacities_size] + guaranteed_value,
            chosen_items_list[capacities_size],
            item_to_capacities_map,
        )

    def _match_capacities(self, total_weight: TotalWeight[T], available_capacities: Sequence[T]) -> list[T]:
        result: list[T] = []
        for weight_component in total_weight.components:
            matching_capacity: T | None = next(
                (capacity for capacity in available_capacities if weight_component.is_satisfied_by(capacity)),
                None,
            )

            if matching_capacity:
                result.append(matching_capacity)
            else:
                return []
        return result
