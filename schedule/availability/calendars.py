from __future__ import annotations

import attrs as a

from .calendar import Calendar
from .resource_id import ResourceId


@a.define(frozen=True)
class Calendars:
    calendars: dict[ResourceId, Calendar]

    @staticmethod
    def of(*calendars: Calendar) -> Calendars:
        return Calendars({calendar.resource_id: calendar for calendar in calendars})

    def get(self, resource_id: ResourceId) -> Calendar:
        return self.calendars.get(resource_id, Calendar.empty(resource_id))
