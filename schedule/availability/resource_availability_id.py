from __future__ import annotations

from uuid import UUID, uuid4

import attrs as a


@a.frozen(order=True)
class ResourceAvailabilityId:
    owner: UUID = a.field(alias="uuid")

    @property
    def id(self) -> UUID:
        return self.owner

    @staticmethod
    def none() -> ResourceAvailabilityId:
        return ResourceAvailabilityId(UUID(int=0))

    @staticmethod
    def new_one() -> ResourceAvailabilityId:
        return ResourceAvailabilityId(uuid4())

    @staticmethod
    def from_str(value: str) -> ResourceAvailabilityId:
        return ResourceAvailabilityId(UUID(hex=value))
