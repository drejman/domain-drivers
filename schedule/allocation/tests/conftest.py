from collections.abc import Callable

import pytest
from lagom import Container

from ...availability import AvailabilityFacade, ResourceId
from ...shared.timeslot import TimeSlot
from ..allocation_facade import AllocationFacade


@pytest.fixture
def allocation_facade(container: Container) -> AllocationFacade:
    return container.resolve(AllocationFacade)


AllocatableResourceFactory = Callable[[TimeSlot], ResourceId]


@pytest.fixture
def allocatable_resource_factory(
    availability_facade: AvailabilityFacade,
) -> AllocatableResourceFactory:
    def _create_allocatable_resource(period: TimeSlot) -> ResourceId:
        resource_id = ResourceId.new_one()
        availability_facade.create_resource_slots(resource_id, period)
        return resource_id

    return _create_allocatable_resource
