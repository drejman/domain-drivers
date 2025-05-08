from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

from schedule.allocation.demand import Demand
from schedule.shared.capability import Capability
from schedule.shared.timeslot import TimeSlot

if TYPE_CHECKING:
    from collections.abc import Iterable

    from schedule.allocation.allocations import Allocations


def freeze_demands(demand: Iterable[Demand]) -> tuple[Demand, ...]:
    return tuple(demand)


@a.define(frozen=True)
class Demands:
    all: tuple[Demand, ...] = a.field(converter=freeze_demands)

    @staticmethod
    def none() -> Demands:
        return Demands(all=())

    @staticmethod
    def of(*demands: Demand) -> Demands:
        return Demands(all=demands)

    @staticmethod
    def all_in_same_time_slot(time_slot: TimeSlot, *capabilities: Capability) -> Demands:
        return Demands.of(*[Demand(capability, time_slot) for capability in capabilities])

    def with_new(self, new_demands: Demands) -> Demands:
        return Demands(all=self.all + new_demands.all)

    def missing_demands(self, allocations: Allocations) -> Demands:
        return Demands(tuple(demand for demand in self.all if not self._satisfied_by(demand, allocations)))

    def _satisfied_by(self, demand: Demand, allocations: Allocations) -> bool:
        return any(
            allocation.capability == demand.capability and demand.time_slot.within(allocation.time_slot)
            for allocation in allocations.all
        )
