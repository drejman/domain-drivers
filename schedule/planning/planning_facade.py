from datetime import date
from typing import final

from schedule.availability import ResourceId
from schedule.planning.events import CapabilitiesDemandedEvent, CriticalStagePlannedEvent
from schedule.shared.timeslot import TimeSlot

from ..shared.event import EventPublisher
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
        event_publisher: EventPublisher,
    ) -> None:
        self._project_repository = project_repository
        self._stage_parallelization = stage_parallelization
        self._plan_chosen_resources_service = plan_chosen_resources_service
        self._event_publisher = event_publisher

    def add_new_project(self, name: str, *stages: Stage) -> ProjectId:
        parallelized_stages = self._stage_parallelization.from_stages(*set(stages))
        project = Project(name, parallelized_stages)
        self._project_repository.add(project)
        return project.id

    def add_demands(self, project_id: ProjectId, demands: Demands) -> None:
        project = self._project_repository.get(project_id)
        project.add_demands(demands)
        event = CapabilitiesDemandedEvent(project_id, project.all_demands)
        self._event_publisher.publish(event)

    def define_demands_per_stage(self, project_id: ProjectId, demands_per_stage: DemandsPerStage) -> None:
        project = self._project_repository.get(project_id)
        project.add_demands_per_stage(demands_per_stage)
        event = CapabilitiesDemandedEvent(project_id, project.all_demands)
        self._event_publisher.publish(event)

    def define_resources_within_dates(
        self,
        project_id: ProjectId,
        chosen_resources: set[ResourceId],
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
        ids = None if not project_ids else list(project_ids)
        projects = self._project_repository.get_all(ids=ids)
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

    def plan_critical_stage(self, project_id: ProjectId, critical_stage: Stage, stage_time_slot: TimeSlot) -> None:
        project = self._project_repository.get(id=project_id)
        project.add_schedule_by_critical_stage(critical_stage, stage_time_slot)
        event = CriticalStagePlannedEvent(
            project_id=project_id, stage_time_slot=stage_time_slot, critical_resource_id=None
        )
        self._event_publisher.publish(event)  # TODO: untested event  # noqa: FIX002, TD002

    def plan_critical_stage_with_resource(
        self,
        project_id: ProjectId,
        critical_stage: Stage,
        resource_id: ResourceId,
        stage_time_slot: TimeSlot,
    ) -> None:
        project = self._project_repository.get(id=project_id)
        project.add_schedule_by_critical_stage(critical_stage, stage_time_slot)
        event = CriticalStagePlannedEvent(
            project_id=project_id, stage_time_slot=stage_time_slot, critical_resource_id=resource_id
        )
        self._event_publisher.publish(event)  # TODO: untested event  # noqa: FIX002, TD002

    def adjust_stages_to_resource_availability(
        self, project_id: ProjectId, time_boundaries: TimeSlot, *stages: Stage
    ) -> None:
        self._plan_chosen_resources_service.adjust_stages_to_resource_availability(project_id, time_boundaries, *stages)
