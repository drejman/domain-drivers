from __future__ import annotations

from typing import override
from uuid import UUID, uuid4

import attrs as a


@a.define(frozen=True, repr=False)
class ResourceId:
    _resource_id: UUID = a.field(alias="uuid")

    @property
    def id(self) -> UUID:
        return self._resource_id

    @staticmethod
    def new_one() -> ResourceId:
        return ResourceId(uuid4())

    @override
    def __repr__(self) -> str:
        return f"ResourceId(UUID(hex='{self._resource_id}'))"
