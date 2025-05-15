from __future__ import annotations

import attrs as a

from schedule.allocation.project_allocations_id import ProjectAllocationsId

from .cost import Cost
from .earnings import Earnings
from .income import Income


@a.define(slots=False)
class Cashflow:
    project_id: ProjectAllocationsId
    income: Income
    cost: Cost

    @property
    def earnings(self) -> Earnings:
        return self.income - self.cost
