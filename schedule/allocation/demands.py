from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

if TYPE_CHECKING:
    from collections.abc import Iterable

    from schedule.allocation.allocations import Allocations
    from schedule.allocation.demand import Demand


def freeze_demands(demand: Iterable[Demand]) -> tuple[Demand, ...]:
    return tuple(demand)


@a.define(frozen=True)
class Demands:
    all: tuple[Demand, ...] = a.field(converter=freeze_demands)

    def missing_demands(self, allocations: Allocations) -> Demands:
        return Demands([demand for demand in self.all if not self._satisfied_by(demand, allocations)])

    def _satisfied_by(self, demand: Demand, allocations: Allocations) -> bool:
        return any(
            allocation.capability == demand.capability and demand.time_slot.within(allocation.time_slot)
            for allocation in allocations.all
        )
