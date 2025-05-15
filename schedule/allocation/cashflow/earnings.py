from __future__ import annotations

from decimal import Decimal

import attrs as a

from schedule.shared.converters import to_decimal


@a.frozen(order=True)
class Earnings:
    _earnings: Decimal = a.field(converter=to_decimal)

    def to_decimal(self) -> Decimal:
        return self._earnings
