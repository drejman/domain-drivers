from ..stage import Stage
from ..stage_parallelization import StageParallelization


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
    assert repr(sorted_stages) == "Stage1 | Stage2, Stage3 | Stage4"
