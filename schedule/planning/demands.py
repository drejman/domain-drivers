from __future__ import annotations

import attrs as a

from .demand import Demand


@a.define(frozen=True)
class Demands:
    all: tuple[Demand, ...]

    @staticmethod
    def none() -> Demands:
        return Demands(())

    @staticmethod
    def of(*demands: Demand) -> Demands:
        return Demands(demands)

    def __add__(self, other: Demands) -> Demands:
        return Demands(self.all + other.all)
