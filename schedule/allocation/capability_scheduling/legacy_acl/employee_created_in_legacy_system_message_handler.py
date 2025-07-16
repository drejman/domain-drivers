from __future__ import annotations

from schedule.allocation.capability_scheduling import (
    AllocatableResourceId,
    CapabilityScheduler,
)

from . import (
    translate_to_capability_selector,
)
from .employee_data_from_legacy_esb_message import (
    EmployeeDataFromLegacyEsbMessage,
)


class EmployeeCreatedInLegacySystemMessageHandler:
    def __init__(self, capability_scheduler: CapabilityScheduler) -> None:
        self._capability_scheduler: CapabilityScheduler = capability_scheduler

    # subscribe to message bus
    def handle(self, message: EmployeeDataFromLegacyEsbMessage) -> None:
        allocatable_resource_id = AllocatableResourceId(message.resource_id)
        capability_selectors = translate_to_capability_selector.translate(message)
        _ = self._capability_scheduler.schedule_resource_capabilities_for_period(
            allocatable_resource_id, capability_selectors, message.time_slot
        )
