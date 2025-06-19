from __future__ import annotations

import attrs as a

from schedule.availability.blockade import Blockade
from schedule.availability.owner import Owner
from schedule.availability.resource_availability_id import ResourceAvailabilityId
from schedule.availability.time_blocks.atomic_time_block import AtomicTimeBlock


@a.define(slots=False)
class ResourceAvailability:
    _id: ResourceAvailabilityId
    _resource_id: ResourceAvailabilityId = a.field(eq=False)
    _time_block: AtomicTimeBlock = a.field(eq=False)
    _blockade: Blockade = a.field(factory=Blockade.none, eq=False)
    _version: int = a.field(default=0, eq=False)

    @property
    def id(self) -> ResourceAvailabilityId:
        return self._id

    @property
    def blocked_by(self) -> Owner:
        return self._blockade.taken_by

    def block(self, requester: Owner) -> bool:
        if self._blockade.is_available_for(requester):
            self._blockade = Blockade.owned_by(requester)
            return True
        return False

    def release(self, requester: Owner) -> bool:
        if self._blockade.is_available_for(requester):
            self._blockade = Blockade.none()
            return True
        return False

    def disable(self, requester: Owner) -> bool:
        self._blockade = Blockade.disable(requester)
        return True

    def enable(self, requester: Owner) -> bool:
        if self._blockade.can_be_taken_by(requester):
            self._blockade = Blockade.none()
            return True
        return False

    def is_disabled_by(self, requester: Owner) -> bool:
        return self._blockade.is_disabled_by(requester)

    def is_disabled(self) -> bool:
        return self._blockade.disabled
