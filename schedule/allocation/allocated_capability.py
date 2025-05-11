from __future__ import annotations

from uuid import UUID, uuid4

import attrs as a

from schedule.shared.capability import Capability
from schedule.shared.timeslot import TimeSlot


@a.define(frozen=True)
class AllocatedCapability:
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot
    allocated_capability_id: UUID = a.field(factory=uuid4, eq=False)
