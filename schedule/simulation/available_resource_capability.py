from uuid import UUID

import attrs as a

from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot import TimeSlot


@a.define(frozen=True)
class AvailableResourceCapability:
    _resource_id: UUID
    _capability: Capability
    time_slot: TimeSlot

    def performs(self, capability: Capability) -> bool:
        return self._capability == capability
