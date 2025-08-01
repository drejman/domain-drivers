from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Final
from uuid import uuid4

import pytest
import time_machine

from schedule.allocation.capability_scheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from schedule.allocation.cashflow.earnings import Earnings
from schedule.allocation.cashflow.earnings_recalculated_event import EarningsRecalculatedEvent
from schedule.allocation.demand import Demand
from schedule.allocation.demands import Demands
from schedule.allocation.events import (
    CapabilitiesAllocatedEvent,
    CapabilityReleasedEvent,
    ProjectAllocationScheduledEvent,
    ProjectAllocationsDemandsScheduledEvent,
)
from schedule.allocation.project_allocations_id import ProjectAllocationsId
from schedule.availability.owner import Owner
from schedule.availability.resource_taken_over_event import ResourceTakenOverEvent
from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot
from schedule.shared.utcnow import utcnow

from ..risk_periodic_check_saga import RiskPeriodicCheckSaga
from ..risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep


class TestRiskPeriodicCheckSaga:
    JAVA: Final = Capability.skill("JAVA")
    ONE_DAY: Final = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    SINGLE_DEMAND: Final = Demands.of(Demand(JAVA, ONE_DAY))
    MANY_DEMANDS: Final = Demands.of(Demand(JAVA, ONE_DAY), Demand(JAVA, ONE_DAY))
    PROJECT_DATES: Final = TimeSlot(
        datetime(2021, 1, 1, tzinfo=UTC),
        datetime(2021, 1, 5, tzinfo=UTC),
    )
    PROJECT_ID: Final = ProjectAllocationsId.new_one()
    CAPABILITY_ID: Final = AllocatableCapabilityId.new_one()

    @pytest.fixture(autouse=True)
    def freeze_time(self) -> Iterator[None]:
        with time_machine.travel(datetime.now(tz=UTC), tick=False):
            yield

    def test_updates_missing_demands_on_saga_creation(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        assert saga.missing_demands == self.SINGLE_DEMAND

    def test_updates_deadline_on_deadline_set(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        _ = saga.handle(ProjectAllocationScheduledEvent(self.PROJECT_ID, self.PROJECT_DATES))

        assert saga.deadline == self.PROJECT_DATES.to

    def test_updates_demands_on_schedule_change(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        next_step = saga.handle(ProjectAllocationsDemandsScheduledEvent(self.PROJECT_ID, self.MANY_DEMANDS))

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING
        assert saga.missing_demands == self.MANY_DEMANDS

    def test_updated_earnings_on_earnings_recalculated(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        next_step = saga.handle(EarningsRecalculatedEvent(self.PROJECT_ID, Earnings(1000)))
        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

        assert saga.earnings == Earnings(1000)

        next_step = saga.handle(EarningsRecalculatedEvent(self.PROJECT_ID, Earnings(900)))

        assert saga.earnings == Earnings(900)
        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_informs_about_demands_satisfied_when_demands_rescheduled(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        _ = saga.handle(EarningsRecalculatedEvent(self.PROJECT_ID, Earnings(1000)))

        still_missing = saga.handle(ProjectAllocationsDemandsScheduledEvent(self.PROJECT_ID, self.SINGLE_DEMAND))
        zero_demands = saga.handle(ProjectAllocationsDemandsScheduledEvent(self.PROJECT_ID, Demands.none()))

        assert still_missing == RiskPeriodicCheckSagaStep.DO_NOTHING
        assert zero_demands == RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED

    def test_notify_about_no_missing_demands_on_capability_allocated(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        next_step = saga.handle(CapabilitiesAllocatedEvent(uuid4(), self.PROJECT_ID, Demands.none()))

        assert next_step == RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED

    def test_no_new_steps_on_capability_allocated_when_missing_demands(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)

        next_step = saga.handle(CapabilitiesAllocatedEvent(uuid4(), self.PROJECT_ID, self.SINGLE_DEMAND))

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_do_nothing_on_resource_taken_over_when_after_deadline(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        _ = saga.handle(CapabilitiesAllocatedEvent(uuid4(), self.PROJECT_ID, self.SINGLE_DEMAND))
        _ = saga.handle(ProjectAllocationScheduledEvent(self.PROJECT_ID, self.PROJECT_DATES))

        after_deadline = self.PROJECT_DATES.to + timedelta(hours=100)
        next_step = saga.handle(
            ResourceTakenOverEvent(
                self.CAPABILITY_ID.to_availability_resource_id(),
                {Owner(self.PROJECT_ID.id)},
                self.ONE_DAY,
                after_deadline,
            )
        )

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_notify_about_risk_on_resource_taken_over_when_before_deadline(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        _ = saga.handle(CapabilitiesAllocatedEvent(uuid4(), self.PROJECT_ID, self.MANY_DEMANDS))
        _ = saga.handle(ProjectAllocationScheduledEvent(self.PROJECT_ID, self.PROJECT_DATES))

        before_deadline = self.PROJECT_DATES.to - timedelta(hours=100)
        next_step = saga.handle(
            ResourceTakenOverEvent(
                self.CAPABILITY_ID.to_availability_resource_id(),
                {Owner(self.PROJECT_ID.id)},
                self.ONE_DAY,
                before_deadline,
            )
        )

        assert next_step == RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_POSSIBLE_RISK

    def test_no_next_step_on_capability_released(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)
        _ = saga.handle(CapabilitiesAllocatedEvent(uuid4(), self.PROJECT_ID, Demands.none()))

        next_step = saga.handle(CapabilityReleasedEvent(self.PROJECT_ID, self.SINGLE_DEMAND))

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_weekly_check_should_result_in_nothing_when_all_demands_satisfied(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)
        _ = saga.handle(EarningsRecalculatedEvent(self.PROJECT_ID, Earnings(1000)))
        _ = saga.handle(CapabilitiesAllocatedEvent(uuid4(), self.PROJECT_ID, Demands.none()))
        _ = saga.handle(ProjectAllocationScheduledEvent(self.PROJECT_ID, self.PROJECT_DATES))

        way_before_deadline = self.PROJECT_DATES.to - timedelta(days=1)
        next_step = saga.handle_periodic_check(way_before_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_handle_weekly_check_should_result_in_nothing_when_after_deadline(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)
        _ = saga.handle(EarningsRecalculatedEvent(self.PROJECT_ID, Earnings(1000)))
        _ = saga.handle(ProjectAllocationScheduledEvent(self.PROJECT_ID, self.PROJECT_DATES))

        way_after_deadline = self.PROJECT_DATES.to + timedelta(days=300)
        next_step = saga.handle_periodic_check(way_after_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_weekly_check_does_nothing_when_no_deadline(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        next_step = saga.handle_periodic_check(utcnow())

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_weekly_check_results_in_nothing_when_not_close_to_deadline_and_demands_unsatisfied(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)
        _ = saga.handle(EarningsRecalculatedEvent(self.PROJECT_ID, Earnings(1000)))
        _ = saga.handle(ProjectAllocationScheduledEvent(self.PROJECT_ID, self.PROJECT_DATES))

        way_before_deadline = self.PROJECT_DATES.to - timedelta(days=300)
        next_step = saga.handle_periodic_check(way_before_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_weekly_check_should_result_in_find_available_when_close_to_deadline_and_demands_not_satisfied(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        _ = saga.handle(EarningsRecalculatedEvent(self.PROJECT_ID, Earnings(1000)))
        _ = saga.handle(ProjectAllocationScheduledEvent(self.PROJECT_ID, self.PROJECT_DATES))

        close_to_deadline = self.PROJECT_DATES.to - timedelta(days=20)
        next_step = saga.handle_periodic_check(close_to_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.FIND_AVAILABLE

    def test_weekly_check_should_result_in_replacement_suggesting_when_high_value_project_really_close_to_deadline_and_demands_not_satisfied(  # noqa: E501
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        _ = saga.handle(EarningsRecalculatedEvent(self.PROJECT_ID, Earnings(1000)))
        _ = saga.handle(ProjectAllocationScheduledEvent(self.PROJECT_ID, self.PROJECT_DATES))

        really_close_to_deadline = self.PROJECT_DATES.to - timedelta(days=2)
        next_step = saga.handle_periodic_check(really_close_to_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.SUGGEST_REPLACEMENT
