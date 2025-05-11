from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import attrs as a

from schedule.shared.timeslot import TimeSlot

from .allocated_capability import AllocatedCapability

if TYPE_CHECKING:
    from collections.abc import Iterable


def freeze_allocated_capabilites(
    allocated_capabilities: Iterable[AllocatedCapability],
) -> frozenset[AllocatedCapability]:
    return frozenset(allocated_capabilities)


@a.define(frozen=True)
class Allocations:
    all: frozenset[AllocatedCapability] = a.field(converter=freeze_allocated_capabilites)

    @staticmethod
    def none() -> Allocations:
        return Allocations(frozenset())

    def add(self, *allocated_capability: AllocatedCapability) -> Allocations:
        return Allocations(self.all.union(allocated_capability))

    def remove(self, to_remove: UUID, time_slot: TimeSlot) -> Allocations:
        allocated_capability = self.find(to_remove)
        if allocated_capability is None:
            return self
        return self._remove_from_slot(allocated_capability, time_slot)

    def _remove_from_slot(self, allocated_capability: AllocatedCapability, time_slot: TimeSlot) -> Allocations:
        difference = allocated_capability.time_slot.leftover_after_removing_common_with(time_slot)
        leftovers: set[AllocatedCapability] = {
            AllocatedCapability(
                allocated_capability.resource_id,
                allocated_capability.capability,
                leftover,
            )
            for leftover in difference
            if leftover.within(allocated_capability.time_slot)
        }

        return Allocations(all=self.all.difference({allocated_capability}).union(leftovers))

    def find(self, allocated_capability_id: UUID) -> AllocatedCapability | None:
        return next(
            (allocation for allocation in self.all if allocation.allocated_capability_id == allocated_capability_id),
            None,
        )
