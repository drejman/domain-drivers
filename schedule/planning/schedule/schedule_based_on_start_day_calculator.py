from datetime import date, datetime

from schedule.planning.parallelization.parallel_stages_seq import (
    ParallelStagesSequence,
)
from schedule.shared.timeslot.time_slot import TimeSlot


class ScheduleBasedOnStartDayCalculator:
    def calculate(
        self,
        start_date: date,
        parallelized_stages: ParallelStagesSequence,
    ) -> dict[str, TimeSlot]:
        schedule_dict: dict[str, TimeSlot] = {}
        current_start = datetime.combine(start_date, datetime.min.time())
        for stages in parallelized_stages.all:
            parallelized_stages_end: datetime = current_start
            for stage in stages.stages:
                stage_end = current_start + stage.duration
                schedule_dict[stage.name] = TimeSlot(current_start, stage_end)
                parallelized_stages_end = max(parallelized_stages_end, stage_end)
            current_start = parallelized_stages_end
        return schedule_dict
