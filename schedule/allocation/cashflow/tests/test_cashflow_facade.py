from typing import Any

from mockito import verify  # pyright: ignore [reportUnknownVariableType, reportMissingTypeStubs]
from mockito.matchers import arg_that  # pyright: ignore [reportUnknownVariableType, reportMissingTypeStubs]

from schedule.allocation.project_allocations_id import ProjectAllocationsId
from schedule.shared.event import EventBus

from ..cashflow_facade import CashflowFacade
from ..cost import Cost
from ..earnings import Earnings
from ..earnings_recalculated_event import EarningsRecalculatedEvent
from ..income import Income


class TestCashflowFacade:
    def test_saves_cashflow(self, cashflow_facade: CashflowFacade) -> None:
        project_id = ProjectAllocationsId.new_one()

        cashflow_facade.add_income_and_cost(project_id, Income(100), Cost(50))

        earnings = cashflow_facade.find(project_id)
        assert earnings == Earnings(50)

    def test_updating_cash_flow_emits_an_event(self, cashflow_facade: CashflowFacade, when: Any) -> None:
        when(EventBus).publish(...)
        project_id = ProjectAllocationsId.new_one()
        income = Income(100)
        cost = Cost(50)

        cashflow_facade.add_income_and_cost(project_id, income, cost)

        verify(EventBus).publish(
            arg_that(lambda event: self._is_earnings_recalculated_event(event, project_id, Earnings(50)))
        )

    def _is_earnings_recalculated_event(self, event: Any, project_id: ProjectAllocationsId, earnings: Earnings) -> Any:
        return (
            isinstance(event, EarningsRecalculatedEvent)
            and event.project_id == project_id
            and event.earnings == earnings
        )
