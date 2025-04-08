from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

from .allocated_capability import AllocatedCapability

if TYPE_CHECKING:
    from collections.abc import Iterable

    from schedule.shared.timeslot import TimeSlot


def freeze_allocated_capabilites(
    allocated_capabilites: Iterable[AllocatedCapability],
) -> frozenset[AllocatedCapability]:
    return frozenset(allocated_capabilites)


@a.define(frozen=True)
class Allocations:
    all: frozenset[AllocatedCapability] = a.field(converter=freeze_allocated_capabilites)

    @staticmethod
    def none() -> Allocations:
        return Allocations([])

    def add(self, *allocated_capability: AllocatedCapability) -> Allocations:
        return Allocations(self.all.union(allocated_capability))

    def remove(self, to_remove: AllocatedCapability, time_slot: TimeSlot) -> Allocations:
        allocated_resource = self.find(to_remove)
        if allocated_resource is None:
            return self

        difference_slot = allocated_resource.time_slot.leftover_after_removing_common_with(time_slot)
        leftovers: set[AllocatedCapability] = {
            AllocatedCapability(allocated_resource.resource_id, allocated_resource.capability, leftover)
            for leftover in difference_slot
            if leftover.within(to_remove.time_slot)
        }

        return Allocations(all=self.all.difference({to_remove}).union(leftovers))

    def find(self, capability: AllocatedCapability) -> AllocatedCapability | None:
        return next((allocation for allocation in self.all if allocation == capability), None)
