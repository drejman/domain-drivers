from __future__ import annotations

from datetime import datetime
from functools import singledispatchmethod
from typing import ClassVar

import attrs as a

from schedule.allocation import (
    CapabilitiesAllocatedEvent,
    CapabilityReleasedEvent,
    Demands,
    ProjectAllocationScheduledEvent,
    ProjectAllocationsDemandsScheduledEvent,
    ProjectAllocationsId,
)
from schedule.allocation.cashflow import Earnings, EarningsRecalculatedEvent
from schedule.availability import ResourceTakenOverEvent
from schedule.shared.event import Event

from .risk_periodic_check_saga_id import RiskPeriodicCheckSagaId
from .risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep


@a.define(slots=False)
class RiskPeriodicCheckSaga:
    RISK_THRESHOLD_VALUE: ClassVar[Earnings] = Earnings(1000)
    UPCOMING_DEADLINE_AVAILABILITY_SEARCH: ClassVar[int] = 30
    UPCOMING_DEADLINE_REPLACEMENT_SUGGESTION: ClassVar[int] = 15
    assert UPCOMING_DEADLINE_AVAILABILITY_SEARCH >= UPCOMING_DEADLINE_REPLACEMENT_SUGGESTION  # noqa: S101

    _id: RiskPeriodicCheckSagaId = a.field(factory=RiskPeriodicCheckSagaId.new_one, init=False)
    _project_id: ProjectAllocationsId
    _missing_demands: Demands = a.field(factory=Demands.none)
    _earnings: Earnings = a.field(default=Earnings(0))
    _deadline: datetime | None = a.field(default=None, init=False)

    @property
    def project_id(self) -> ProjectAllocationsId:
        return self._project_id

    @property
    def missing_demands(self) -> Demands:
        return self._missing_demands

    @property
    def earnings(self) -> Earnings:
        return self._earnings

    @property
    def deadline(self) -> datetime | None:
        return self._deadline

    def are_demands_satisfied(self) -> bool:
        return len(self._missing_demands.all) == 0

    @singledispatchmethod
    def handle(self, event: Event) -> RiskPeriodicCheckSagaStep:  # pyright: ignore [reportUnusedParameter]
        raise NotImplementedError

    @handle.register
    def _handle_earnings_recalculated(self, event: EarningsRecalculatedEvent) -> RiskPeriodicCheckSagaStep:
        self._earnings = event.earnings
        return RiskPeriodicCheckSagaStep.DO_NOTHING

    @handle.register
    def _handle_project_allocations_demands_scheduled(
        self, event: ProjectAllocationsDemandsScheduledEvent
    ) -> RiskPeriodicCheckSagaStep:
        self._missing_demands = event.missing_demands
        if self.are_demands_satisfied():
            return RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED
        return RiskPeriodicCheckSagaStep.DO_NOTHING

    @handle.register
    def _handle_project_allocations_scheduled(
        self, event: ProjectAllocationScheduledEvent
    ) -> RiskPeriodicCheckSagaStep:
        self._deadline = event.from_to.to
        return RiskPeriodicCheckSagaStep.DO_NOTHING

    @handle.register
    def _handle_resource_taken_over(self, event: ResourceTakenOverEvent) -> RiskPeriodicCheckSagaStep:
        if self._deadline is not None and event.occurred_at > self._deadline:
            return RiskPeriodicCheckSagaStep.DO_NOTHING
        return RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_POSSIBLE_RISK

    @handle.register
    def _handle_capability_released(self, event: CapabilityReleasedEvent) -> RiskPeriodicCheckSagaStep:
        self._missing_demands = event.missing_demands
        return RiskPeriodicCheckSagaStep.DO_NOTHING

    @handle.register
    def _handle_capabilities_allocated(self, event: CapabilitiesAllocatedEvent) -> RiskPeriodicCheckSagaStep:
        self._missing_demands = event.missing_demands
        if self.are_demands_satisfied():
            return RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED
        return RiskPeriodicCheckSagaStep.DO_NOTHING

    def handle_periodic_check(self, when: datetime) -> RiskPeriodicCheckSagaStep:
        if self._deadline is None or when > self._deadline:
            return RiskPeriodicCheckSagaStep.DO_NOTHING
        # exit early if there is no deadline, or it's already past deadline - there's nothing to check yet from risk PoV

        if self.are_demands_satisfied():
            return RiskPeriodicCheckSagaStep.DO_NOTHING
        # everything if fine - no need to notify

        days_to_deadline = (self._deadline - when).days
        if days_to_deadline > self.UPCOMING_DEADLINE_AVAILABILITY_SEARCH:
            return RiskPeriodicCheckSagaStep.DO_NOTHING
        # it's too early to look for search

        if (
            self.UPCOMING_DEADLINE_AVAILABILITY_SEARCH
            >= days_to_deadline
            > self.UPCOMING_DEADLINE_REPLACEMENT_SUGGESTION
        ):
            return RiskPeriodicCheckSagaStep.FIND_AVAILABLE
        # suggest looking for available resources

        if (
            days_to_deadline <= self.UPCOMING_DEADLINE_REPLACEMENT_SUGGESTION
            and self._earnings >= self.RISK_THRESHOLD_VALUE
        ):
            return RiskPeriodicCheckSagaStep.SUGGEST_REPLACEMENT
        # look for replacement - project is close to deadline and high value

        return RiskPeriodicCheckSagaStep.DO_NOTHING
        # return null value, other options were exhausted
