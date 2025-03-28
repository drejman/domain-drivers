from __future__ import annotations

import attrs as a

from .available_resource_capability import AvailableResourceCapability
from .capability import Capability
from .time_slot import TimeSlot


@a.define(frozen=True)
class Demand:
    _capability: Capability
    _slot: TimeSlot

    @classmethod
    def demand_for(cls, capability: Capability, slot: TimeSlot) -> Demand:
        return Demand(capability, slot)

    def is_satisfied_by(
        self, available_capability: AvailableResourceCapability
    ) -> bool:
        return available_capability.performs(self._capability) and self._slot.within(
            available_capability.time_slot
        )
