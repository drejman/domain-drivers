from collections.abc import Callable

import pytest

from schedule.allocation.capability_scheduling.allocatable_capability_id import AllocatableCapabilityId
from schedule.shared.capability.capability import Capability

from ...availability import AvailabilityFacade
from ...shared.timeslot import TimeSlot
from ..capability_scheduling.allocatable_resource_id import AllocatableResourceId
from ..capability_scheduling.capability_scheduler import CapabilityScheduler
from ..capability_scheduling.capability_selector import CapabilitySelector
from .availability_assert import AvailabilityAssert

AllocatableResourceFactory = Callable[[TimeSlot, Capability, AllocatableResourceId], AllocatableCapabilityId]


@pytest.fixture
def allocatable_resource_factory(
    capability_scheduler: CapabilityScheduler,
) -> AllocatableResourceFactory:
    def _create_allocatable_resource(
        period: TimeSlot, capability: Capability, resource_id: AllocatableResourceId
    ) -> AllocatableCapabilityId:
        capabilities = [CapabilitySelector.can_just_perform(capability)]
        allocatable_capability_ids = capability_scheduler.schedule_resource_capabilities_for_period(
            resource_id=resource_id, time_slot=period, capabilities=capabilities
        )
        assert len(allocatable_capability_ids) == 1
        return allocatable_capability_ids[0]

    return _create_allocatable_resource


@pytest.fixture
def availability_assert(availability_facade: AvailabilityFacade) -> AvailabilityAssert:
    return AvailabilityAssert(availability_facade)
