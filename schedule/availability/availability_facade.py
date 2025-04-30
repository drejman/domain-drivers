from .calendars import Calendars


class AvailabilityFacade:
    def availabilities_of_resources(self) -> Calendars:
        return Calendars.of()  # TODO  # noqa: FIX002, TD002, TD003, TD004
