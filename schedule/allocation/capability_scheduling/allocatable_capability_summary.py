from __future__ import annotations

import attrs as a

from schedule.shared.capability.capability import Capability
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
    capability: Capability
    time_slot: TimeSlot
