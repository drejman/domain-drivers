from collections.abc import Iterable
from datetime import timedelta

from .stage import Stage
from .stage_parallelization import (
    StageParallelization,
)


def calculate_duration(stages: Iterable[Stage]) -> timedelta:
    parallelized_stages = StageParallelization().from_stages(*stages)
    return sum(
        (parallel_stages.duration for parallel_stages in parallelized_stages.all),
        timedelta(),
    )
