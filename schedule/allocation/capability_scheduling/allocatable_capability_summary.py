from __future__ import annotations

import attrs as a

from schedule.allocation.capability_scheduling.capability_selector import CapabilitySelector
from schedule.shared.timeslot.time_slot import TimeSlot

from .allocatable_capability_id import (
    AllocatableCapabilityId,
)
from .allocatable_resource_id import (
    AllocatableResourceId,
)


@a.frozen
class AllocatableCapabilitySummary:
    id: AllocatableCapabilityId
    allocatable_resource_id: AllocatableResourceId
    capabilities: CapabilitySelector
    time_slot: TimeSlot
