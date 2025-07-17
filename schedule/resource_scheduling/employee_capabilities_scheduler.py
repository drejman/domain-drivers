from schedule.allocation.capability_scheduling import AllocatableCapabilityId, CapabilityScheduler
from schedule.resource import EmployeeId, EmployeeSummary, ResourceFacade, Seniority
from schedule.shared.timeslot import TimeSlot

from .employee_allocation_policy import EmployeeAllocationPolicy
from .to_allocatable_resource_id import to_allocatable_resource_id


class EmployeeCapabilitiesScheduler:
    def __init__(
        self,
        resource_facade: ResourceFacade,
        capability_scheduler: CapabilityScheduler,
    ) -> None:
        self._resource_facade: ResourceFacade = resource_facade
        self._capability_scheduler: CapabilityScheduler = capability_scheduler

    def setup_employee_capabilities(
        self, employee_id: EmployeeId, time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        summary = self._resource_facade.find_resource_summary(employee_id)
        policy = self._find_allocation_policy(summary)
        capabilities = policy.simultaneous_capabilities_of(summary)
        return self._capability_scheduler.schedule_resource_capabilities_for_period(
            to_allocatable_resource_id(employee_id), capabilities, time_slot
        )

    @staticmethod
    def _find_allocation_policy(summary: EmployeeSummary) -> EmployeeAllocationPolicy:
        if summary.seniority == Seniority.LEAD:
            return EmployeeAllocationPolicy.simultaneous(
                EmployeeAllocationPolicy.one_of_skills(),
                EmployeeAllocationPolicy.permissions_in_multiple_projects(3),
            )
        return EmployeeAllocationPolicy.default_policy()
