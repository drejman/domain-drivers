from decimal import Decimal
from uuid import UUID

from schedule.shared.timeslot.time_slot import TimeSlot
from schedule.simulation import SimulatedCapabilities, SimulationFacade

from .allocated_capability import AllocatedCapability
from .projects import Projects


class AllocationFacade:
    def __init__(self, simulation_facade: SimulationFacade) -> None:
        self._simulation_facade: SimulationFacade = simulation_facade

    def check_potential_transfer(
        self,
        projects: Projects,
        project_from: UUID,
        project_to: UUID,
        capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> Decimal:
        # Project rather fetched from a DB.
        result_before = self._simulation_facade.what_is_the_optimal_setup(
            projects.to_simulated_projects(), SimulatedCapabilities.none()
        )

        projects = projects.transfer(project_from, project_to, capability, for_slot)
        result_after = self._simulation_facade.what_is_the_optimal_setup(
            projects.to_simulated_projects(), SimulatedCapabilities.none()
        )

        return result_after.profit - result_before.profit
