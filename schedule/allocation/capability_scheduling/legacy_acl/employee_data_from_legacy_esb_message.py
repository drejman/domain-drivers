from __future__ import annotations

from uuid import UUID

import attrs as a

from schedule.shared.timeslot import TimeSlot


@a.frozen
class EmployeeDataFromLegacyEsbMessage:
    resource_id: UUID
    skills_performed_together: tuple[tuple[str, ...], ...]
    exclusive_skills: tuple[str, ...]
    permissions: tuple[str, ...]
    time_slot: TimeSlot
