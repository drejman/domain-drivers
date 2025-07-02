import pytest

from schedule.planning.parallelization.removal_suggestion import StageDependency
from schedule.planning.parallelization.stage import Stage
from schedule.planning.parallelization.stage_parallelization import (
    StageParallelization,
)


@pytest.fixture
def stage_parallelization() -> StageParallelization:
    return StageParallelization()


class TestDependencyRemovalSuggesting:
    def test_suggests_breaking_cycle_in_schedule(self, stage_parallelization: StageParallelization) -> None:
        stage1 = Stage("Stage1")
        stage2 = Stage("Stage2")
        stage3 = Stage("Stage3")
        stage4 = Stage("Stage4")
        stage1 = stage1.depends_on(stage2)
        stage2 = stage2.depends_on(stage3)
        stage4 = stage4.depends_on(stage3)
        stage1 = stage1.depends_on(stage4)
        stage3 = stage3.depends_on(stage1)

        suggestion = stage_parallelization.what_to_remove(stage1, stage2, stage3, stage4)

        assert set(suggestion.dependencies) == {StageDependency(stage3, stage1)}
