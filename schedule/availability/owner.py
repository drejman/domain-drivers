from __future__ import annotations

from uuid import UUID

import attrs as a


@a.define(frozen=True)
class Owner:
    owner: UUID | None

    @staticmethod
    def none() -> Owner:
        return Owner(None)
