from collections.abc import Iterable

from schedule.optimization import Item, OptimizationFacade, TotalCapacity, TotalWeight

from .available_resource_capability import AvailableResourceCapability
from .result import SimulationResult
from .simulated_capabilities import SimulatedCapabilities
from .simulated_project import SimulatedProject


class SimulationFacade:
    def __init__(self, optimization_facade: OptimizationFacade) -> None:
        self._optimization_facade: OptimizationFacade = optimization_facade

    def which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
        self,
        projects_simulations: Iterable[SimulatedProject],
        total_capability: SimulatedCapabilities,
    ) -> SimulationResult:
        result = self._optimization_facade.calculate(
            items=self._to_items(projects_simulations),
            total_capacity=self._to_capacity(total_capability),
            loss_function=lambda x: -x.value,
        )
        return SimulationResult.from_optimization(optimization_result=result, simulated_projects=projects_simulations)

    def _to_capacity(self, total_capability: SimulatedCapabilities) -> TotalCapacity[AvailableResourceCapability]:
        return TotalCapacity(list(total_capability.capabilities))

    def _to_items(self, projects_simulations: Iterable[SimulatedProject]) -> list[Item[AvailableResourceCapability]]:
        return [self._to_item(project) for project in projects_simulations]

    def _to_item(self, project: SimulatedProject) -> Item[AvailableResourceCapability]:
        return Item(
            project.project_id,
            float(project.earnings),
            TotalWeight[AvailableResourceCapability].of(*project.missing_demands.all),
        )
