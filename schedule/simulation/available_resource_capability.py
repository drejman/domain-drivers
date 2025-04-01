from uuid import UUID

import attrs as a

from schedule.optimization.capacity_dimension import CapacityDimension

from .capability import Capability
from .time_slot import TimeSlot


@a.define(frozen=True)
class AvailableResourceCapability(CapacityDimension):
    _resource_id: UUID
    _capability: Capability
    time_slot: TimeSlot

    def performs(self, capability: Capability) -> bool:
        return self._capability == capability
