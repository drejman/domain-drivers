from __future__ import annotations

from typing import ClassVar
from uuid import UUID, uuid4

import attrs as a


@a.define(frozen=True)
class Owner:
    _owner: UUID
    NONE_MAGIC_VALUE: ClassVar[int] = 0

    @property
    def id(self) -> UUID:
        return self._owner

    @classmethod
    def none(cls) -> Owner:
        return Owner(UUID(int=cls.NONE_MAGIC_VALUE))

    @staticmethod
    def new_one() -> Owner:
        return Owner(uuid4())

    def by_none(self) -> bool:
        return self._owner == UUID(int=self.NONE_MAGIC_VALUE)
