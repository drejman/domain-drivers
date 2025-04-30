import pytest

from schedule.shared.resource_name import ResourceName
from schedule.sorter import CycleError

from ..stage import Stage
from ..stage_parallelization import StageParallelization


def test_everything_can_be_done_in_parallel_if_there_are_no_dependencies() -> None:
    # given
    stage1 = Stage("Stage1")
    stage2 = Stage("Stage2")

    # when
    sorted_stages = StageParallelization().from_stages(stage1, stage2)

    # then
    assert len(sorted_stages.all) == 1


def test_simple_dependencies() -> None:
    # given
    stage1 = Stage(name="Stage1")
    stage2 = Stage(name="Stage2")
    stage3 = Stage(name="Stage3")
    stage4 = Stage(name="Stage4")
    stage2.depends_on(stage1)
    stage3.depends_on(stage1)
    stage4.depends_on(stage2)

    # when
    sorted_stages = StageParallelization().from_stages(stage1, stage2, stage3, stage4)

    # then
    assert str(sorted_stages) == "Stage1 | Stage2, Stage3 | Stage4"


def test_cant_be_done_when_there_are_circular_dependencies() -> None:
    # given
    stage1 = Stage(name="Stage1")
    stage2 = Stage(name="Stage2")
    stage1.depends_on(stage2)
    stage2.depends_on(stage1)  # circular dependency

    # when
    with pytest.raises(CycleError):
        StageParallelization().from_stages(stage1, stage2)


def test_mixed_dependency_levels() -> None:
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
    sorted_stages = StageParallelization().from_stages(stage1, stage2, stage3, stage4, stage5)

    # then
    assert str(sorted_stages) == "Stage1 | Stage2, Stage3 | Stage4, Stage5"


LEON = ResourceName("Leon")
ERYK = ResourceName("Eryk")
SLAWEK = ResourceName("Sławek")
KUBA = ResourceName("Kuba")


def test_takes_into_account_shared_resources() -> None:
    stage_1 = Stage("Stage1").with_chosen_resource_capabilities(LEON)
    stage_2 = Stage("Stage2").with_chosen_resource_capabilities(ERYK, LEON)
    stage_3 = Stage("Stage3").with_chosen_resource_capabilities(SLAWEK)
    stage_4 = Stage("Stage4").with_chosen_resource_capabilities(SLAWEK, KUBA)

    parallel_stages = StageParallelization().from_stages(stage_1, stage_2, stage_3, stage_4)

    assert str(parallel_stages) in [
        "Stage1, Stage3 | Stage2, Stage4",
        "Stage2, Stage4 | Stage1, Stage3",
    ]
