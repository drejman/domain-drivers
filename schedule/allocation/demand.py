from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

if TYPE_CHECKING:
    from schedule.shared.timeslot import TimeSlot
    from schedule.simulation import Capability


@a.define(frozen=True)
class Demand:
    capability: Capability
    time_slot: TimeSlot
