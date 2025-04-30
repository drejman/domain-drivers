from __future__ import annotations

import attrs as a

from schedule.shared.resource_name import ResourceName

from .calendar import Calendar


@a.define(frozen=True)
class Calendars:
    calendars: dict[ResourceName, Calendar]

    @staticmethod
    def of(*calendars: Calendar) -> Calendars:
        return Calendars({calendar.resource_id: calendar for calendar in calendars})

    def get(self, resource_id: ResourceName) -> Calendar:
        return self.calendars.get(resource_id, Calendar.empty(resource_id))
