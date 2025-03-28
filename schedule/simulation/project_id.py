from __future__ import annotations

from uuid import UUID, uuid4
import attrs as a


@a.define(frozen=True)
class ProjectId:
    _project_id: UUID = a.field(factory=uuid4)

    @staticmethod
    def new() -> ProjectId:
        return ProjectId()
