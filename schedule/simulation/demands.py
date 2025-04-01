from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .demand import Demand


def iterable_to_frozenset(demands: Iterable[Demand]) -> frozenset[Demand]:
    return frozenset(demands)


@a.define(frozen=True)
class Demands:
    all: frozenset[Demand] = a.field(converter=iterable_to_frozenset)

    @classmethod
    def of(cls, demands: Iterable[Demand]) -> Demands:
        return Demands(all=demands)
