from __future__ import annotations

from typing import TYPE_CHECKING, Self

import attrs as a

from .allocations import Allocations

if TYPE_CHECKING:
    from decimal import Decimal

    from schedule.shared.timeslot import TimeSlot

    from .allocated_capability import AllocatedCapability
    from .demands import Demands


@a.define
class Project:
    _demands: Demands
    _earnings: Decimal
    _allocations: Allocations = a.field(factory=Allocations.none)

    @property
    def missing_demands(self) -> Demands:
        return self._demands.missing_demands(self._allocations)

    @property
    def earnings(self) -> Decimal:
        return self._earnings

    def remove(self, capability: AllocatedCapability, for_slot: TimeSlot) -> AllocatedCapability | None:
        to_remove = self._allocations.find(capability.allocated_capability_id)
        if to_remove is None:
            return None

        self._allocations = self._allocations.remove(to_remove.allocated_capability_id, for_slot)
        return to_remove

    def add(self, allocated_capability: AllocatedCapability) -> Self:
        self._allocations = self._allocations.add(allocated_capability)
        return self
