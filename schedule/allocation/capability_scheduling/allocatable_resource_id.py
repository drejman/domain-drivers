from __future__ import annotations

from uuid import UUID, uuid4

import attrs as a


@a.frozen
class AllocatableResourceId:
    _resource_id: UUID

    @property
    def id(self) -> UUID:
        return self._resource_id

    @staticmethod
    def new_one() -> AllocatableResourceId:
        return AllocatableResourceId(uuid4())
