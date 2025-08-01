from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

import attrs as a

from schedule.shared.timeslot import TimeSlot
from schedule.shared.utcnow import utcnow

from .demands import Demands
from .project_allocations_id import ProjectAllocationsId


@a.frozen
class CapabilitiesAllocatedEvent:
    allocated_capability_id: UUID
    project_id: ProjectAllocationsId
    missing_demands: Demands
    occurred_at: datetime = a.field(factory=utcnow)
    event_id: UUID = a.field(factory=uuid4, eq=False)


@a.frozen
class CapabilityReleasedEvent:
    project_id: ProjectAllocationsId
    missing_demands: Demands
    occurred_at: datetime = a.field(factory=utcnow)
    event_id: UUID = a.field(factory=uuid4, eq=False)


@a.frozen
class ProjectAllocationScheduledEvent:
    project_id: ProjectAllocationsId
    from_to: TimeSlot
    occurred_at: datetime = a.field(factory=utcnow)
    uuid: UUID = a.field(factory=uuid4)


@a.frozen
class ProjectAllocationsDemandsScheduledEvent:
    project_id: ProjectAllocationsId
    missing_demands: Demands
    occurred_at: datetime = a.field(factory=utcnow)
    uuid: UUID = a.field(factory=uuid4)
