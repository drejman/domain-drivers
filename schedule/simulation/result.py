import attrs as a
from frozendict import frozendict

from .available_resource_capability import (
    AvailableResourceCapability,
)
from .simulated_project import SimulatedProject


@a.define(frozen=True)
class Result:
    profit: float
    chosen_projects: frozenset[SimulatedProject]
    resources_allocated_to_projects: frozendict[
        SimulatedProject, frozenset[AvailableResourceCapability]
    ]

    def __str__(self) -> str:
        return f"Result{{profit={self.profit}, items={self.chosen_projects}}}"
