from typing import Final

from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot

from ..allocation_facade import AllocationFacade
from ..demand import Demand
from ..demands import Demands
from ..project_allocations_id import ProjectAllocationsId


class TestDemandScheduling:
    JAVA: Final = Demand(Capability.skill("JAVA"), TimeSlot.create_daily_time_slot_at_utc(2022, 2, 2))

    def test_schedule_project_demands(self, allocation_facade: AllocationFacade) -> None:
        project_id = ProjectAllocationsId.new_one()

        allocation_facade.schedule_project_allocations_demands(project_id, Demands.of(self.JAVA))

        summary = allocation_facade.find_all_projects_allocations()
        assert len(summary.project_allocations[project_id].all) == 0
        assert summary.demands[project_id].all == (self.JAVA,)
