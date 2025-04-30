from __future__ import annotations

from typing import override
from uuid import UUID, uuid4

import attrs as a


@a.define(repr=False, frozen=True)
class ProjectId:
    _project_id: UUID = a.field(alias="uuid")

    @property
    def id(self) -> UUID:
        return self._project_id

    @override
    def __repr__(self) -> str:
        return f"ProjectId(UUID(hex='{self._project_id}'))"

    @staticmethod
    def new() -> ProjectId:
        return ProjectId(uuid4())
