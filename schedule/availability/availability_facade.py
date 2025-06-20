from schedule.shared.timeslot.time_slot import TimeSlot

from .calendar import Calendar
from .calendars import Calendars
from .grouped_resource_availability import GroupedResourceAvailability
from .owner import Owner
from .repository.availability_sqla_repository import ResourceAvailabilityRepository
from .repository.resource_availability_read_model import ResourceAvailabilityReadModel
from .resource_id import ResourceId
from .time_blocks.duration_unit import DurationUnit
from .time_blocks.normalized_slot import NormalizedSlot


class AvailabilityFacade:
    def __init__(
        self,
        repository: ResourceAvailabilityRepository,
        read_model: ResourceAvailabilityReadModel,
        duration_unit: DurationUnit | None = None,
    ) -> None:
        self._repository: ResourceAvailabilityRepository = repository
        self._read_model: ResourceAvailabilityReadModel = read_model
        if duration_unit is None:
            duration_unit = DurationUnit.default()
        self._duration_unit: DurationUnit = duration_unit

    def create_resource_slots(self, resource_id: ResourceId, time_slot: TimeSlot) -> None:
        """Create and persist availability slots for given resource over provided time_slot."""
        grouped_availability = GroupedResourceAvailability.of(
            resource_id=resource_id,
            time_slot=time_slot,
            duration_unit=self._duration_unit,
        )
        self._repository.add(grouped_availability)

    def block(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        """Reserve the resource for given time_slot and set the owner of this reservation to the requester."""
        grouped = self.find(resource_id=resource_id, time_slot=time_slot)
        result = grouped.block(requester=requester)
        if result is True:
            self._repository.add(grouped)
        return result

    def release(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        """Delete existing reservation for the given resource and for the given time_slot if requester matches."""
        grouped = self.find(resource_id=resource_id, time_slot=time_slot)
        result = grouped.release(requester=requester)
        if result is True:
            self._repository.add(grouped)
        return result

    def disable(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        """Turn off the possibility of reserving the resource, used by superusers or admins."""
        grouped = self.find(resource_id=resource_id, time_slot=time_slot)
        result = grouped.disable(requester=requester)
        if result is True:
            self._repository.add(grouped)
        return result

    def find(self, resource_id: ResourceId, time_slot: TimeSlot) -> GroupedResourceAvailability:
        time_slot = NormalizedSlot.from_time_slot(time_slot=time_slot, duration_unit=self._duration_unit)
        availabilities = self._repository.load_all_within_slot(resource_id=resource_id, time_slot=time_slot)
        return GroupedResourceAvailability(availabilities)

    def load_calendar(self, resource_id: ResourceId, within: TimeSlot) -> Calendar:
        normalized = NormalizedSlot.from_time_slot(within, self._duration_unit)
        return self._read_model.load(resource_id, normalized)

    def load_calendars(self, resource_ids: set[ResourceId], within: TimeSlot) -> Calendars:
        normalized = NormalizedSlot.from_time_slot(within, self._duration_unit)
        return self._read_model.load_all(resource_ids, normalized)
