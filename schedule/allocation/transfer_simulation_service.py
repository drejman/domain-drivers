from decimal import Decimal

from schedule.shared.timeslot.time_slot import TimeSlot
from schedule.simulation import SimulatedCapabilities, SimulationFacade

from .allocated_capability import AllocatedCapability
from .project_allocations_id import ProjectAllocationsId
from .simulated_transfer import SimulatedProjectAllocations


class TransferSimulationService:
    def __init__(self, simulation_facade: SimulationFacade) -> None:
        self._simulation_facade: SimulationFacade = simulation_facade

    def simulate_potential_transfer(
        self,
        simulated_project_allocations: SimulatedProjectAllocations,
        project_from: ProjectAllocationsId,
        project_to: ProjectAllocationsId,
        capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> Decimal:
        # Project rather fetched from a DB.
        result_before = self._simulation_facade.what_is_the_optimal_setup(
            simulated_project_allocations.to_simulated_projects(), SimulatedCapabilities.none()
        )

        after_transfer = simulated_project_allocations.transfer(project_from, project_to, capability, for_slot)
        result_after = self._simulation_facade.what_is_the_optimal_setup(
            after_transfer.to_simulated_projects(), SimulatedCapabilities.none()
        )

        return result_after.profit - result_before.profit
