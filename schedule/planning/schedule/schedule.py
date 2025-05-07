from __future__ import annotations

from datetime import date

import attrs as a

from schedule.availability import Calendars
from schedule.planning.parallelization.parallel_stages_seq import ParallelStagesSequence
from schedule.shared.timeslot import TimeSlot

from ..parallelization.stage import Stage
from .schedule_based_on_chosen_resources_availability_calculator import (
    ScheduleBasedOnChosenResourcesAvailabilityCalculator,
)
from .schedule_based_on_reference_stage_calculator import ScheduleBasedOnReferenceStageCalculator
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

    @staticmethod
    def based_on_reference_stage_time_slots(
        reference_stage: Stage,
        stage_proposed_time_slot: TimeSlot,
        parallelized_stages: ParallelStagesSequence,
    ) -> Schedule:
        schedule_dict = ScheduleBasedOnReferenceStageCalculator().calculate(
            reference_stage,
            stage_proposed_time_slot,
            parallelized_stages,
        )
        return Schedule(schedule_dict)

    @staticmethod
    def based_on_chosen_resource_availability(chosen_resources_calendars: Calendars, stages: list[Stage]) -> Schedule:
        schedule_dict = ScheduleBasedOnChosenResourcesAvailabilityCalculator().calculate(
            chosen_resources_calendars,
            stages,
        )
        return Schedule(schedule_dict)
