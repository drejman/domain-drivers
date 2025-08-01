import itertools

from schedule.allocation import (
    CapabilitiesAllocatedEvent,
    Demand,
    Demands,
    ProjectAllocationScheduledEvent,
    ProjectAllocationsDemandsScheduledEvent,
    ProjectAllocationsId,
)
from schedule.allocation.capability_scheduling import AllocatableCapabilitiesSummary, CapabilityFinder
from schedule.allocation.cashflow import EarningsRecalculatedEvent
from schedule.allocation.transfers import TransferSimulationService
from schedule.availability import ResourceTakenOverEvent
from schedule.shared.event import EventBus
from schedule.shared.utcnow import utcnow

from .risk_periodic_check_saga import RiskPeriodicCheckSaga
from .risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep
from .risk_push_notification import RiskPushNotification
from .risk_sqla_repository import RiskPeriodicCheckSagaRepository


@EventBus.has_event_handlers
class RiskPeriodicCheckSagaDispatcher:
    def __init__(
        self,
        state_repository: RiskPeriodicCheckSagaRepository,
        potential_transfers_service: TransferSimulationService,
        capability_finder: CapabilityFinder,
        risk_push_notification: RiskPushNotification,
    ) -> None:
        self._state_repository: RiskPeriodicCheckSagaRepository = state_repository
        self._potential_transfers_service: TransferSimulationService = potential_transfers_service
        self._capability_finder: CapabilityFinder = capability_finder
        self._risk_push_notification: RiskPushNotification = risk_push_notification

    # remember about transactions spanning saga and potential external system
    @EventBus.async_event_handler
    def handle_project_allocations_demands_scheduled(self, event: ProjectAllocationsDemandsScheduledEvent) -> None:
        try:
            saga = self._state_repository.find_by_project_id(event.project_id)
        except self._state_repository.NotFoundError:
            saga = RiskPeriodicCheckSaga(event.project_id, event.missing_demands)

        next_step = saga.handle(event)
        self._state_repository.add(saga)
        self._perform(next_step, saga)

    # remember about transactions spanning saga and potential external system
    @EventBus.async_event_handler
    def handle_earnings_recalculated(self, event: EarningsRecalculatedEvent) -> None:
        try:
            saga = self._state_repository.find_by_project_id(event.project_id)
        except self._state_repository.NotFoundError:
            saga = RiskPeriodicCheckSaga(event.project_id, earnings=event.earnings)

        next_step = saga.handle(event)
        self._state_repository.add(saga)
        self._perform(next_step, saga)

    # remember about transactions spanning saga and potential external system
    @EventBus.async_event_handler
    def handle_project_allocations_scheduled(self, event: ProjectAllocationScheduledEvent) -> None:
        saga = self._state_repository.find_by_project_id(event.project_id)
        next_step = saga.handle(event)
        self._state_repository.add(saga)
        self._perform(next_step, saga)

    @EventBus.async_event_handler
    def handle_capabilities_allocated(self, event: CapabilitiesAllocatedEvent) -> None:
        saga = self._state_repository.find_by_project_id(event.project_id)
        next_step = saga.handle(event)
        self._state_repository.add(saga)
        self._perform(next_step, saga)

    @EventBus.async_event_handler
    def handle_capability_released(self, event: CapabilitiesAllocatedEvent) -> None:
        saga = self._state_repository.find_by_project_id(event.project_id)
        next_step = saga.handle(event)
        self._state_repository.add(saga)
        self._perform(next_step, saga)

    @EventBus.async_event_handler
    def handle_resource_taken_over(self, event: ResourceTakenOverEvent) -> None:
        interested = [ProjectAllocationsId(owner.id) for owner in event.previous_owners]
        # transaction per one saga
        sagas = self._state_repository.find_by_project_id_in(interested)
        for saga in sagas:
            next_step = saga.handle(event)
            self._state_repository.add(saga)
            self._perform(next_step, saga)

    # To be called periodically in some sort of cron job, e.g. Celery Beat
    def handle_periodic_check(self) -> None:
        sagas = self._state_repository.get_all()
        now = utcnow()
        for saga in sagas:
            next_step = saga.handle_periodic_check(now)
            self._state_repository.add(saga)
            self._perform(next_step, saga)

    def _perform(self, next_step: RiskPeriodicCheckSagaStep, saga: RiskPeriodicCheckSaga) -> None:
        if next_step == RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED:
            self._risk_push_notification.notify_demands_satisfied(saga.project_id)
        elif next_step == RiskPeriodicCheckSagaStep.FIND_AVAILABLE:
            self._handle_find_available_for(saga)
        elif next_step == RiskPeriodicCheckSagaStep.DO_NOTHING:
            return
        elif next_step == RiskPeriodicCheckSagaStep.SUGGEST_REPLACEMENT:
            self._handle_simulate_relocation(saga)
        elif next_step == RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_POSSIBLE_RISK:
            self._risk_push_notification.notify_about_possible_risk(saga.project_id)

    def _handle_find_available_for(self, saga: RiskPeriodicCheckSaga) -> None:
        replacements = self._find_available_replacements_for(saga.missing_demands)
        allocatable_capabilities = list(itertools.chain(*[summary.all for summary in replacements.values()]))
        if len(allocatable_capabilities) > 0:
            self._risk_push_notification.notify_about_availability(saga.project_id, replacements)

    def _handle_simulate_relocation(self, saga: RiskPeriodicCheckSaga) -> None:
        all_replacements = self._find_possible_replacements_for(saga.missing_demands)
        for replacements in all_replacements.values():
            for replacement in replacements.all:
                profit_after_moving_capabilities = self._potential_transfers_service.profit_after_moving_capabilities(
                    saga.project_id, replacement, replacement.time_slot
                )
                if profit_after_moving_capabilities > 0:
                    self._risk_push_notification.notify_profitable_relocation_found(saga.project_id, replacement.id)

    def _find_available_replacements_for(self, demands: Demands) -> dict[Demand, AllocatableCapabilitiesSummary]:
        return {
            demand: self._capability_finder.find_available_capabilities(demand.capability, demand.time_slot)
            for demand in demands.all
        }

    def _find_possible_replacements_for(self, demands: Demands) -> dict[Demand, AllocatableCapabilitiesSummary]:
        return {
            demand: self._capability_finder.find_capabilities(demand.capability, demand.time_slot)
            for demand in demands.all
        }
