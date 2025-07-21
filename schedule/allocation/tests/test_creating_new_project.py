from typing import Any

from mockito import verify  # pyright: ignore [reportUnknownVariableType, reportMissingTypeStubs]
from mockito.matchers import arg_that  # pyright: ignore [reportUnknownVariableType, reportMissingTypeStubs]

from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot

from ...shared.event import EventBus
from ..allocation_facade import AllocationFacade
from ..demand import Demand
from ..demands import Demands
from ..events import ProjectAllocationScheduledEvent
from ..project_allocations_id import ProjectAllocationsId


class TestCreatingNewProject:
    JAN = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)
    FEB = TimeSlot.create_monthly_time_slot_at_utc(2021, 2)

    def test_create_new_project(self, allocation_facade: AllocationFacade, when: Any) -> None:
        when(EventBus).publish(...)
        demand = Demand(Capability.skill("JAVA"), self.JAN)

        demands = Demands.of(demand)
        new_project_id = allocation_facade.create_allocation(self.JAN, demands)

        summary = allocation_facade.find_all_projects_allocations()
        assert summary.demands[new_project_id] == demands
        assert summary.time_slots[new_project_id] == self.JAN
        verify(EventBus).publish(arg_that(lambda arg: self._is_project_allocation_event(arg, new_project_id, self.JAN)))

    def test_redefine_project_deadline(self, allocation_facade: AllocationFacade, when: Any) -> None:
        when(EventBus).publish(...)
        demand = Demand(Capability.skill("JAVA"), self.JAN)
        demands = Demands.of(demand)
        new_project_id = allocation_facade.create_allocation(self.JAN, demands)

        allocation_facade.edit_project_dates(new_project_id, self.FEB)

        summary = allocation_facade.find_all_projects_allocations()
        assert summary.time_slots[new_project_id] == self.FEB
        verify(EventBus).publish(arg_that(lambda arg: self._is_project_allocation_event(arg, new_project_id, self.FEB)))

    def _is_project_allocation_event(self, event: Any, project_id: ProjectAllocationsId, time_slot: TimeSlot) -> bool:
        return (
            isinstance(event, ProjectAllocationScheduledEvent)
            and event.project_id == project_id
            and event.from_to == time_slot
        )
