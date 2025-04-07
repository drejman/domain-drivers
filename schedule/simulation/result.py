from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, override

import attrs as a
from frozendict import frozendict

if TYPE_CHECKING:
    from collections.abc import Iterable

    from schedule.optimization.result import OptimizationResult

    from .available_resource_capability import (
        AvailableResourceCapability,
    )
    from .simulated_project import SimulatedProject


def freeze_projects(project: Iterable[SimulatedProject]) -> frozenset[SimulatedProject]:
    return frozenset(project)


@a.define(frozen=True)
class SimulationResult:
    profit: Decimal
    chosen_projects: frozenset[SimulatedProject] = a.field(converter=freeze_projects)
    resources_allocated_to_projects: frozendict[SimulatedProject, frozenset[AvailableResourceCapability]]

    @classmethod
    def from_optimization(
        cls,
        optimization_result: OptimizationResult[AvailableResourceCapability],
        simulated_projects: Iterable[SimulatedProject],
    ) -> SimulationResult:
        simulated_projects_lookup = {project.project_id: project for project in simulated_projects}
        chosen_projects = [simulated_projects_lookup[item.name] for item in optimization_result.chosen_items]
        return cls(
            profit=Decimal(optimization_result.profit),
            chosen_projects=chosen_projects,
            resources_allocated_to_projects=frozendict(
                {
                    simulated_projects_lookup[k.name]: frozenset(v)
                    for k, v in optimization_result.item_to_capacities.items()
                }
            ),
        )

    @override
    def __str__(self) -> str:
        return f"Result{{profit={self.profit}, items={self.chosen_projects}}}"
