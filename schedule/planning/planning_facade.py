from datetime import date
from typing import final

from schedule.shared.resource_name import ResourceName
from schedule.shared.timeslot import TimeSlot

from .demands import Demands
from .demands_per_stage import DemandsPerStage
from .parallelization.stage import Stage
from .parallelization.stage_parallelization import StageParallelization
from .plan_chosen_resources import PlanChosenResources
from .project import Project
from .project_card import ProjectCard
from .project_id import ProjectId
from .repository.planning_sqla_repository import ProjectRepository
from .schedule.schedule import Schedule


@final
class PlanningFacade:
    def __init__(
        self,
        project_repository: ProjectRepository,
        stage_parallelization: StageParallelization,
        plan_chosen_resources_service: PlanChosenResources,
    ) -> None:
        self._project_repository = project_repository
        self._stage_parallelization = stage_parallelization
        self._plan_chosen_resources_service = plan_chosen_resources_service

    def add_new_project(self, name: str, *stages: Stage) -> ProjectId:
        parallelized_stages = self._stage_parallelization.from_stages(*set(stages))
        project = Project(name, parallelized_stages)
        self._project_repository.add(project)
        return project.id

    def add_demands(self, project_id: ProjectId, demands: Demands) -> None:
        project = self._project_repository.get(project_id)
        project.add_demands(demands)

    def define_demands_per_stage(self, project_id: ProjectId, demands_per_stage: DemandsPerStage) -> None:
        project = self._project_repository.get(project_id)
        project.add_demands_per_stage(demands_per_stage)

    def define_resources_within_dates(
        self,
        project_id: ProjectId,
        chosen_resources: set[ResourceName],
        time_boundaries: TimeSlot,
    ) -> None:
        self._plan_chosen_resources_service.define_resources_within_dates(project_id, chosen_resources, time_boundaries)

    def define_project_stages(self, project_id: ProjectId, *stages: Stage) -> None:
        project = self._project_repository.get(project_id)
        parallelized_stages = self._stage_parallelization.from_stages(*set(stages))
        project.parallelized_stages = parallelized_stages

    def define_start_date(self, project_id: ProjectId, start_date: date) -> None:
        project = self._project_repository.get(project_id)
        project.add_schedule_by_start_date(start_date)

    def define_manual_schedule(self, project_id: ProjectId, schedule: Schedule) -> None:
        project = self._project_repository.get(id=project_id)
        project.add_schedule(schedule)

    def load(self, project_id: ProjectId) -> ProjectCard:
        project = self._project_repository.get(id=project_id)
        return self._to_project_card(project)

    def load_all(self, *project_ids: ProjectId) -> list[ProjectCard]:
        projects = self._project_repository.get_all(ids=list(project_ids))
        return [self._to_project_card(project) for project in projects]

    @staticmethod
    def _to_project_card(project: Project) -> ProjectCard:
        return ProjectCard(
            project_id=project.id,
            name=project.name,
            parallelized_stages=project.parallelized_stages,
            demands=project.all_demands,
            schedule=project.schedule,
            demands_per_stage=project.demands_per_stage,
            needed_resources=project.chosen_resources,
        )
