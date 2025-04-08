from collections.abc import Iterable
from decimal import Decimal

from schedule.optimization import Item, OptimizationFacade, TotalCapacity, TotalWeight

from .additional_priced_capability import AdditionalPricedCapability
from .available_resource_capability import AvailableResourceCapability
from .result import SimulationResult
from .simulated_capabilities import SimulatedCapabilities
from .simulated_project import SimulatedProject


class SimulationFacade:
    def __init__(self, optimization_facade: OptimizationFacade) -> None:
        self._optimization_facade: OptimizationFacade = optimization_facade

    def what_is_the_optimal_setup(
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

    def profit_after_buying_new_capability(
        self,
        projects_simulations: Iterable[SimulatedProject],
        capabilities_without_new_one: SimulatedCapabilities,
        new_priced_capability: AdditionalPricedCapability,
    ) -> Decimal:
        result_without_capability = self._optimization_facade.calculate(
            self._to_items(projects_simulations), self._to_capacity(capabilities_without_new_one)
        )

        capabilities_with_new_resource = capabilities_without_new_one.add(
            new_priced_capability.available_resource_capability
        )
        result_with_capability = self._optimization_facade.calculate(
            self._to_items(projects_simulations), self._to_capacity(capabilities_with_new_resource)
        )

        return (result_with_capability.profit - new_priced_capability.value) - result_without_capability.profit

    def _to_capacity(self, total_capability: SimulatedCapabilities) -> TotalCapacity[AvailableResourceCapability]:
        return TotalCapacity(total_capability.capabilities)

    def _to_item(self, project: SimulatedProject) -> Item[AvailableResourceCapability]:
        return Item(
            project.project_id,
            float(project.earnings),
            TotalWeight[AvailableResourceCapability].of(*project.missing_demands.all),
        )

    def _to_items(self, projects_simulations: Iterable[SimulatedProject]) -> list[Item[AvailableResourceCapability]]:
        return [self._to_item(project) for project in projects_simulations]
