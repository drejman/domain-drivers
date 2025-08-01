# pyright: reportUnusedParameter=false
# TODO: missing implementation  # noqa: FIX002, TD002

from schedule.allocation import Demand, ProjectAllocationsId
from schedule.allocation.capability_scheduling import AllocatableCapabilitiesSummary, AllocatableCapabilityId
from schedule.availability import ResourceId
from schedule.planning import Demands, ProjectId
from schedule.shared.timeslot import TimeSlot


class RiskPushNotification:
    def notify_demands_satisfied(self, project_id: ProjectAllocationsId) -> None:
        pass

    def notify_about_availability(
        self,
        project_id: ProjectAllocationsId,
        available: dict[Demand, AllocatableCapabilitiesSummary],
    ) -> None:
        pass

    def notify_profitable_relocation_found(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
    ) -> None:
        pass

    def notify_about_possible_risk(self, project_id: ProjectAllocationsId) -> None:
        pass

    def notify_about_possible_risk_during_planning(self, cause: ProjectId, demands: Demands) -> None:
        pass

    def notify_about_critical_resource_not_available(
        self, cause: ProjectId, critical_resource: ResourceId, time_slot: TimeSlot
    ) -> None:
        pass

    def notify_about_resources_not_available(self, project_id: ProjectId, not_available: set[ResourceId]) -> None:
        pass
