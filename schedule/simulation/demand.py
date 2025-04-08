from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

if TYPE_CHECKING:
    from schedule.shared.timeslot import TimeSlot

    from .available_resource_capability import AvailableResourceCapability
    from .capability import Capability


@a.define(frozen=True)
class Demand:
    _capability: Capability
    _slot: TimeSlot

    @classmethod
    def demand_for(cls, capability: Capability, slot: TimeSlot) -> Demand:
        return Demand(capability, slot)

    def is_satisfied_by(self, capacity: AvailableResourceCapability) -> bool:
        return capacity.performs(self._capability) and self._slot.within(capacity.time_slot)
