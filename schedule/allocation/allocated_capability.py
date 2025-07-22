from __future__ import annotations

import attrs as a

from schedule.allocation.capability_scheduling import AllocatableCapabilityId, CapabilitySelector
from schedule.shared.timeslot import TimeSlot


@a.define(frozen=True)
class AllocatedCapability:
    allocated_capability_id: AllocatableCapabilityId
    capability: CapabilitySelector
    time_slot: TimeSlot
