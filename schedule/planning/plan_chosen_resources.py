from itertools import chain
from typing import final

from schedule.availability import AvailabilityFacade, Calendars, ResourceId
from schedule.planning.events import NeededResourcesChosenEvent
from schedule.shared.event.event_publisher import EventPublisher
from schedule.shared.timeslot import TimeSlot

from .chosen_resources import ChosenResources
from .parallelization.stage import Stage
from .project_id import ProjectId
from .repository.planning_sqla_repository import ProjectRepository
from .schedule import Schedule


@final
class PlanChosenResources:
    def __init__(
        self,
        project_repository: ProjectRepository,
        availability_facade: AvailabilityFacade,
        event_publisher: EventPublisher,
    ) -> None:
        self._project_repository = project_repository
        self._availability_facade = availability_facade
        self._event_publisher = event_publisher

    def define_resources_within_dates(
        self,
        project_id: ProjectId,
        resources: set[ResourceId],
        time_boundaries: TimeSlot,
    ) -> None:
        project = self._project_repository.get(id=project_id)
        chosen_resources = ChosenResources(resources, time_boundaries)
        project.add_chosen_resources(chosen_resources)
        event = NeededResourcesChosenEvent(project_id=project_id, needed_resources=resources, time_slot=time_boundaries)
        self._event_publisher.publish(event)  # TODO: untested event  # noqa: FIX002, TD002

    def adjust_stages_to_resource_availability(
        self, project_id: ProjectId, time_boundaries: TimeSlot, *stages: Stage
    ) -> None:
        needed_resources = set(chain.from_iterable(stage.resources for stage in stages))
        project = self._project_repository.get(id=project_id)
        self.define_resources_within_dates(project_id, needed_resources, time_boundaries)
        needed_resources_calendars = self._availability_facade.load_calendars(
            resource_ids=needed_resources, within=time_boundaries
        )
        schedule = self._create_schedule_adjusting_to_calendars(needed_resources_calendars, *stages)
        project.add_schedule(schedule)

    def _create_schedule_adjusting_to_calendars(
        self, needed_resources_calendars: Calendars, *stages: Stage
    ) -> Schedule:
        return Schedule.based_on_chosen_resource_availability(needed_resources_calendars, list(stages))
