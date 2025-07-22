from datetime import UTC, datetime
from uuid import UUID

from schedule.allocation.events import CapabilitiesAllocatedEvent
from schedule.availability import AvailabilityFacade, Owner, ResourceId
from schedule.shared.capability.capability import Capability
from schedule.shared.event import EventPublisher
from schedule.shared.timeslot.time_slot import TimeSlot

from .allocations import Allocations
from .capability_scheduling import (
    AllocatableCapabilitiesSummary,
    AllocatableCapabilityId,
    AllocatableCapabilitySummary,
    CapabilityFinder,
    CapabilitySelector,
)
from .demands import Demands
from .events import ProjectAllocationScheduledEvent
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
        capability_finder: CapabilityFinder,
        event_publisher: EventPublisher,
    ) -> None:
        self._project_allocations_repository: ProjectAllocationsRepository = project_allocations_repository
        self._availability_facade: AvailabilityFacade = availability_facade
        self._capability_finder: CapabilityFinder = capability_finder
        self._event_publisher: EventPublisher = event_publisher

    def create_allocation(self, time_slot: TimeSlot, scheduled_demands: Demands) -> ProjectAllocationsId:
        project_id = ProjectAllocationsId.new_one()
        project_allocations = ProjectAllocations(project_id, Allocations.none(), scheduled_demands, time_slot)
        self._project_allocations_repository.add(project_allocations)
        self._event_publisher.publish(ProjectAllocationScheduledEvent(project_id=project_id, from_to=time_slot))
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
        time_slot: TimeSlot,
    ) -> UUID | None:
        # TODO: add transaction  # noqa: FIX002, TD002
        capabilities = self._capability_finder.find_by_id(allocatable_capability_id)
        capability = next(iter(capabilities.all), None)
        if capability is None:
            return None

        if not self._availability_facade.block(
            resource_id=allocatable_capability_id.to_availability_resource_id(),
            time_slot=time_slot,
            requester=Owner(project_id.id),
        ):
            return None

        event = self._allocate(
            project_id=project_id,
            allocatable_capability_id=allocatable_capability_id,
            capability=capability.capabilities,
            time_slot=time_slot,
        )
        return event.allocated_capability_id if event is not None else None

    def allocate_capability_to_project_for_period(
        self,
        project_id: ProjectAllocationsId,
        capability: Capability,
        time_slot: TimeSlot,
    ) -> bool:
        proposed_capabilities = self._capability_finder.find_capabilities(capability=capability, time_slot=time_slot)
        if not proposed_capabilities.all:
            return False

        availability_resource_ids = {
            resource.id.to_availability_resource_id() for resource in proposed_capabilities.all
        }
        chosen = self._availability_facade.block_random_available(
            resource_ids=availability_resource_ids, within=time_slot, requester=Owner(project_id.id)
        )
        if not chosen:
            return False

        to_allocate = self._find_chosen_allocatable_capability(
            proposed_capabilities=proposed_capabilities, chosen=chosen
        )
        if not to_allocate:
            return False

        allocated_event = self._allocate(
            project_id=project_id,
            allocatable_capability_id=to_allocate.id,
            capability=to_allocate.capabilities,
            time_slot=time_slot,
        )
        return allocated_event is not None

    def _allocate(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
        capability: CapabilitySelector,
        time_slot: TimeSlot,
    ) -> CapabilitiesAllocatedEvent | None:
        allocations = self._project_allocations_repository.get(project_id)
        return allocations.allocate(
            allocatable_capability_id=allocatable_capability_id,
            capability=capability,
            requested_slot=time_slot,
            when=datetime.now(tz=UTC),
        )

    def _find_chosen_allocatable_capability(
        self, proposed_capabilities: AllocatableCapabilitiesSummary, chosen: ResourceId
    ) -> AllocatableCapabilitySummary | None:
        matching = [ac for ac in proposed_capabilities.all if ac.id.to_availability_resource_id() == chosen]
        return next(iter(matching), None)

    def release_from_project(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
        time_slot: TimeSlot,
    ) -> bool:
        # Can release not scheduled capability - at least for now.
        # Hence no check to CapabilityFinder
        # TODO: rethink and potentially add transaction  # noqa: FIX002, TD002
        _ = self._availability_facade.release(
            resource_id=allocatable_capability_id.to_availability_resource_id(),
            time_slot=time_slot,
            requester=Owner(project_id.id),
        )
        allocations = self._project_allocations_repository.get(project_id)
        event = allocations.release(allocatable_capability_id, time_slot, datetime.now(tz=UTC))
        return event is not None

    def edit_project_dates(self, project_id: ProjectAllocationsId, from_to: TimeSlot) -> None:
        allocations = self._project_allocations_repository.get(project_id)
        _ = allocations.define_slot(from_to, datetime.now(tz=UTC))
        self._event_publisher.publish(ProjectAllocationScheduledEvent(project_id, from_to))

    def schedule_project_allocations_demands(self, project_id: ProjectAllocationsId, demands: Demands) -> None:
        try:
            allocations = self._project_allocations_repository.get(project_id)
        except self._project_allocations_repository.NotFoundError:
            allocations = ProjectAllocations.empty(project_id)
        event = allocations.add_demands(demands, datetime.now(tz=UTC))
        self._project_allocations_repository.add(allocations)
        self._event_publisher.publish(event)
