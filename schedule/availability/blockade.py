from __future__ import annotations

from uuid import UUID

import attrs as a

from schedule.availability.owner import Owner


@a.frozen
class Blockade:
    taken_by: Owner
    disabled: bool

    def __composite_values__(self) -> tuple[UUID, bool]:
        return self.taken_by.id, self.disabled

    @staticmethod
    def none() -> Blockade:
        return Blockade(taken_by=Owner.none(), disabled=False)

    @staticmethod
    def disable(owner: Owner) -> Blockade:
        return Blockade(taken_by=owner, disabled=True)

    @staticmethod
    def owned_by(owner: Owner) -> Blockade:
        return Blockade(taken_by=owner, disabled=False)

    def can_be_taken_by(self, requester: Owner) -> bool:
        return self.taken_by == requester or self.taken_by == Owner.none()

    def is_disabled_by(self, owner: Owner) -> bool:
        return self.disabled and self.taken_by == owner

    def is_available_for(self, requester: Owner) -> bool:
        return self.can_be_taken_by(requester) and not self.disabled
