from __future__ import annotations

from collections.abc import Iterable

import attrs as a

from schedule.shared.resource_name import ResourceName
from schedule.shared.timeslot import TimeSlot


def freeze_resources(
    resources: Iterable[ResourceName],
) -> frozenset[ResourceName]:
    return frozenset(resources)


@a.define
class ChosenResources:
    _resources: frozenset[ResourceName] = a.field(converter=freeze_resources)
    _time_slot: TimeSlot

    @staticmethod
    def none() -> ChosenResources:
        return ChosenResources(set(), TimeSlot.empty())
