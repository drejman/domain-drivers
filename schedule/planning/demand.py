from __future__ import annotations

import attrs as a

from schedule.shared.capability import Capability


@a.define(frozen=True)
class Demand:
    capability: Capability

    @staticmethod
    def for_(capability: Capability) -> Demand:
        return Demand(capability)
