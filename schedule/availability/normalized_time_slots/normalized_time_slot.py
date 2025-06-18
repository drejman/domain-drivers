from __future__ import annotations

import math
from datetime import datetime

from schedule.availability.normalized_time_slots.normalize_slot import slot_to_normalized_slot
from schedule.availability.normalized_time_slots.time_quant import TimeQuantumInMinutes
from schedule.shared.timeslot import TimeSlot


class QuantizedTimeSlot(TimeSlot):
    @classmethod
    def from_time_slot(cls, time_slot: TimeSlot, unit: TimeQuantumInMinutes) -> list[QuantizedTimeSlot]:
        normalized_slot = slot_to_normalized_slot(time_slot, unit)
        return quantize_slot(normalized_slot, unit)


def quantize_slot(time_slot: TimeSlot, duration: TimeQuantumInMinutes) -> list[QuantizedTimeSlot]:
    minimal_segment = QuantizedTimeSlot(time_slot.from_, time_slot.from_ + duration.value)
    if time_slot.within(minimal_segment):
        return [minimal_segment]
    number_of_segments = _calculate_number_of_segments(time_slot, duration)

    current_start = time_slot.from_
    result: list[QuantizedTimeSlot] = []
    for _ in range(number_of_segments):
        current_end = _calculate_end(duration, current_start, time_slot.to)
        slot = QuantizedTimeSlot(current_start, current_end)
        result.append(slot)
        current_start = current_start + duration.value
    return result


def _calculate_number_of_segments(time_slot: TimeSlot, duration: TimeQuantumInMinutes) -> int:
    return math.ceil(time_slot.duration.total_seconds() / duration.value.total_seconds())


def _calculate_end(duration: TimeQuantumInMinutes, current_start: datetime, initial_end: datetime) -> datetime:
    return min(current_start + duration.value, initial_end)
