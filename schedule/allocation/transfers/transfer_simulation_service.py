from decimal import Decimal

from schedule.allocation import AllocatedCapability, AllocationFacade, ProjectAllocationsId
from schedule.allocation.capability_scheduling import AllocatableCapabilitySummary
from schedule.allocation.cashflow import CashflowFacade, Earnings
from schedule.shared.timeslot.time_slot import TimeSlot
from schedule.simulation import SimulatedCapabilities, SimulationFacade

from .simulated_project_allocations import SimulatedProjectAllocations


class TransferSimulationService:
    def __init__(
        self, simulation_facade: SimulationFacade, allocation_facade: AllocationFacade, cashflow_facade: CashflowFacade
    ) -> None:
        self._simulation_facade: SimulationFacade = simulation_facade
        self._allocation_facade: AllocationFacade = allocation_facade
        self._cashflow_facade: CashflowFacade = cashflow_facade

    def profit_after_moving_capabilities(
        self,
        project_id: ProjectAllocationsId,
        capability_to_move: AllocatableCapabilitySummary,
        time_slot: TimeSlot,
    ) -> Decimal:
        # cached?
        potential_transfers = SimulatedProjectAllocations(
            self._allocation_facade.find_all_projects_allocations(),
            self._cashflow_facade.find_all(),
        )
        result_before = self._simulation_facade.what_is_the_optimal_setup(
            potential_transfers.to_simulated_projects(), SimulatedCapabilities.none()
        )
        after_transfer = potential_transfers.transfer_capabilities(project_id, capability_to_move, time_slot)
        result_after = self._simulation_facade.what_is_the_optimal_setup(
            after_transfer.to_simulated_projects(), SimulatedCapabilities.none()
        )

        return result_after.profit - result_before.profit

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
