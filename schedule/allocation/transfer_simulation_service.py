from decimal import Decimal

from schedule.shared.timeslot.time_slot import TimeSlot
from schedule.simulation import SimulatedCapabilities, SimulationFacade

from .allocated_capability import AllocatedCapability
from .allocation_facade import AllocationFacade
from .cashflow.earnings import Earnings
from .project_allocations_id import ProjectAllocationsId
from .simulated_project_allocations import SimulatedProjectAllocations


class TransferSimulationService:
    def __init__(self, simulation_facade: SimulationFacade, allocation_facade: AllocationFacade) -> None:
        self._simulation_facade: SimulationFacade = simulation_facade
        self._allocation_facade: AllocationFacade = allocation_facade

    # TODO(rejman): consider changing method signature to use a DTO when it's stable  # noqa: FIX002
    def simulate_potential_transfer(  # noqa: PLR0913
        self,
        project_from: ProjectAllocationsId,
        project_to: ProjectAllocationsId,
        project_from_earnings: Earnings,
        project_to_earnings: Earnings,
        capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> Decimal:
        allocations_summary = self._allocation_facade.find_projects_allocations_by_ids(project_from, project_to)
        earnings = {project_from: project_from_earnings, project_to: project_to_earnings}
        simulated_allocations = SimulatedProjectAllocations(allocations_summary, earnings)

        result_before = self._simulation_facade.what_is_the_optimal_setup(
            simulated_allocations.to_simulated_projects(), SimulatedCapabilities.none()
        )
        after_transfer = simulated_allocations.transfer(project_from, project_to, capability, for_slot)
        result_after = self._simulation_facade.what_is_the_optimal_setup(
            after_transfer.to_simulated_projects(), SimulatedCapabilities.none()
        )

        return result_after.profit - result_before.profit
