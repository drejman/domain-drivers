from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import attrs as a

from schedule.allocation import AllocatedCapability, ProjectAllocationsId, ProjectsAllocationsSummary
from schedule.allocation.capability_scheduling import AllocatableCapabilityId, AllocatableCapabilitySummary
from schedule.allocation.cashflow import Earnings
from schedule.simulation import Demand as SimulationDemand
from schedule.simulation import Demands as SimulationDemands
from schedule.simulation import ProjectId, SimulatedProject

if TYPE_CHECKING:
    from decimal import Decimal

    from schedule.shared.timeslot import TimeSlot


@a.frozen
class SimulatedProjectAllocations:
    _summary: ProjectsAllocationsSummary
    _earnings: dict[ProjectAllocationsId, Earnings]

    def transfer(
        self,
        project_from: ProjectAllocationsId,
        project_to: ProjectAllocationsId,
        allocated_capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> SimulatedProjectAllocations:
        try:
            allocations_from = self._summary.project_allocations[project_from]
            allocations_to = self._summary.project_allocations[project_to]
        except KeyError:
            return self

        new_allocations_project_from = allocations_from.remove(allocated_capability.allocated_capability_id, for_slot)
        if new_allocations_project_from == allocations_from:
            return self
        self._summary.project_allocations[project_from] = new_allocations_project_from

        new_allocations_project_to = allocations_to.add(
            AllocatedCapability(allocated_capability.allocated_capability_id, allocated_capability.capability, for_slot)
        )
        self._summary.project_allocations[project_to] = new_allocations_project_to

        return SimulatedProjectAllocations(self._summary, self._earnings)

    def transfer_capabilities(
        self,
        project_to: ProjectAllocationsId,
        capability_to_transfer: AllocatableCapabilitySummary,
        for_slot: TimeSlot,
    ) -> SimulatedProjectAllocations:
        project_to_move_from = self._find_project_to_move_from(capability_to_transfer.id, for_slot)
        if project_to_move_from is None:
            return self

        allocated_capability = AllocatedCapability(
            capability_to_transfer.id,
            capability_to_transfer.capabilities,
            capability_to_transfer.time_slot,
        )
        return self.transfer(project_to_move_from, project_to, allocated_capability, for_slot)

    def _find_project_to_move_from(
        self,
        capability_id: AllocatableCapabilityId,
        for_slot: TimeSlot,  # pyright: ignore [reportUnusedParameter]  # noqa: ARG002
        # TODO: check why it's not used  # noqa: FIX002, TD002
    ) -> ProjectAllocationsId | None:
        for (
            project_allocations_id,
            allocations,
        ) in self._summary.project_allocations.items():
            if allocations.find(capability_id) is not None:
                return project_allocations_id
        return None

    def to_simulated_projects(self) -> list[SimulatedProject]:
        def value_getter(earnings: Earnings) -> Decimal:
            return earnings.to_decimal()

        return [
            SimulatedProject(
                ProjectId(project_id.id),
                functools.partial(value_getter, self._earnings[project_id]),
                missing_demands=self._get_missing_demands(project_id),
            )
            for project_id in self._summary.project_allocations
        ]

    def _get_missing_demands(self, project_id: ProjectAllocationsId) -> SimulationDemands:
        allocations = self._summary.project_allocations[project_id]
        all_demands = self._summary.demands[project_id].missing_demands(allocations)
        return SimulationDemands.of(
            [SimulationDemand(demand.capability, demand.time_slot) for demand in all_demands.all]
        )
