from __future__ import annotations

from collections.abc import Sequence

import attrs as a

from schedule.availability.normalized_time_slots.normalized_time_slot import QuantizedTimeSlot
from schedule.availability.normalized_time_slots.time_quant import TimeQuantumInMinutes
from schedule.availability.owner import Owner
from schedule.availability.resource_availability import ResourceAvailability
from schedule.availability.resource_availability_id import ResourceAvailabilityId
from schedule.shared.timeslot import TimeSlot


def _convert_sequence_to_list(resource_availabilities: Sequence[ResourceAvailability]) -> list[ResourceAvailability]:
    return list(resource_availabilities)


@a.define
class GroupedResourceAvailability:
    _resource_availabilities: list[ResourceAvailability] = a.field(converter=_convert_sequence_to_list)

    @property
    def resource_availabilities(self) -> list[ResourceAvailability]:
        return self._resource_availabilities

    @staticmethod
    def of(
        resource_id: ResourceAvailabilityId,
        time_slot: TimeSlot,
    ) -> GroupedResourceAvailability:
        resource_availabilities = [
            ResourceAvailability(
                ResourceAvailabilityId.new_one(),
                resource_id,
                quantized_time_slot,
            )
            for quantized_time_slot in QuantizedTimeSlot.from_time_slot(
                time_slot=time_slot, unit=TimeQuantumInMinutes.default_segment()
            )
        ]
        return GroupedResourceAvailability(resource_availabilities)

    def block(self, requester: Owner) -> bool:
        return all(resource_availability.block(requester) for resource_availability in self.resource_availabilities)

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
        return all(resource_availability.disable(requester) for resource_availability in self._resource_availabilities)

    def is_entirely_available(self) -> bool:
        return all(resource_availability.blocked_by for resource_availability in self._resource_availabilities)

    def release(self, requester: Owner) -> bool:
        return all(resource_availability.release(requester) for resource_availability in self._resource_availabilities)

    def find_blocked_by(self, owner: Owner) -> list[ResourceAvailability]:
        return [
            resource_availability
            for resource_availability in self.resource_availabilities
            if resource_availability.blocked_by == owner
        ]
