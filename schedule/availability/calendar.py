from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

import attrs as a
from frozendict import frozendict

from schedule.shared.timeslot import TimeSlot

from .owner import Owner
from .resource_id import ResourceId

TimeSlots = tuple[TimeSlot, ...]


def _freeze_dict_of_sequences(values: Mapping[Owner, Sequence[TimeSlot]]) -> frozendict[Owner, TimeSlots]:
    return frozendict({k: tuple(v) for k, v in values.items()})


@a.define(frozen=True)
class Calendar:
    resource_id: ResourceId
    calendar: frozendict[Owner, TimeSlots] = a.field(factory=frozendict, converter=_freeze_dict_of_sequences)  # pyright: ignore [reportAssignmentType]

    @staticmethod
    def empty(resource_id: ResourceId) -> Calendar:
        return Calendar(resource_id=resource_id)

    @staticmethod
    def with_available_slots(resource_id: ResourceId, *available_slots: TimeSlot) -> Calendar:
        return Calendar(
            resource_id=resource_id, calendar=cast(Mapping[Owner, Sequence[TimeSlot]], {Owner.none(): available_slots})
        )

    def available_slots(self) -> TimeSlots:
        return self.calendar.get(Owner.none(), tuple())

    def taken_by(self, owner: Owner) -> TimeSlots:
        return self.calendar.get(owner, tuple())
