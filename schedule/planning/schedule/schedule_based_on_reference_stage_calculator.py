from collections.abc import Sequence

from schedule.planning.parallelization.parallel_stages import ParallelStages
from schedule.planning.parallelization.parallel_stages_seq import (
    ParallelStagesSequence,
)
from schedule.planning.parallelization.stage import Stage
from schedule.shared.timeslot.time_slot import TimeSlot


class ScheduleBasedOnReferenceStageCalculator:
    def calculate(
        self,
        reference_stage: Stage,
        reference_stage_proposed_time_slot: TimeSlot,
        parallelized_stages: ParallelStagesSequence,
    ) -> dict[str, TimeSlot]:
        reference_stage_index = self._find_reference_stage_index(reference_stage, parallelized_stages.all)
        if reference_stage_index == -1:
            return {}
        schedule_map: dict[str, TimeSlot] = {}
        stages_before_reference = parallelized_stages.all[:reference_stage_index]
        stages_after_reference = parallelized_stages.all[reference_stage_index + 1 :]
        self._calculate_stages_before_critical(
            stages_before_reference, reference_stage_proposed_time_slot, schedule_map
        )
        self._calculate_stages_after_critical(stages_after_reference, reference_stage_proposed_time_slot, schedule_map)
        self._calculate_stages_with_reference_stage(
            parallelized_stages.all[reference_stage_index],
            reference_stage_proposed_time_slot,
            schedule_map,
        )
        return schedule_map

    def _calculate_stages_before_critical(
        self,
        before: Sequence[ParallelStages],
        stage_proposed_time_slot: TimeSlot,
        schedule_map: dict[str, TimeSlot],
    ) -> None:
        current_start = stage_proposed_time_slot.from_
        for current_stages in reversed(before):
            stage_duration = current_stages.duration
            start = current_start - stage_duration
            for stage in current_stages.stages:
                schedule_map[stage.name] = TimeSlot(start, start + stage.duration)

    def _calculate_stages_after_critical(
        self,
        after: Sequence[ParallelStages],
        stage_proposed_time_slot: TimeSlot,
        schedule_map: dict[str, TimeSlot],
    ) -> None:
        current_start = stage_proposed_time_slot.to
        for current_stages in after:
            for stage in current_stages.stages:
                schedule_map[stage.name] = TimeSlot(current_start, current_start + stage.duration)
            current_start += current_stages.duration

    def _calculate_stages_with_reference_stage(
        self,
        stages_with_reference: ParallelStages,
        stage_proposed_time_slot: TimeSlot,
        schedule_map: dict[str, TimeSlot],
    ) -> None:
        current_start = stage_proposed_time_slot.from_
        for stage in stages_with_reference.stages:
            schedule_map[stage.name] = TimeSlot(current_start, current_start + stage.duration)

    def _find_reference_stage_index(self, reference_stage: Stage, stages_in_parallel: Sequence[ParallelStages]) -> int:
        stages_with_the_reference_stage_with_proposed_time_index = -1
        for i, stages in enumerate(stages_in_parallel):
            stages_names = {stage.name for stage in stages.stages}
            if reference_stage.name in stages_names:
                stages_with_the_reference_stage_with_proposed_time_index = i
                break
        return stages_with_the_reference_stage_with_proposed_time_index
