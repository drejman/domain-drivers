from schedule.shared.timeslot.time_slot import TimeSlot

from .grouped_resource_availability import GroupedResourceAvailability
from .normalized_time_slots.normalize_slot import slot_to_normalized_slot
from .normalized_time_slots.time_quant import TimeQuantumInMinutes
from .owner import Owner
from .repository.availability_sqla_repository import ResourceAvailabilityRepository
from .resource_availability_id import ResourceAvailabilityId


class AvailabilityFacade:
    def __init__(
        self, repository: ResourceAvailabilityRepository, time_quantum: TimeQuantumInMinutes | None = None
    ) -> None:
        self._repository: ResourceAvailabilityRepository = repository
        if time_quantum is None:
            time_quantum = TimeQuantumInMinutes.default_segment()
        self._time_quantum: TimeQuantumInMinutes = time_quantum

    def create_resource_slots(self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot) -> None:
        """Create and persist availability slots for given resource over provided time_slot."""
        grouped_availability = GroupedResourceAvailability.of(
            resource_id=resource_id,
            time_slot=time_slot,
        )
        self._repository.add(grouped_availability)

    def block(self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner) -> bool:
        """Reserve the resource for given time_slot and set the owner of this reservation to the requester."""
        grouped = self.find(resource_id=resource_id, time_slot=time_slot)
        result = grouped.block(requester=requester)
        if result is True:
            self._repository.add(grouped)
        return result

    def release(self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner) -> bool:
        """Delete existing reservation for the given resource and for the given time_slot if requester matches."""
        grouped = self.find(resource_id=resource_id, time_slot=time_slot)
        result = grouped.release(requester=requester)
        if result is True:
            self._repository.add(grouped)
        return result

    def disable(self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner) -> bool:
        """Turn off the possibility of reserving the resource, used by superusers or admins."""
        grouped = self.find(resource_id=resource_id, time_slot=time_slot)
        result = grouped.disable(requester=requester)
        if result is True:
            self._repository.add(grouped)
        return result

    def find(self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot) -> GroupedResourceAvailability:
        time_slot = slot_to_normalized_slot(time_slot=time_slot, time_quant_in_minutes=self._time_quantum)
        availabilities = self._repository.load_all_within_slot(resource_id=resource_id, time_slot=time_slot)
        return GroupedResourceAvailability(availabilities)
