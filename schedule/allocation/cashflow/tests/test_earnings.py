from decimal import Decimal
from typing import Final

import pytest

from ..cost import Cost
from ..earnings import Earnings
from ..income import Income


class TestEarnings:
    TEN: Final = Decimal(10)

    @pytest.mark.parametrize(
        ("expected_earnings", "income", "cost"),
        [
            (9, 10, 1),
            (8, 10, 2),
            (7, 10, 3),
            (-70, 100, 170),
        ],
    )
    def test_income_minus_cost(self, expected_earnings: int, income: int, cost: int) -> None:
        assert Income(income) - Cost(cost) == Earnings(expected_earnings)

    @pytest.mark.parametrize(
        ("expected", "left", "right"),
        [
            (True, 10, 9),
            (True, 10, 0),
            (True, 10, -1),
            (False, 10, 10),
            (False, 10, 11),
        ],
    )
    def test_greater_than(self, expected: bool, left: int, right: int) -> None:
        assert (Earnings(left) > Earnings(right)) is expected
