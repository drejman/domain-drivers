from __future__ import annotations

from typing import override
from uuid import UUID, uuid4

import attrs as a


@a.define(frozen=True)
class ProjectId:
    _project_id: UUID = a.field(factory=uuid4)

    @staticmethod
    def new() -> ProjectId:
        return ProjectId()

    @override
    def __str__(self) -> str:
        return str(self._project_id)
