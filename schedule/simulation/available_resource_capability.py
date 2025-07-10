from uuid import UUID

import attrs as a

from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot import TimeSlot
from schedule.simulation.capability_performer import CapabilityPerformer


@a.define(frozen=True)
class AvailableResourceCapability:
    _resource_id: UUID
    _capability: CapabilityPerformer
    time_slot: TimeSlot

    def performs(self, capability: Capability) -> bool:
        return self._capability.perform(capability)
