from collections.abc import Iterable

from schedule.availability import AvailabilityFacade, ResourceId
from schedule.planning import NeededResourcesChosenEvent, ProjectId
from schedule.shared.event import EventBus
from schedule.shared.timeslot.time_slot import TimeSlot

from .risk_push_notification import RiskPushNotification


@EventBus.has_event_handlers
class VerifyNeededResourcesAvailableInTimeSlot:
    def __init__(
        self,
        availability_facade: AvailabilityFacade,
        risk_push_notification: RiskPushNotification,
    ) -> None:
        self._availability_facade: AvailabilityFacade = availability_facade
        self._risk_push_notification: RiskPushNotification = risk_push_notification

    @EventBus.async_event_handler
    def handle(self, event: NeededResourcesChosenEvent) -> None:
        self._notify_about_not_available_resources(event.needed_resources, event.time_slot, event.project_id)

    def _notify_about_not_available_resources(
        self, resource_ids: Iterable[ResourceId], time_slot: TimeSlot, project_id: ProjectId
    ) -> None:
        not_available: set[ResourceId] = set()
        calendars = self._availability_facade.load_calendars(resource_ids, time_slot)
        for resource_id in resource_ids:
            available_slots = calendars.get(resource_id).available_slots()
            if not any(time_slot.within(slot) for slot in available_slots):
                not_available.add(resource_id)
        if len(not_available) > 0:
            self._risk_push_notification.notify_about_resources_not_available(project_id, not_available)
