from __future__ import annotations

import attrs as a

from schedule.allocation.capability_scheduling import AllocatableCapabilityId
from schedule.shared.capability import Capability
from schedule.shared.timeslot import TimeSlot


@a.define(frozen=True)
class AllocatedCapability:
    allocated_capability_id: AllocatableCapabilityId
    capability: Capability
    time_slot: TimeSlot
