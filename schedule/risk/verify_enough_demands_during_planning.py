from decimal import Decimal
from typing import Final
from uuid import uuid4

from schedule.allocation.capability_scheduling import CapabilitySelector
from schedule.planning import CapabilitiesDemandedEvent, PlanningFacade, ProjectCard
from schedule.resource import ResourceFacade
from schedule.shared.capability import Capability
from schedule.shared.event import EventBus
from schedule.shared.timeslot import TimeSlot
from schedule.simulation import (
    AvailableResourceCapability,
    Demand,
    Demands,
    ProjectId,
    SimulatedCapabilities,
    SimulatedProject,
    SimulationFacade,
)

from .risk_push_notification import RiskPushNotification


@EventBus.has_event_handlers
class VerifyEnoughDemandsDuringPlanning:
    SAME_ARBITRARY_VALUE_FOR_EVERY_PROJECT: Final = Decimal(100)

    def __init__(
        self,
        planning_facade: PlanningFacade,
        simulation_facade: SimulationFacade,
        resource_facade: ResourceFacade,
        risk_push_notification: RiskPushNotification,
    ) -> None:
        self._planning_facade: PlanningFacade = planning_facade
        self._simulation_facade: SimulationFacade = simulation_facade
        self._resource_facade: ResourceFacade = resource_facade
        self._risk_push_notification: RiskPushNotification = risk_push_notification

    @EventBus.async_event_handler
    def handle(self, event: CapabilitiesDemandedEvent) -> None:
        project_summaries = self._planning_facade.load_all()
        all_capabilities = self._resource_facade.find_all_capabilities()
        result = self._not_able_to_handle_all_projects_given_capabilities(project_summaries, all_capabilities)
        if result:
            self._risk_push_notification.notify_about_possible_risk_during_planning(event.project_id, event.demands)

    def _not_able_to_handle_all_projects_given_capabilities(
        self, project_summaries: list[ProjectCard], all_capabilities: list[Capability]
    ) -> bool:
        capabilities = [
            AvailableResourceCapability(
                uuid4(),
                CapabilitySelector.can_just_perform(capability),
                TimeSlot.empty(),
            )
            for capability in all_capabilities
        ]
        simulated_projects = [self._same_priced_simulated_project(summary) for summary in project_summaries]
        result = self._simulation_facade.what_is_the_optimal_setup(
            simulated_projects, SimulatedCapabilities(capabilities)
        )
        return len(result.chosen_projects) != len(project_summaries)

    def _same_priced_simulated_project(self, card: ProjectCard) -> SimulatedProject:
        simulated_demands = [Demand(demand.capability, TimeSlot.empty()) for demand in card.demands.all]
        return SimulatedProject(
            ProjectId(card.project_id.id),
            lambda: self.SAME_ARBITRARY_VALUE_FOR_EVERY_PROJECT,
            Demands(simulated_demands),
        )
