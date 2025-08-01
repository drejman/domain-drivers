from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

import attrs as a

from schedule.allocation import ProjectAllocationsId
from schedule.shared.utcnow import utcnow

from .earnings import Earnings


@a.frozen
class EarningsRecalculatedEvent:
    project_id: ProjectAllocationsId
    earnings: Earnings
    occurred_at: datetime = a.field(factory=utcnow)
    uuid: UUID = a.field(factory=uuid4)
