from schedule.allocation.capability_scheduling import (
    AllocatableCapabilityId,
    CapabilityScheduler,
    CapabilitySelector,
)
from schedule.resource import DeviceId, ResourceFacade
from schedule.shared.timeslot.time_slot import TimeSlot

from .to_allocatable_resource_id import to_allocatable_resource_id


class DeviceCapabilitiesScheduler:
    def __init__(
        self,
        resource_facade: ResourceFacade,
        capability_scheduler: CapabilityScheduler,
    ) -> None:
        self._resource_facade: ResourceFacade = resource_facade
        self._capability_scheduler: CapabilityScheduler = capability_scheduler

    def setup_device_capabilities(self, device_id: DeviceId, time_slot: TimeSlot) -> list[AllocatableCapabilityId]:
        summary = self._resource_facade.find_resource_summary(device_id)
        return self._capability_scheduler.schedule_resource_capabilities_for_period(
            to_allocatable_resource_id(device_id),
            [CapabilitySelector.can_perform_all_at_the_time(summary.assets)],
            time_slot,
        )
