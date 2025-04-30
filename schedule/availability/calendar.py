from __future__ import annotations

import attrs as a

from schedule.shared.resource_name import ResourceName
from schedule.shared.timeslot import TimeSlot

from .owner import Owner


@a.define(frozen=True)
class Calendar:
    resource_id: ResourceName
    calendar: dict[Owner, tuple[TimeSlot, ...]]

    @staticmethod
    def empty(resource_id: ResourceName) -> Calendar:
        return Calendar(resource_id=resource_id, calendar={})

    @staticmethod
    def with_available_slots(resource_id: ResourceName, *available_slots: TimeSlot) -> Calendar:
        return Calendar(resource_id=resource_id, calendar={Owner.none(): available_slots})

    def available_slots(self) -> list[TimeSlot]:
        return list(self.calendar.get(Owner.none(), []))
