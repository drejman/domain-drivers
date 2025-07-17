from functools import singledispatchmethod

from schedule.allocation.capability_scheduling import AllocatableCapabilityId
from schedule.resource import DeviceId, EmployeeId
from schedule.shared.timeslot import TimeSlot

from .device_capabilities_scheduler import DeviceCapabilitiesScheduler
from .employee_capabilities_scheduler import EmployeeCapabilitiesScheduler

ResourceId = DeviceId | EmployeeId


class ResourceSchedulingFacade:
    def __init__(
        self,
        device_capability_scheduler: DeviceCapabilitiesScheduler,
        employee_capability_scheduler: EmployeeCapabilitiesScheduler,
    ) -> None:
        self._device_capability_scheduler: DeviceCapabilitiesScheduler = device_capability_scheduler
        self._employee_capability_scheduler: EmployeeCapabilitiesScheduler = employee_capability_scheduler

    def schedule_capabilities(self, resource_id: ResourceId, time_slot: TimeSlot) -> list[AllocatableCapabilityId]:
        return self._schedule_capabilities(resource_id, time_slot)

    @singledispatchmethod
    def _schedule_capabilities(self, resource_id: ResourceId) -> list[AllocatableCapabilityId]:
        msg = f"{type(resource_id)} is not a valid ResourceId type: supported are {ResourceId}"
        raise TypeError(msg)

    @_schedule_capabilities.register
    def _schedule_device_capabilities(
        self, resource_id: DeviceId, time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        return self._device_capability_scheduler.setup_device_capabilities(resource_id, time_slot)

    @_schedule_capabilities.register
    def _schedule_employee_capabilities(
        self, resource_id: EmployeeId, time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        return self._employee_capability_scheduler.setup_employee_capabilities(resource_id, time_slot)
