from schedule.parallelization.stage import Stage
from schedule.parallelization.stage_parallelization import StageParallelization


def test_everything_can_be_done_in_parallel_if_there_are_no_dependencies():
    # given
    stage1 = Stage("Stage1")
    stage2 = Stage("Stage2")

    # when
    sorted_stages = StageParallelization().from_stages(stages=[stage1, stage2])

    # then
    assert len(sorted_stages.all) == 1


def test_simple_dependencies():
    # given
    stage1 = Stage(name="Stage1")
    stage2 = Stage(name="Stage2")
    stage3 = Stage(name="Stage3")
    stage4 = Stage(name="Stage4")
    stage2.depends_on(stage1)
    stage3.depends_on(stage1)
    stage4.depends_on(stage2)

    # when
    sorted_stages = StageParallelization().from_stages(
        stages=[stage1, stage2, stage3, stage4]
    )

    # then
    assert str(sorted_stages) == "Stage1 | Stage2, Stage3 | Stage4"


def test_cant_be_done_when_there_are_circular_dependencies():
    # given
    stage1 = Stage(name="Stage1")
    stage2 = Stage(name="Stage2")
    stage1.depends_on(stage2)
    stage2.depends_on(stage1)  # circular dependency

    # when
    sorted_stages = StageParallelization().from_stages(stages=[stage1, stage2])

    # then
    assert len(sorted_stages.all) == 0


def test_mixed_dependency_levels():
    # given
    stage1 = Stage(name="Stage1")
    stage2 = Stage(name="Stage2")
    stage3 = Stage(name="Stage3")
    stage4 = Stage(name="Stage4")
    stage5 = Stage(name="Stage5")

    stage2.depends_on(stage1)
    stage3.depends_on(stage1)
    stage4.depends_on(stage2)
    stage5.depends_on(stage3)

    # when
    sorted_stages = StageParallelization().from_stages(
        stages=[stage1, stage2, stage3, stage4, stage5]
    )

    # then
    assert str(sorted_stages) == "Stage1 | Stage2, Stage3 | Stage4, Stage5"
