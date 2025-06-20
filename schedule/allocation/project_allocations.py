from __future__ import annotations

from datetime import datetime
from uuid import UUID

import attrs as a

from schedule.availability import ResourceId
from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot

from .allocated_capability import AllocatedCapability
from .allocations import Allocations
from .demands import Demands
from .events import (
    CapabilitiesAllocatedEvent,
    CapabilityReleasedEvent,
    ProjectAllocationScheduledEvent,
    ProjectAllocationsDemandsScheduledEvent,
)
from .project_allocations_id import ProjectAllocationsId


@a.define(slots=False)
class ProjectAllocations:
    _version: int = a.field(init=False, default=1)
    _project_id: ProjectAllocationsId
    _allocations: Allocations
    _demands: Demands
    _time_slot: TimeSlot

    @property
    def allocations(self) -> Allocations:
        return self._allocations

    @property
    def demands(self) -> Demands:
        return self._demands

    @property
    def time_slot(self) -> TimeSlot:
        return self._time_slot

    @property
    def project_id(self) -> ProjectAllocationsId:
        return self._project_id

    @staticmethod
    def empty(project_id: ProjectAllocationsId) -> ProjectAllocations:
        return ProjectAllocations(project_id, Allocations.none(), Demands.none(), TimeSlot.empty())

    @staticmethod
    def with_demands(project_id: ProjectAllocationsId, demands: Demands) -> ProjectAllocations:
        return ProjectAllocations(project_id, Allocations.none(), demands, TimeSlot.empty())

    def allocate(
        self,
        resource_id: ResourceId,
        capability: Capability,
        requested_slot: TimeSlot,
        when: datetime,
    ) -> CapabilitiesAllocatedEvent | None:
        if not self._within_project_time_slot(requested_slot):
            return None

        allocated_capability = AllocatedCapability(
            resource_id=resource_id.id, capability=capability, time_slot=requested_slot
        )
        new_allocations = self._allocations.add(allocated_capability)
        if self._nothing_allocated(new_allocations):
            return None
        self._allocations = new_allocations

        return CapabilitiesAllocatedEvent(
            allocated_capability_id=allocated_capability.allocated_capability_id,
            project_id=self._project_id,
            missing_demands=self._demands.missing_demands(self._allocations),
            occurred_at=when,
        )

    def _nothing_allocated(self, new_allocations: Allocations) -> bool:
        return self._allocations == new_allocations

    def _within_project_time_slot(self, requested_slot: TimeSlot) -> bool:
        if self._time_slot.is_empty():
            return True
        return requested_slot.within(self._time_slot)

    def release(
        self, allocated_capability_id: UUID, time_slot: TimeSlot, when: datetime
    ) -> CapabilityReleasedEvent | None:
        new_allocations = self._allocations.remove(to_remove=allocated_capability_id, time_slot=time_slot)
        if self._nothing_released(new_allocations):
            return None
        self._allocations = new_allocations
        return CapabilityReleasedEvent(
            project_id=self._project_id, missing_demands=self.missing_demands(), occurred_at=when
        )

    def _nothing_released(self, new_allocations: Allocations) -> bool:
        return new_allocations == self._allocations

    def missing_demands(self) -> Demands:
        return self._demands.missing_demands(self._allocations)

    def has_time_slot(self) -> bool:
        return not self._time_slot.is_empty()

    def add_demands(self, demands: Demands, when: datetime) -> ProjectAllocationsDemandsScheduledEvent:
        self._demands = self._demands.with_new(demands)
        return ProjectAllocationsDemandsScheduledEvent(
            project_id=self._project_id, missing_demands=self.missing_demands(), occurred_at=when
        )

    def define_slot(self, slot: TimeSlot, when: datetime) -> ProjectAllocationScheduledEvent:
        self._time_slot = slot
        return ProjectAllocationScheduledEvent(project_id=self._project_id, from_to=self._time_slot, occurred_at=when)
