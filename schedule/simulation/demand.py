from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

from schedule.optimization.weight_dimension import WeightDimension

from .available_resource_capability import AvailableResourceCapability

if TYPE_CHECKING:
    from .capability import Capability
    from .time_slot import TimeSlot


@a.define(frozen=True)
class Demand(WeightDimension[AvailableResourceCapability]):
    _capability: Capability
    _slot: TimeSlot

    @classmethod
    def demand_for(cls, capability: Capability, slot: TimeSlot) -> Demand:
        return Demand(capability, slot)

    def is_satisfied_by(self, capacity: AvailableResourceCapability) -> bool:
        return capacity.performs(self._capability) and self._slot.within(capacity.time_slot)
