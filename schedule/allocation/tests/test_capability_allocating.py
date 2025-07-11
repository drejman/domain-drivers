import pytest

from schedule.allocation.capability_scheduling.allocatable_capability_id import AllocatableCapabilityId
from schedule.availability.resource_id import ResourceId
from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot

from ...availability import AvailabilityFacade
from ...availability.owner import Owner
from ..allocated_capability import AllocatedCapability
from ..allocation_facade import AllocationFacade
from ..capability_scheduling.allocatable_resource_id import AllocatableResourceId
from ..demand import Demand
from ..demands import Demands
from ..project_allocations_id import ProjectAllocationsId
from .conftest import AllocatableResourceFactory


class AvailabilityAssert:
    def __init__(self, availability_facade: AvailabilityFacade) -> None:
        self._availability_facade: AvailabilityFacade = availability_facade

    def assert_availability_was_blocked(
        self,
        resource_id: ResourceId,
        period: TimeSlot,
        project_id: ProjectAllocationsId,
    ) -> None:
        __tracebackhide__ = True

        owner = Owner(project_id.id)
        calendars = self._availability_facade.load_calendars({resource_id}, period)
        assert all(calendar.taken_by(owner) == (period,) for calendar in calendars.calendars.values())


@pytest.fixture
def availability_assert(availability_facade: AvailabilityFacade) -> AvailabilityAssert:
    return AvailabilityAssert(availability_facade)


class TestCapabilityAllocating:
    RESOURCE_ID = AllocatableResourceId.new_one()

    def test_allocate_capability_to_project(
        self,
        allocation_facade: AllocationFacade,
        allocatable_resource_factory: AllocatableResourceFactory,
        availability_assert: AvailabilityAssert,
    ) -> None:
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        skill_java = Capability.skill("JAVA")
        demand = Demand(skill_java, one_day)
        allocatable_resource_id = allocatable_resource_factory(one_day, skill_java, self.RESOURCE_ID)
        project_id = ProjectAllocationsId.new_one()
        allocation_facade.schedule_project_allocations_demands(project_id, Demands.of(demand))

        result = allocation_facade.allocate_to_project(project_id, allocatable_resource_id, skill_java, one_day)

        assert result is not None
        summary = allocation_facade.find_all_projects_allocations()
        assert summary.project_allocations[project_id].all == {
            AllocatedCapability(allocatable_resource_id, skill_java, one_day)
        }
        assert summary.demands[project_id].all == (demand,)
        availability_assert.assert_availability_was_blocked(
            allocatable_resource_id.to_availability_resource_id(), one_day, project_id
        )

    def test_cant_allocate_when_resource_not_available(
        self,
        allocatable_resource_factory: AllocatableResourceFactory,
        availability_facade: AvailabilityFacade,
        allocation_facade: AllocationFacade,
    ) -> None:
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        skill_java = Capability.skill("JAVA")
        demand = Demand(skill_java, one_day)
        allocatable_resource_id = allocatable_resource_factory(one_day, skill_java, self.RESOURCE_ID)
        _ = availability_facade.block(allocatable_resource_id.to_availability_resource_id(), one_day, Owner.new_one())
        project_id = ProjectAllocationsId.new_one()
        allocation_facade.schedule_project_allocations_demands(project_id, Demands.of(demand))

        result = allocation_facade.allocate_to_project(project_id, allocatable_resource_id, skill_java, one_day)

        assert result is None
        summary = allocation_facade.find_all_projects_allocations()
        assert summary.project_allocations[project_id].all == set()

    def test_release_capability_for_the_project(
        self,
        allocation_facade: AllocationFacade,
        allocatable_resource_factory: AllocatableResourceFactory,
    ) -> None:
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        allocatable_resource_id = allocatable_resource_factory(one_day, Capability.skill("JAVA"), self.RESOURCE_ID)
        project_id = ProjectAllocationsId.new_one()
        allocation_facade.schedule_project_allocations_demands(project_id, Demands.none())
        chosen_capability = Capability.skill("JAVA")
        allocated_id = allocation_facade.allocate_to_project(
            project_id, allocatable_resource_id, chosen_capability, one_day
        )
        assert allocated_id is not None

        result = allocation_facade.release_from_project(project_id, AllocatableCapabilityId(allocated_id), one_day)

        assert result is True
        summary = allocation_facade.find_all_projects_allocations()
        assert len(summary.project_allocations[project_id].all) == 0
