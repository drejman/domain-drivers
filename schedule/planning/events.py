from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from uuid import UUID, uuid4

import attrs as a

from schedule.availability import ResourceId
from schedule.shared.timeslot import TimeSlot
from schedule.shared.utcnow import utcnow

from .demands import Demands
from .project_id import ProjectId


@a.frozen
class CapabilitiesDemandedEvent:
    project_id: ProjectId
    demands: Demands
    occurred_at: datetime = a.field(factory=utcnow)
    uuid: UUID = a.field(factory=uuid4)


@a.frozen
class CriticalStagePlannedEvent:
    project_id: ProjectId
    stage_time_slot: TimeSlot
    critical_resource_id: ResourceId | None
    occurred_at: datetime = a.field(factory=utcnow)


def freeze_resources(
    resources: Iterable[ResourceId],
) -> frozenset[ResourceId]:
    return frozenset(resources)


@a.frozen
class NeededResourcesChosenEvent:
    project_id: ProjectId
    needed_resources: frozenset[ResourceId] = a.field(converter=freeze_resources)
    time_slot: TimeSlot
    occurred_at: datetime = a.field(factory=utcnow)
