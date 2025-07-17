from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import override

from schedule.shared.timeslot import TimeSlot

from .duration_unit import DurationUnit


@dataclass(frozen=True)
class NormalizedSlot(TimeSlot):
    @classmethod
    def from_time_slot(cls, time_slot: TimeSlot, duration_unit: DurationUnit) -> NormalizedSlot:
        normalizer = TimeSlotNormalizer(duration_unit=duration_unit)
        return normalizer.slot_to_normalized_slot(time_slot=time_slot)

    @override
    def __eq__(self, other: object) -> bool:
        return TimeSlot(from_=self.from_, to=self.to) == other

    @override
    def __hash__(self) -> int:
        return hash((self.from_, self.to))


class TimeSlotNormalizer:
    def __init__(self, duration_unit: DurationUnit) -> None:
        self._duration_unit: DurationUnit = duration_unit

    def slot_to_normalized_slot(self, time_slot: TimeSlot) -> NormalizedSlot:
        segment_start = self._normalize_start(time_slot.from_)
        segment_end = self._normalize_end(time_slot.to)
        normalized = NormalizedSlot(segment_start, segment_end)
        minimal_segment = NormalizedSlot(segment_start, segment_start + self._duration_unit.value)
        if normalized.within(minimal_segment):
            return minimal_segment
        return normalized

    def _normalize_start(self, initial_start: datetime) -> datetime:
        closest_segment_start = initial_start.replace(minute=0, second=0, microsecond=0)
        if closest_segment_start + self._duration_unit.value > initial_start:
            return closest_segment_start
        while closest_segment_start < initial_start:
            closest_segment_start += self._duration_unit.value
        return closest_segment_start

    def _normalize_end(self, initial_end: datetime) -> datetime:
        closest_segment_end = initial_end.replace(minute=0, second=0, microsecond=0)
        while initial_end > closest_segment_end:
            closest_segment_end += self._duration_unit.value
        return closest_segment_end
