from datetime import UTC, datetime

from schedule.allocation import ProjectAllocationsId
from schedule.allocation.cashflow.cashflow_sqla_repository import CashflowRepository
from schedule.shared.event import EventPublisher

from .cashflow import Cashflow
from .cost import Cost
from .earnings import Earnings
from .earnings_recalculated_event import EarningsRecalculatedEvent
from .income import Income


class CashflowFacade:
    def __init__(self, cash_flow_repository: CashflowRepository, event_publisher: EventPublisher) -> None:
        self._cash_flow_repository: CashflowRepository = cash_flow_repository
        self._event_publisher: EventPublisher = event_publisher

    def add_income_and_cost(self, project_id: ProjectAllocationsId, income: Income, cost: Cost) -> None:
        try:
            cashflow = self._cash_flow_repository.get(project_id)
            cashflow.income = income
            cashflow.cost = cost
        except self._cash_flow_repository.NotFoundError:
            cashflow = Cashflow(project_id=project_id, income=income, cost=cost)
            self._cash_flow_repository.add(cashflow)

        event = EarningsRecalculatedEvent(
            project_id=project_id, earnings=cashflow.earnings, occurred_at=datetime.now(tz=UTC)
        )
        self._event_publisher.publish(event)

    def find(self, project_id: ProjectAllocationsId) -> Earnings:
        cashflow = self._cash_flow_repository.get(project_id)
        return cashflow.earnings

    def find_all(self) -> dict[ProjectAllocationsId, Earnings]:
        cashflows = self._cash_flow_repository.get_all()
        return {cashflow.project_id: cashflow.earnings for cashflow in cashflows}
