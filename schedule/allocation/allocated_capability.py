from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import attrs as a

if TYPE_CHECKING:
    from uuid import UUID

    from schedule.shared.capability import Capability
    from schedule.shared.timeslot import TimeSlot


@a.define(frozen=True)
class AllocatedCapability:
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot
    allocated_capability_id: UUID = a.field(factory=uuid4, eq=False)
