from __future__ import annotations

from datetime import date

import attrs as a

from .chosen_resources import ChosenResources
from .demand import Demand
from .demands import Demands
from .demands_per_stage import DemandsPerStage
from .parallelization.parallel_stages_seq import ParallelStagesSequence
from .project_id import ProjectId
from .schedule import Schedule


@a.define(slots=False)
class Project:
    _domain_id: ProjectId = a.field(init=False, factory=ProjectId.new)
    _version: int = a.field(init=False, default=1)
    name: str
    parallelized_stages: ParallelStagesSequence
    demands_per_stage: DemandsPerStage = a.field(init=False, factory=DemandsPerStage.empty)
    all_demands: Demands = a.field(init=False, factory=Demands.none)
    chosen_resources: ChosenResources = a.field(init=False, factory=ChosenResources.none)
    schedule: Schedule = a.field(init=False, factory=Schedule.none)

    @property
    def id(self) -> ProjectId:
        return self._domain_id

    def add_demands(self, demands: Demands) -> None:
        self.all_demands += demands

    def add_demands_per_stage(self, demands_per_stage: DemandsPerStage) -> None:
        self.demands_per_stage += demands_per_stage
        unique_demands: set[Demand] = set()
        for demands in demands_per_stage.demands.values():
            unique_demands.update(demands.all)
        self.add_demands(Demands.of(*unique_demands))

    def add_chosen_resources(self, chosen_resources: ChosenResources) -> None:
        self.chosen_resources = chosen_resources

    def add_schedule_by_start_date(self, start_date: date) -> None:
        self.schedule = Schedule.based_on_start_day(start_date, self.parallelized_stages)

    def add_schedule(self, schedule: Schedule) -> None:
        self.schedule = schedule
