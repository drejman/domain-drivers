from __future__ import annotations

from datetime import date

import attrs as a

from schedule.planning.parallelization.parallel_stages_seq import ParallelStagesSequence
from schedule.shared.timeslot import TimeSlot

from .schedule_based_on_start_day_calculator import ScheduleBasedOnStartDayCalculator


@a.define(frozen=True)
class Schedule:
    dates: dict[str, TimeSlot]

    @staticmethod
    def none() -> Schedule:
        return Schedule({})

    @staticmethod
    def based_on_start_day(start_date: date, parallelized_stages: ParallelStagesSequence) -> Schedule:
        schedule_dict = ScheduleBasedOnStartDayCalculator().calculate(
            start_date,
            parallelized_stages,
        )
        return Schedule(schedule_dict)
