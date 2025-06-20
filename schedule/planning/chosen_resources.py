from __future__ import annotations

from collections.abc import Iterable

import attrs as a

from schedule.availability import ResourceId
from schedule.shared.timeslot import TimeSlot


def freeze_resources(
    resources: Iterable[ResourceId],
) -> frozenset[ResourceId]:
    return frozenset(resources)


@a.define
class ChosenResources:
    _resources: frozenset[ResourceId] = a.field(converter=freeze_resources)
    _time_slot: TimeSlot

    @staticmethod
    def none() -> ChosenResources:
        return ChosenResources(set(), TimeSlot.empty())
