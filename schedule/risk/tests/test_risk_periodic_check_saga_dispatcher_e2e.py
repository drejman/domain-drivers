from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta
from typing import Final
from unittest.mock import Mock
from uuid import uuid4

import pytest
import time_machine
from lagom import Container

from schedule.allocation.allocation_facade import AllocationFacade
from schedule.allocation.capability_scheduling import AllocatableCapabilityId
from schedule.allocation.cashflow.cashflow_facade import CashflowFacade
from schedule.allocation.cashflow.cost import Cost
from schedule.allocation.cashflow.earnings import Earnings
from schedule.allocation.cashflow.earnings_recalculated_event import EarningsRecalculatedEvent
from schedule.allocation.cashflow.income import Income
from schedule.allocation.demand import Demand
from schedule.allocation.demands import Demands
from schedule.allocation.events import (
    CapabilitiesAllocatedEvent,
    ProjectAllocationScheduledEvent,
    ProjectAllocationsDemandsScheduledEvent,
)
from schedule.allocation.project_allocations_id import ProjectAllocationsId
from schedule.availability.owner import Owner
from schedule.availability.resource_id import ResourceId
from schedule.availability.resource_taken_over_event import ResourceTakenOverEvent
from schedule.resource import ResourceFacade
from schedule.resource.employee.seniority import Seniority
from schedule.resource_scheduling.resouce_scheduling_facade import ResourceSchedulingFacade
from schedule.shared.capability.capability import Capability
from schedule.shared.event.tests.timeout import timeout
from schedule.shared.timeslot.time_slot import TimeSlot

from ...shared.utcnow import utcnow
from ..risk_periodic_check_saga_dispatcher import (
    RiskPeriodicCheckSagaDispatcher,
)
from ..risk_push_notification import RiskPushNotification


@pytest.fixture
def risk_push_notification_mock() -> Mock:
    return Mock(spec_set=RiskPushNotification)


@pytest.fixture(autouse=True)
def configure_risk_notification_mock(risk_push_notification_mock: Mock, container: Container) -> None:
    container[RiskPushNotification] = risk_push_notification_mock


@pytest.fixture
def risk_saga_dispatcher(container: Container) -> RiskPeriodicCheckSagaDispatcher:
    return container.resolve(RiskPeriodicCheckSagaDispatcher)


class TestRiskPeriodicCheckSagaDispatcherE2E:
    ONE_DAY_LONG: Final = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    PROJECT_DATES: Final = TimeSlot(
        utcnow(),
        utcnow() + timedelta(days=20),
    )

    @pytest.fixture(autouse=True)
    def setup(
        self,
        resource_facade: ResourceFacade,
        resource_scheduling_facade: ResourceSchedulingFacade,
        allocation_facade: AllocationFacade,
        risk_saga_dispatcher: RiskPeriodicCheckSagaDispatcher,
        cashflow_facade: CashflowFacade,
    ) -> None:
        self.resource_facade = resource_facade
        self.resource_scheduling_facade = resource_scheduling_facade
        self.allocation_facade = allocation_facade
        self.risk_saga_dispatcher = risk_saga_dispatcher
        self.cashflow_facade = cashflow_facade

    def test_informs_about_demand_satisfied(self, risk_push_notification_mock: Mock) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduledEvent(project_id, Demands.of(java_one_day_demand), utcnow)
        )

        event = CapabilitiesAllocatedEvent(uuid4(), project_id, Demands.none(), utcnow)
        self.risk_saga_dispatcher.handle_capabilities_allocated(event)

        risk_push_notification_mock.notify_demands_satisfied.assert_called_once_with(project_id)

    def test_informs_about_potential_risk_when_resource_taken_over(self, risk_push_notification_mock: Mock) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduledEvent(project_id, Demands.of(java_one_day_demand), utcnow)
        )
        self.risk_saga_dispatcher.handle_capabilities_allocated(
            CapabilitiesAllocatedEvent(uuid4(), project_id, Demands.none(), utcnow)
        )
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduledEvent(project_id, self.PROJECT_DATES, utcnow)
        )

        risk_push_notification_mock.reset_mock()
        with self._days_before_deadline(100):
            event = ResourceTakenOverEvent(
                ResourceId.new_one(),
                {Owner(project_id.id)},
                self.ONE_DAY_LONG,
            )
            self.risk_saga_dispatcher.handle_resource_taken_over(event)

        risk_push_notification_mock.notify_about_possible_risk.assert_called_once_with(project_id)

    def test_does_nothing_when_resource_taken_from_unknown_project(self, risk_push_notification_mock: Mock) -> None:
        unknown_project_id = ProjectAllocationsId.new_one()

        event = ResourceTakenOverEvent(
            ResourceId.new_one(),
            {Owner(unknown_project_id.id)},
            self.ONE_DAY_LONG,
            utcnow,
        )
        self.risk_saga_dispatcher.handle_resource_taken_over(event)

        assert len(risk_push_notification_mock.mock_calls) == 0

    def test_periodic_check_does_nothing_when_not_too_close_to_deadline_and_demands_not_satisfied(
        self, risk_push_notification_mock: Mock
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduledEvent(project_id, Demands.of(java_one_day_demand), utcnow())
        )
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduledEvent(project_id, self.PROJECT_DATES)
        )

        with self._days_before_deadline(100):
            self.risk_saga_dispatcher.handle_periodic_check()

        assert len(risk_push_notification_mock.mock_calls) == 0

    def test_periodic_check_does_nothing_when_close_to_deadline_and_demands_satisfied(
        self, risk_push_notification_mock: Mock
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR-UNIQUE")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduledEvent(project_id, Demands.of(java_one_day_demand), utcnow())
        )
        self.risk_saga_dispatcher.handle_earnings_recalculated(
            EarningsRecalculatedEvent(project_id, Earnings(10), utcnow())
        )
        self.risk_saga_dispatcher.handle_capabilities_allocated(
            CapabilitiesAllocatedEvent(uuid4(), project_id, Demands.none(), utcnow())
        )
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduledEvent(project_id, self.PROJECT_DATES, utcnow())
        )

        risk_push_notification_mock.reset_mock()
        with self._days_before_deadline(100):
            self.risk_saga_dispatcher.handle_periodic_check()

        assert len(risk_push_notification_mock.mock_calls) == 0

    def test_find_replacements_when_deadline_is_close(self, risk_push_notification_mock: Mock) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduledEvent(project_id, Demands.of(java_one_day_demand), utcnow())
        )
        self.risk_saga_dispatcher.handle_earnings_recalculated(EarningsRecalculatedEvent(project_id, Earnings(10)))
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduledEvent(project_id, self.PROJECT_DATES)
        )
        employee_id = self._employee_with_skills({java}, self.ONE_DAY_LONG)

        risk_push_notification_mock.reset_mock()
        with self._days_before_deadline(20):
            self.risk_saga_dispatcher.handle_periodic_check()

        assert len(risk_push_notification_mock.notify_about_availability.mock_calls) == 1
        called_with_project_id, available = risk_push_notification_mock.notify_about_availability.mock_calls[0].args
        assert called_with_project_id == project_id
        suggested_capabilities = {ac.id for ac in available[java_one_day_demand].all}
        assert employee_id in suggested_capabilities

    def test_suggest_resources_from_different_projects(self, risk_push_notification_mock: Mock) -> None:
        high_value_project = ProjectAllocationsId.new_one()
        low_value_project = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR-SUPER-UNIQUE")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.allocation_facade.schedule_project_allocations_demands(high_value_project, Demands.of(java_one_day_demand))
        self.cashflow_facade.add_income_and_cost(high_value_project, Income(10000), Cost(10))
        self.allocation_facade.schedule_project_allocations_demands(low_value_project, Demands.of(java_one_day_demand))
        self.cashflow_facade.add_income_and_cost(low_value_project, Income(100), Cost(10))
        employee_id = self._employee_with_skills({java}, self.ONE_DAY_LONG)
        self.allocation_facade.allocate_to_project(low_value_project, employee_id, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduledEvent(high_value_project, self.PROJECT_DATES)
        )

        risk_push_notification_mock.reset_mock()
        self.allocation_facade.edit_project_dates(high_value_project, self.PROJECT_DATES)
        self.allocation_facade.edit_project_dates(low_value_project, self.PROJECT_DATES)
        with self._days_before_deadline(1):
            self.risk_saga_dispatcher.handle_periodic_check()

        def assertions() -> None:
            risk_push_notification_mock.notify_profitable_relocation_found.assert_called_once_with(
                high_value_project, employee_id
            )

        timeout(milliseconds=1000, callable=assertions)

    @contextmanager
    def _days_before_deadline(self, days: int) -> Iterator[None]:
        date_to_set = self.PROJECT_DATES.to - timedelta(days=days)
        with time_machine.travel(date_to_set, tick=False):
            yield

    def _employee_with_skills(self, skills: set[Capability], in_slot: TimeSlot) -> AllocatableCapabilityId:
        staszek = self.resource_facade.add_employee(
            "Staszek", "Staszkowski", Seniority.MID, skills, Capability.permissions()
        )
        allocatable_capability_ids = self.resource_scheduling_facade.schedule_capabilities(staszek, in_slot)
        return allocatable_capability_ids[0]
