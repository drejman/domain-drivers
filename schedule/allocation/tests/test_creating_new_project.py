from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot

from ..allocation_facade import AllocationFacade
from ..demand import Demand
from ..demands import Demands


class TestCreatingNewProject:
    JAN = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)
    FEB = TimeSlot.create_monthly_time_slot_at_utc(2021, 2)

    def test_create_new_projct(self, allocation_facade: AllocationFacade) -> None:
        demand = Demand(Capability.skill("JAVA"), self.JAN)

        demands = Demands.of(demand)
        new_project_id = allocation_facade.create_allocation(self.JAN, demands)

        summary = allocation_facade.find_all_projects_allocations()
        assert summary.demands[new_project_id] == demands
        assert summary.time_slots[new_project_id] == self.JAN

    def test_redefine_project_deadline(self, allocation_facade: AllocationFacade) -> None:
        demand = Demand(Capability.skill("JAVA"), self.JAN)
        demands = Demands.of(demand)
        new_project_id = allocation_facade.create_allocation(self.JAN, demands)

        allocation_facade.edit_project_dates(new_project_id, self.FEB)

        summary = allocation_facade.find_all_projects_allocations()
        assert summary.time_slots[new_project_id] == self.FEB
