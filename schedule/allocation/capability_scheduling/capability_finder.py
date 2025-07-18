from collections.abc import Sequence

from schedule.availability import AvailabilityFacade
from schedule.shared.capability import Capability
from schedule.shared.timeslot import TimeSlot

from .allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from .allocatable_capability import (
    AllocatableCapability,
)
from .allocatable_capability_id import (
    AllocatableCapabilityId,
)
from .allocatable_capability_repository import (
    AllocatableCapabilityRepository,
)
from .allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)


class CapabilityFinder:
    def __init__(
        self,
        availability_facade: AvailabilityFacade,
        allocatable_capability_repository: AllocatableCapabilityRepository,
    ) -> None:
        self._availability_facade: AvailabilityFacade = availability_facade
        self._repository: AllocatableCapabilityRepository = allocatable_capability_repository

    def find_available_capabilities(
        self, capability: Capability, time_slot: TimeSlot
    ) -> AllocatableCapabilitiesSummary:
        found = self._repository.find_by_capability_within(
            capability.name, capability.type, time_slot.from_, time_slot.to
        )
        found = self._filter_availability_in_time_slot(found, time_slot)
        return self._create_summary(found)

    def find_capabilities(self, capability: Capability, time_slot: TimeSlot) -> AllocatableCapabilitiesSummary:
        found = self._repository.find_by_capability_within(
            capability.name, capability.type, time_slot.from_, time_slot.to
        )
        return self._create_summary(found)

    def find_by_id(self, allocatable_capability_ids: list[AllocatableCapabilityId]) -> AllocatableCapabilitiesSummary:
        found = self._repository.get_all(allocatable_capability_ids)
        return self._create_summary(list(found))

    def is_present(self, allocatable_capability_id: AllocatableCapabilityId) -> bool:
        return self._repository.exists(id=allocatable_capability_id)

    def _filter_availability_in_time_slot(
        self, allocatable_capabilities: Sequence[AllocatableCapability], time_slot: TimeSlot
    ) -> list[AllocatableCapability]:
        availability_ids = {
            allocatable_capability.id.to_availability_resource_id()
            for allocatable_capability in allocatable_capabilities
        }
        calendars = self._availability_facade.load_calendars(availability_ids, time_slot)
        return [
            allocatable_capability
            for allocatable_capability in allocatable_capabilities
            if time_slot in calendars.get(allocatable_capability.id.to_availability_resource_id()).available_slots()
        ]

    def _create_summary(self, found: Sequence[AllocatableCapability]) -> AllocatableCapabilitiesSummary:
        summaries = [
            AllocatableCapabilitySummary(
                allocatable_capability.id,
                allocatable_capability.resource_id,
                allocatable_capability.possible_capabilities,
                allocatable_capability.time_slot,
            )
            for allocatable_capability in found
        ]
        return AllocatableCapabilitiesSummary(all=summaries)
