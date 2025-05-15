from __future__ import annotations

from decimal import Decimal

import attrs as a

from schedule.allocation.cashflow.cost import Cost
from schedule.allocation.cashflow.earnings import Earnings
from schedule.shared.converters import to_decimal


@a.frozen
class Income:
    _income: Decimal = a.field(converter=to_decimal)

    def __sub__(self, other: Cost) -> Earnings:
        return Earnings(self._income - other.value)
