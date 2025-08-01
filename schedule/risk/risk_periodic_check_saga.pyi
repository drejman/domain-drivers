from datetime import datetime
from functools import singledispatchmethod
from typing import ClassVar

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

from .risk_periodic_check_saga_id import RiskPeriodicCheckSagaId
from .risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep

class RiskPeriodicCheckSaga:
    RISK_THRESHOLD_VALUE: ClassVar[Earnings]
    UPCOMING_DEADLINE_AVAILABILITY_SEARCH: ClassVar[int]
    UPCOMING_DEADLINE_REPLACEMENT_SUGGESTION: ClassVar[int]

    _id: RiskPeriodicCheckSagaId
    _project_id: ProjectAllocationsId
    _missing_demands: Demands
    _earnings: Earnings
    _deadline: datetime | None

    def __init__(
        self, project_id: ProjectAllocationsId, missing_demands: Demands = ..., earnings: Earnings = ...
    ) -> None: ...
    @property
    def project_id(self) -> ProjectAllocationsId: ...
    @property
    def missing_demands(self) -> Demands: ...
    @property
    def earnings(self) -> Earnings: ...
    @property
    def deadline(self) -> datetime | None: ...
    def are_demands_satisfied(self) -> bool: ...
    @singledispatchmethod
    def handle(
        self,
        event: EarningsRecalculatedEvent
        | ProjectAllocationsDemandsScheduledEvent
        | ProjectAllocationScheduledEvent
        | ResourceTakenOverEvent
        | CapabilityReleasedEvent
        | CapabilitiesAllocatedEvent,
    ) -> RiskPeriodicCheckSagaStep: ...
    def handle_periodic_check(self, when: datetime) -> RiskPeriodicCheckSagaStep: ...
