from datetime import UTC, datetime
from uuid import UUID

from schedule.allocation.capability_scheduling import AllocatableCapabilityId
from schedule.availability import AvailabilityFacade, Owner
from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot

from .allocations import Allocations
from .demands import Demands
from .project_allocations import ProjectAllocations
from .project_allocations_id import ProjectAllocationsId
from .projects_allocations_summary import (
    ProjectsAllocationsSummary,
)
from .repository.allocation_sqla_repository import (
    ProjectAllocationsRepository,
)


class AllocationFacade:
    def __init__(
        self,
        project_allocations_repository: ProjectAllocationsRepository,
        availability_facade: AvailabilityFacade,
    ) -> None:
        self._project_allocations_repository: ProjectAllocationsRepository = project_allocations_repository
        self._availability_facade: AvailabilityFacade = availability_facade

    def create_allocation(self, time_slot: TimeSlot, scheduled_demands: Demands) -> ProjectAllocationsId:
        project_id = ProjectAllocationsId.new_one()
        project_allocations = ProjectAllocations(project_id, Allocations.none(), scheduled_demands, time_slot)
        self._project_allocations_repository.add(project_allocations)
        return project_id

    def find_projects_allocations_by_ids(self, *project_ids: ProjectAllocationsId) -> ProjectsAllocationsSummary:
        projects_allocations = self._project_allocations_repository.get_all(ids=list(project_ids))
        return ProjectsAllocationsSummary.of(*projects_allocations)

    def find_all_projects_allocations(self) -> ProjectsAllocationsSummary:
        projects_allocations = self._project_allocations_repository.get_all()
        return ProjectsAllocationsSummary.of(*projects_allocations)

    def allocate_to_project(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
        capability: Capability,
        time_slot: TimeSlot,
    ) -> UUID | None:
        # TODO: add transaction  # noqa: FIX002, TD002
        owner = Owner(project_id.id)
        if (
            self._availability_facade.block(
                resource_id=allocatable_capability_id.to_availability_resource_id(),
                time_slot=time_slot,
                requester=owner,
            )
            is False
        ):
            return None
        allocations = self._project_allocations_repository.get(project_id)
        event = allocations.allocate(allocatable_capability_id, capability, time_slot, datetime.now(tz=UTC))
        return event.allocated_capability_id if event is not None else None

    def release_from_project(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
        time_slot: TimeSlot,
    ) -> bool:
        # TODO: rethink and potentially add transaction  # noqa: FIX002, TD002
        allocations = self._project_allocations_repository.get(project_id)
        event = allocations.release(allocatable_capability_id, time_slot, datetime.now(tz=UTC))
        return event is not None

    def edit_project_dates(self, project_id: ProjectAllocationsId, from_to: TimeSlot) -> None:
        allocations = self._project_allocations_repository.get(project_id)
        _ = allocations.define_slot(from_to, datetime.now(tz=UTC))

    def schedule_project_allocations_demands(self, project_id: ProjectAllocationsId, demands: Demands) -> None:
        try:
            allocations = self._project_allocations_repository.get(project_id)
        except self._project_allocations_repository.NotFoundError:
            allocations = ProjectAllocations.empty(project_id)
        _ = allocations.add_demands(demands, datetime.now(tz=UTC))
        self._project_allocations_repository.add(allocations)
