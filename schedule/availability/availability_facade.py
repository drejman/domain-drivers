from collections.abc import Iterable

from schedule.availability.resource_taken_over_event import ResourceTakenOverEvent
from schedule.shared.event.event_publisher import EventPublisher
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
        event_publisher: EventPublisher,
        duration_unit: DurationUnit | None = None,
    ) -> None:
        self._repository: ResourceAvailabilityRepository = repository
        self._read_model: ResourceAvailabilityReadModel = read_model
        self._event_publisher: EventPublisher = event_publisher
        if duration_unit is None:
            duration_unit = DurationUnit.default()
        self._duration_unit: DurationUnit = duration_unit

    def create_resource_slots(
        self, resource_id: ResourceId, time_slot: TimeSlot
    ) -> None:  # TODO: check usages and add parent  # noqa: FIX002, TD002
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
        return self._block(grouped, requester)

    def block_random_available(
        self, resource_ids: Iterable[ResourceId], within: TimeSlot, requester: Owner
    ) -> ResourceId | None:
        time_slot = NormalizedSlot.from_time_slot(time_slot=within, duration_unit=self._duration_unit)
        grouped_availability = GroupedResourceAvailability(
            self._repository.load_availabilities_of_random_resources_within(time_slot, *resource_ids)
        )
        result = self._block(grouped_availability, requester)
        return grouped_availability.resource_id if result is True else None

    def _block(self, to_block: GroupedResourceAvailability, requester: Owner) -> bool:
        result = to_block.block(requester=requester)
        if result is True:
            self._repository.add(to_block)
        return result

    def release(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        """Delete existing reservation for the given resource and for the given time_slot if requester matches."""
        grouped = self.find(resource_id=resource_id, time_slot=time_slot)
        result = grouped.release(requester=requester)
        if result is True:
            self._repository.add(grouped)
        else:
            self._repository.expire(
                grouped
            )  # TODO: probably not needed once transactions with proper rollbacks are added  # noqa: FIX002, TD002
        return result

    def disable(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        """Turn off the possibility of reserving the resource, used by superusers or admins."""
        to_disable = self.find(resource_id=resource_id, time_slot=time_slot)
        previous_owners = to_disable.owners
        if result := to_disable.disable(requester=requester):
            self._repository.add(to_disable)
            self._event_publisher.publish(
                ResourceTakenOverEvent(resource_id=resource_id, slot=time_slot, previous_owners=previous_owners)
            )
        return result

    def find(self, resource_id: ResourceId, time_slot: TimeSlot) -> GroupedResourceAvailability:
        time_slot = NormalizedSlot.from_time_slot(time_slot=time_slot, duration_unit=self._duration_unit)
        availabilities = self._repository.load_all_within_slot(resource_id=resource_id, time_slot=time_slot)
        return GroupedResourceAvailability(availabilities)

    def load_calendar(self, resource_id: ResourceId, within: TimeSlot) -> Calendar:
        normalized = NormalizedSlot.from_time_slot(within, self._duration_unit)
        return self._read_model.load(resource_id, normalized)

    def load_calendars(self, resource_ids: Iterable[ResourceId], within: TimeSlot) -> Calendars:
        normalized = NormalizedSlot.from_time_slot(within, self._duration_unit)
        return self._read_model.load_all(resource_ids, normalized)
