from __future__ import annotations

import attrs as a

from .chosen_resources import ChosenResources
from .demands import Demands
from .demands_per_stage import DemandsPerStage
from .parallelization.parallel_stages_seq import ParallelStagesSequence
from .project_id import ProjectId
from .schedule.schedule import Schedule


@a.define(frozen=True)
class ProjectCard:
    project_id: ProjectId
    name: str
    parallelized_stages: ParallelStagesSequence
    demands: Demands
    schedule: Schedule
    demands_per_stage: DemandsPerStage
    needed_resources: ChosenResources
