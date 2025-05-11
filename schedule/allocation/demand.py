from __future__ import annotations

import attrs as a

from schedule.shared.capability import Capability
from schedule.shared.timeslot import TimeSlot


@a.define(frozen=True)
class Demand:
    capability: Capability
    time_slot: TimeSlot
