from __future__ import annotations

import attrs as a

from .demands import Demands


@a.define(frozen=True)
class DemandsPerStage:
    demands: dict[str, Demands]

    @staticmethod
    def empty() -> DemandsPerStage:
        return DemandsPerStage({})

    def __add__(self, other: DemandsPerStage) -> DemandsPerStage:
        demands = self.demands.copy()
        demands.update(other.demands)
        return DemandsPerStage(demands)
