from typing import Any, Final

from mockito import verify  # pyright: ignore [reportUnknownVariableType, reportMissingTypeStubs]
from mockito.matchers import arg_that  # pyright: ignore [reportUnknownVariableType, reportMissingTypeStubs]

from schedule.shared.capability.capability import Capability
from schedule.shared.event import EventBus
from schedule.shared.timeslot.time_slot import TimeSlot

from ..allocation_facade import AllocationFacade
from ..demand import Demand
from ..demands import Demands
from ..events import ProjectAllocationsDemandsScheduledEvent
from ..project_allocations_id import ProjectAllocationsId


class TestDemandScheduling:
    JAVA: Final = Demand(Capability.skill("JAVA"), TimeSlot.create_daily_time_slot_at_utc(2022, 2, 2))

    def test_schedule_project_demands(self, allocation_facade: AllocationFacade, when: Any) -> None:
        when(EventBus).publish(...)
        project_id = ProjectAllocationsId.new_one()

        demands = Demands.of(self.JAVA)
        allocation_facade.schedule_project_allocations_demands(project_id, demands)

        summary = allocation_facade.find_all_projects_allocations()
        assert len(summary.project_allocations[project_id].all) == 0
        assert summary.demands[project_id].all == (self.JAVA,)
        verify(EventBus).publish(arg_that(lambda arg: self._is_project_allocation_event(arg, project_id, demands)))

    def _is_project_allocation_event(self, event: Any, project_id: ProjectAllocationsId, demands: Demands) -> bool:
        return (
            isinstance(event, ProjectAllocationsDemandsScheduledEvent)
            and event.project_id == project_id
            and event.missing_demands == demands
        )
