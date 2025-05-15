from schedule.allocation.project_allocations_id import ProjectAllocationsId

from .cashflow import Cashflow
from .cost import Cost
from .earnings import Earnings
from .income import Income
from .repository.cashflow_repository import CashflowRepository


class CashflowFacade:
    def __init__(self, cash_flow_repository: CashflowRepository) -> None:
        self._cash_flow_repository: CashflowRepository = cash_flow_repository

    def add_income_and_cost(self, project_id: ProjectAllocationsId, income: Income, cost: Cost) -> None:
        try:
            cashflow = self._cash_flow_repository.get(project_id)
            cashflow.income = income
            cashflow.cost = cost
        except self._cash_flow_repository.NotFoundError:
            cashflow = Cashflow(project_id=project_id, income=income, cost=cost)
            self._cash_flow_repository.add(cashflow)

    def find(self, project_id: ProjectAllocationsId) -> Earnings:
        cashflow = self._cash_flow_repository.get(project_id)
        return cashflow.earnings
