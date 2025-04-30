from typing import final

from schedule.availability import AvailabilityFacade
from schedule.shared.resource_name import ResourceName
from schedule.shared.timeslot import TimeSlot

from .chosen_resources import ChosenResources
from .project_id import ProjectId
from .repository.planning_sqla_repository import ProjectRepository


@final
class PlanChosenResources:
    def __init__(
        self,
        project_repository: ProjectRepository,
        availability_facade: AvailabilityFacade,
    ) -> None:
        self._project_repository = project_repository
        self._availability_facade = availability_facade

    def define_resources_within_dates(
        self,
        project_id: ProjectId,
        resources: set[ResourceName],
        time_boundaries: TimeSlot,
    ) -> None:
        project = self._project_repository.get(id=project_id)
        chosen_resources = ChosenResources(resources, time_boundaries)
        project.add_chosen_resources(chosen_resources)
