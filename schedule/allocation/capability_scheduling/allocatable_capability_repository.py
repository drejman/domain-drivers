from datetime import datetime

from sqlalchemy import select

from schedule.shared.sqla_repository import SQLAlchemyRepository

from .allocatable_capability import (
    AllocatableCapability,
)
from .allocatable_capability_id import (
    AllocatableCapabilityId,
)


class AllocatableCapabilityRepository(SQLAlchemyRepository[AllocatableCapability, AllocatableCapabilityId]):
    def find_by_capability_within(
        self,
        name: str,
        type: str,  # noqa: A002
        from_: datetime,
        to: datetime,
    ) -> list[AllocatableCapability]:
        stmt = select(self._type).filter(
            self._type.capability["name"].astext == name,  # pyright: ignore [reportAny]
            self._type.capability["type"].astext == type,  # pyright: ignore [reportAny]
            self._type._from_date <= from_,  # pyright: ignore [reportPrivateUsage]  # noqa: SLF001
            self._type._to_date >= to,  # pyright: ignore [reportPrivateUsage]  # noqa: SLF001
        )
        return list(self._session.execute(stmt).scalars().all())
