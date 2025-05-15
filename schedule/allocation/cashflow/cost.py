from __future__ import annotations

from decimal import Decimal

import attrs as a

from schedule.shared.converters import to_decimal


@a.frozen
class Cost:
    _cost: Decimal = a.field(converter=to_decimal)

    @property
    def value(self) -> Decimal:
        return self._cost
