from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

from schedule.simulation.demand import Demand as SimulationDemand
from schedule.simulation.demands import Demands as SimulationDemands
from schedule.simulation.project_id import ProjectId
from schedule.simulation.simulated_project import SimulatedProject

from .allocated_capability import AllocatedCapability

if TYPE_CHECKING:
    from uuid import UUID

    from schedule.shared.timeslot import TimeSlot

    from .project import Project


@a.define
class Projects:
    _projects: dict[UUID, Project]

    def transfer(
        self, project_from: UUID, project_to: UUID, capability: AllocatedCapability, for_slot: TimeSlot
    ) -> Projects:
        try:
            from_ = self._projects[project_from]
            to = self._projects[project_to]
        except KeyError:
            return self

        removed = from_.remove(capability, for_slot)
        if removed is None:
            return self

        _ = to.add(AllocatedCapability(removed.resource_id, removed.capability, for_slot))
        return self

    def to_simulated_projects(self) -> list[SimulatedProject]:
        result: list[SimulatedProject] = []

        for project_id, project in self._projects.items():
            result.append(SimulatedProject(ProjectId(project_id), project.earnings, self._get_missing_demands(project)))

        return result

    def _get_missing_demands(self, project: Project) -> SimulationDemands:
        all_demands = project.missing_demands.all
        return SimulationDemands([SimulationDemand(demand.capability, demand.time_slot) for demand in all_demands])
