from __future__ import annotations

import attrs as a

from schedule.shared.timeslot.time_slot import TimeSlot

from .allocations import Allocations
from .demands import Demands
from .project_allocations import ProjectAllocations
from .project_allocations_id import ProjectAllocationsId


@a.frozen
class ProjectsAllocationsSummary:
    time_slots: dict[ProjectAllocationsId, TimeSlot]
    project_allocations: dict[ProjectAllocationsId, Allocations]
    demands: dict[ProjectAllocationsId, Demands]

    @staticmethod
    def of(*all_project_allocations: ProjectAllocations) -> ProjectsAllocationsSummary:
        time_slots = {
            project_allocations.project_id: project_allocations.time_slot
            for project_allocations in all_project_allocations
            if project_allocations.has_time_slot()
        }
        allocations = {
            project_allocations.project_id: project_allocations.allocations
            for project_allocations in all_project_allocations
        }
        demands = {
            project_allocations.project_id: project_allocations.demands
            for project_allocations in all_project_allocations
        }
        return ProjectsAllocationsSummary(time_slots, allocations, demands)
