from __future__ import annotations

from typing import override
from uuid import UUID, uuid4

import attrs as a

from schedule.availability import ResourceId


@a.frozen(repr=False)
class AllocatableCapabilityId:
    _id: UUID = a.field(alias="uuid")

    @property
    def id(self) -> UUID:
        return self._id

    @staticmethod
    def new_one() -> AllocatableCapabilityId:
        return AllocatableCapabilityId(uuid4())

    @staticmethod
    def none() -> AllocatableCapabilityId:
        return AllocatableCapabilityId(UUID(int=0))

    def to_availability_resource_id(self) -> ResourceId:
        return ResourceId(self._id)

    @staticmethod
    def from_availability_resource_id(
        resource_id: ResourceId,
    ) -> AllocatableCapabilityId:
        return AllocatableCapabilityId(resource_id.id)

    @override
    def __repr__(self) -> str:
        return f"AllocatableCapabilityId(UUID(hex='{self._id}'))"

    @override
    def __str__(self) -> str:
        return str(self._id)
