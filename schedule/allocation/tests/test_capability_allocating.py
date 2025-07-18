from typing import Final

import pytest

from schedule.allocation.capability_scheduling.allocatable_capability_id import AllocatableCapabilityId
from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot

from ...availability import AvailabilityFacade
from ...availability.owner import Owner
from ..allocation_facade import AllocationFacade
from ..capability_scheduling.allocatable_resource_id import AllocatableResourceId
from ..capability_scheduling.capability_scheduler import CapabilityScheduler
from ..capability_scheduling.capability_selector import CapabilitySelector
from ..demand import Demand
from ..demands import Demands
from ..project_allocations_id import ProjectAllocationsId


class TestCapabilityAllocating:
    ALLOCATABLE_RESOURCE_ID: Final = AllocatableResourceId.new_one()
    ALLOCATABLE_RESOURCE_ID_2: Final = AllocatableResourceId.new_one()
    ALLOCATABLE_RESOURCE_ID_3: Final = AllocatableResourceId.new_one()

    @pytest.fixture(autouse=True)
    def setup(
        self,
        capability_scheduler: CapabilityScheduler,
        allocation_facade: AllocationFacade,
        availability_facade: AvailabilityFacade,
    ) -> None:
        self._capability_scheduler = capability_scheduler
        self._allocation_facade = allocation_facade
        self._availability_facade = availability_facade

    def test_can_allocate_any_capability_of_required_type(self) -> None:
        java_and_python = CapabilitySelector.can_perform_one_of(Capability.skills("JAVA", "PYTHON"))
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        allocatable_capability_id_1 = self._schedule_capabilities(
            self.ALLOCATABLE_RESOURCE_ID, java_and_python, one_day
        )
        allocatable_capability_id_2 = self._schedule_capabilities(
            self.ALLOCATABLE_RESOURCE_ID_2, java_and_python, one_day
        )
        allocatable_capability_id_3 = self._schedule_capabilities(
            self.ALLOCATABLE_RESOURCE_ID_3, java_and_python, one_day
        )
        project_id = ProjectAllocationsId.new_one()
        self._allocation_facade.schedule_project_allocations_demands(project_id, Demands.none())

        result = self._allocation_facade.allocate_capability_to_project_for_period(
            project_id, Capability.skill("JAVA"), one_day
        )

        assert result is True
        allocated_capabilities_ids = self._load_project_allocations(project_id)
        assert allocated_capabilities_ids & {
            allocatable_capability_id_1,
            allocatable_capability_id_2,
            allocatable_capability_id_3,
        }
        assert self._availability_was_blocked(allocated_capabilities_ids, one_day, project_id)

    def test_cant_allocate_any_capability_of_required_type_when_no_capabilities(
        self,
    ) -> None:
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        project_id = ProjectAllocationsId.new_one()
        self._allocation_facade.schedule_project_allocations_demands(project_id, Demands.none())

        result = self._allocation_facade.allocate_capability_to_project_for_period(
            project_id, Capability.skill("DEBUGGING"), one_day
        )

        assert result is False
        summary = self._allocation_facade.find_all_projects_allocations()
        assert len(summary.project_allocations[project_id].all) == 0

    def test_cant_allocate_any_capability_of_required_type_when_all_capabilities_taken(
        self,
    ) -> None:
        debugging = Capability.skill("DEBUGGING")
        capability = CapabilitySelector.can_perform_one_of({debugging})
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        allocatable_capability_1 = self._schedule_capabilities(self.ALLOCATABLE_RESOURCE_ID, capability, one_day)
        allocatable_capability_2 = self._schedule_capabilities(self.ALLOCATABLE_RESOURCE_ID_2, capability, one_day)
        project_1 = self._allocation_facade.create_allocation(one_day, Demands.of(Demand(debugging, one_day)))
        project_2 = self._allocation_facade.create_allocation(one_day, Demands.of(Demand(debugging, one_day)))
        _ = self._allocation_facade.allocate_to_project(project_1, allocatable_capability_1, debugging, one_day)
        _ = self._allocation_facade.allocate_to_project(project_2, allocatable_capability_2, debugging, one_day)
        project_id = ProjectAllocationsId.new_one()
        self._allocation_facade.schedule_project_allocations_demands(project_id, Demands.none())

        result = self._allocation_facade.allocate_capability_to_project_for_period(project_id, debugging, one_day)

        assert result is False
        summary = self._allocation_facade.find_all_projects_allocations()
        assert len(summary.project_allocations[project_id].all) == 0

    def _schedule_capabilities(
        self,
        allocatable_resource_id: AllocatableResourceId,
        capabilities: CapabilitySelector,
        time_slot: TimeSlot,
    ) -> AllocatableCapabilityId:
        allocatable_capability_ids = self._capability_scheduler.schedule_resource_capabilities_for_period(
            allocatable_resource_id, [capabilities], time_slot
        )
        assert len(allocatable_capability_ids) == 1
        return allocatable_capability_ids[0]

    def _load_project_allocations(self, project_id: ProjectAllocationsId) -> set[AllocatableCapabilityId]:
        summary = self._allocation_facade.find_all_projects_allocations()
        allocated_capabilities = summary.project_allocations[project_id].all
        return {ac.allocated_capability_id for ac in allocated_capabilities}

    def _availability_was_blocked(
        self,
        capabilities: set[AllocatableCapabilityId],
        time_slot: TimeSlot,
        project_id: ProjectAllocationsId,
    ) -> bool:
        resource_ids = {ac.to_availability_resource_id() for ac in capabilities}
        calendars = self._availability_facade.load_calendars(resource_ids, time_slot)
        owner = Owner(project_id.id)
        return all(calendar.taken_by(owner) == (time_slot,) for calendar in calendars.calendars.values())
