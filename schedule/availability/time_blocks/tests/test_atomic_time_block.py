from datetime import datetime

import pytest

from schedule.shared.timeslot.time_slot import TimeSlot

from ..atomic_time_block import AtomicTimeBlock
from ..duration_unit import DurationUnit
from ..normalized_slot import NormalizedSlot


class TestSegments:
    @pytest.mark.parametrize("value", [20, 18, 7])
    def test_segment_cannot_be_created_with_number_not_being_multiply_of_15(self, value: int) -> None:
        with pytest.raises(ValueError, match="DurationUnit must be a multiple of"):
            DurationUnit(value)

    @pytest.mark.parametrize("value", [15, 30, 45])
    def test_segment_can_be_created_with_number_being_multiply_of_15(self, value: int) -> None:
        try:
            DurationUnit(value)
        except ValueError:
            pytest.fail("SegmentInMinutes should be created with number being multiply of 15")

    def test_splitting_to_segments_when_there_is_no_leftover(self) -> None:
        start = datetime(2023, 9, 9)
        end = datetime(2023, 9, 9, 1)
        time_slot = TimeSlot(start, end)

        blocks = AtomicTimeBlock.split(time_slot, DurationUnit(15))

        assert blocks == [
            TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 0, 15)),
            TimeSlot(datetime(2023, 9, 9, 0, 15), datetime(2023, 9, 9, 0, 30)),
            TimeSlot(datetime(2023, 9, 9, 0, 30), datetime(2023, 9, 9, 0, 45)),
            TimeSlot(datetime(2023, 9, 9, 0, 45), datetime(2023, 9, 9, 1)),
        ]

    def test_splitting_normalizes_if_chosen_segment_larger_than_passed_slot(
        self,
    ) -> None:
        start = datetime(2023, 9, 9, 0, 10)
        end = datetime(2023, 9, 9, 1)
        time_slot = TimeSlot(start, end)

        blocks = AtomicTimeBlock.split(time_slot, DurationUnit(90))

        assert blocks == [
            TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 1, 30)),
        ]

    def test_normalizing_a_time_slot(self) -> None:
        start = datetime(2023, 9, 9, 0, 10)
        end = datetime(2023, 9, 9, 1)
        time_slot = TimeSlot(start, end)

        slot = NormalizedSlot.from_time_slot(time_slot, DurationUnit(90))

        assert slot == TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 1, 30))

    def test_slots_are_normalized_before_splitting(self) -> None:
        start = datetime(2023, 9, 9, 0, 10)
        end = datetime(2023, 9, 9, 0, 59)
        time_slot = TimeSlot(start, end)

        blocks = AtomicTimeBlock.split(time_slot, DurationUnit(60))

        assert blocks == [
            TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 1)),
        ]

    def test_splitting_into_segments_without_normalization(self) -> None:
        start = datetime(2023, 9, 9)
        end = datetime(2023, 9, 9, 0, 59)
        time_slot = NormalizedSlot(start, end)

        blocks = AtomicTimeBlock.from_normalized_time_slot(time_slot, DurationUnit(30))

        assert blocks == [
            TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 0, 30)),
            TimeSlot(datetime(2023, 9, 9, 0, 30), datetime(2023, 9, 9, 0, 59)),
        ]
