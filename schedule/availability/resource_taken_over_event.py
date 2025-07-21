from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from uuid import UUID, uuid4

import attrs as a

from schedule.availability.owner import Owner
from schedule.availability.resource_id import ResourceId
from schedule.shared.timeslot import TimeSlot
from schedule.shared.utcnow import utcnow


def freeze_owners(owners: Iterable[Owner]) -> frozenset[Owner]:
    return frozenset(owners)


@a.frozen
class ResourceTakenOverEvent:
    resource_id: ResourceId
    previous_owners: frozenset[Owner] = a.field(converter=freeze_owners)
    slot: TimeSlot
    occurred_at: datetime = a.field(factory=utcnow)
    uuid: UUID = a.field(factory=uuid4)
