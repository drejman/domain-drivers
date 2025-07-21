from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import attrs as a

from schedule.shared.timeslot import TimeSlot

from .owner import Owner
from .resource_availability import ResourceAvailability
from .resource_availability_id import ResourceAvailabilityId
from .resource_id import ResourceId
from .time_blocks.atomic_time_block import AtomicTimeBlock
from .time_blocks.duration_unit import DurationUnit

if TYPE_CHECKING:
    from attr import Attribute


def _convert_sequence_to_list(resource_availabilities: Sequence[ResourceAvailability]) -> list[ResourceAvailability]:
    return list(resource_availabilities)


def _validate_all_resource_availabilities_have_the_same_resource_id(
    instance: GroupedResourceAvailability,  # pyright: ignore [reportUnusedParameter]  # noqa: ARG001
    attribute: Attribute[list[ResourceAvailability]],  # pyright: ignore [reportUnusedParameter]  # noqa: ARG001
    value: list[ResourceAvailability],
) -> None:
    if not all(resource_availability.resource_id == value[0].resource_id for resource_availability in value):
        msg = "Resource ids do not match"
        raise ValueError(msg)


@a.define
class GroupedResourceAvailability:
    _resource_availabilities: list[ResourceAvailability] = a.field(
        converter=_convert_sequence_to_list, validator=_validate_all_resource_availabilities_have_the_same_resource_id
    )

    @property
    def owners(self) -> frozenset[Owner]:
        return frozenset(ra.blocked_by for ra in self._resource_availabilities)

    @property
    def resource_availabilities(self) -> list[ResourceAvailability]:
        return self._resource_availabilities

    @property
    def resource_id(self) -> ResourceId | None:
        if self.resource_availabilities:
            return self.resource_availabilities[0].resource_id
        return None

    @staticmethod
    def of(
        resource_id: ResourceId,
        time_slot: TimeSlot,
        duration_unit: DurationUnit,
    ) -> GroupedResourceAvailability:
        resource_availabilities = [
            ResourceAvailability(
                ResourceAvailabilityId.new_one(),
                resource_id,
                quantized_time_slot,
            )
            for quantized_time_slot in AtomicTimeBlock.split(time_slot=time_slot, duration_unit=duration_unit)
        ]
        return GroupedResourceAvailability(resource_availabilities)

    def block(self, requester: Owner) -> bool:
        return self._is_not_empty and all(
            resource_availability.block(requester) for resource_availability in self.resource_availabilities
        )

    def blocked_entirely_by(self, owner: Owner) -> bool:
        return all(resource_availability.blocked_by == owner for resource_availability in self._resource_availabilities)

    def __len__(self) -> int:
        return len(self._resource_availabilities)

    def is_disabled_entirely_by(self, owner: Owner) -> bool:
        return all(
            resource_availability.is_disabled_by(requester=owner)
            for resource_availability in self._resource_availabilities
        )

    def disable(self, requester: Owner) -> bool:
        return self._is_not_empty and all(
            resource_availability.disable(requester) for resource_availability in self._resource_availabilities
        )

    def is_entirely_available(self) -> bool:
        return all(resource_availability.blocked_by for resource_availability in self._resource_availabilities)

    def release(self, requester: Owner) -> bool:
        return self._is_not_empty and all(
            resource_availability.release(requester) for resource_availability in self._resource_availabilities
        )

    def find_blocked_by(self, owner: Owner) -> list[ResourceAvailability]:
        return [
            resource_availability
            for resource_availability in self.resource_availabilities
            if resource_availability.blocked_by == owner
        ]

    @property
    def _is_not_empty(self) -> bool:
        # TODO: consider raising exception in case of empty list   # noqa: FIX002, TD002
        #  - what's the point of changing empty availabilities?
        return len(self._resource_availabilities) > 0
