from __future__ import annotations

import math
from datetime import datetime

from schedule.shared.timeslot import TimeSlot

from .duration_unit import DurationUnit
from .normalized_slot import NormalizedSlot


class AtomicTimeBlock(NormalizedSlot):
    @classmethod
    def split(cls, time_slot: TimeSlot, duration_unit: DurationUnit) -> list[AtomicTimeBlock]:
        normalized_slot = NormalizedSlot.from_time_slot(time_slot, duration_unit)
        return cls.from_normalized_time_slot(time_slot=normalized_slot, duration_unit=duration_unit)

    @classmethod
    def from_normalized_time_slot(cls, time_slot: NormalizedSlot, duration_unit: DurationUnit) -> list[AtomicTimeBlock]:
        return TimeSlotDivider(duration_unit=duration_unit).divide_time_slot(time_slot=time_slot)


class TimeSlotDivider:
    def __init__(self, duration_unit: DurationUnit) -> None:
        self._duration_unit: DurationUnit = duration_unit

    def divide_time_slot(self, time_slot: NormalizedSlot) -> list[AtomicTimeBlock]:
        minimal_segment = AtomicTimeBlock(time_slot.from_, time_slot.from_ + self._duration_unit.value)
        if time_slot.within(minimal_segment):
            return [minimal_segment]
        number_of_segments = self._calculate_number_of_segments(time_slot)

        current_start = time_slot.from_
        result: list[AtomicTimeBlock] = []
        for _ in range(number_of_segments):
            current_end = self._calculate_end(current_start, time_slot.to)
            slot = AtomicTimeBlock(current_start, current_end)
            result.append(slot)
            current_start = current_start + self._duration_unit.value
        return result

    def _calculate_number_of_segments(self, time_slot: TimeSlot) -> int:
        return math.ceil(time_slot.duration.total_seconds() / self._duration_unit.value.total_seconds())

    def _calculate_end(self, current_start: datetime, initial_end: datetime) -> datetime:
        return min(current_start + self._duration_unit.value, initial_end)
