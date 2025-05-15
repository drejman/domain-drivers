import pytest
from lagom import Container

from schedule.allocation.project_allocations_id import ProjectAllocationsId

from ..cashflow_facade import CashflowFacade
from ..cost import Cost
from ..earnings import Earnings
from ..income import Income


@pytest.fixture
def cashflow_facade(container: Container) -> CashflowFacade:
    return container.resolve(CashflowFacade)


class TestCashflowFacade:
    def test_saves_cashflow(self, cashflow_facade: CashflowFacade) -> None:
        project_id = ProjectAllocationsId.new_one()

        cashflow_facade.add_income_and_cost(project_id, Income(100), Cost(50))

        earnings = cashflow_facade.find(project_id)
        assert earnings == Earnings(50)
