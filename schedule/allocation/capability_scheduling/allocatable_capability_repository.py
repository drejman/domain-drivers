from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import ColumnElement, and_, cast, func, select
from sqlalchemy.dialects.postgresql import JSONB

from schedule.shared.sqla_repository import SQLAlchemyRepository

from .allocatable_capability import (
    AllocatableCapability,
)
from .allocatable_capability_id import (
    AllocatableCapabilityId,
)
from .allocatable_resource_id import AllocatableResourceId


class AllocatableCapabilityRepository(SQLAlchemyRepository[AllocatableCapability, AllocatableCapabilityId]):
    def find_by_capability_within(
        self, capability_name: str, capability_type: str, from_: datetime, to: datetime
    ) -> Sequence[AllocatableCapability]:
        stmt = select(self._type).where(
            self._time_slot_within(from_, to),
            self._capability_matches(capability_name, capability_type),
        )
        return self._session.execute(stmt).scalars().all()

    def find_by_resource_id_and_capability_and_time_slot(
        self,
        allocatable_resource_id: AllocatableResourceId,
        capability_name: str,
        capability_type: str,
        from_: datetime,
        to: datetime,
    ) -> AllocatableCapability | None:
        stmt = select(self._type).where(
            self._resource_id_matches(allocatable_resource_id),
            self._time_slot_within(from_, to),
            self._capability_matches(capability_name, capability_type),
        )
        return self._session.execute(stmt).scalars().one_or_none()

    def find_by_resource_id_and_time_slot(
        self,
        allocatable_resource_id: AllocatableResourceId,
        from_: datetime,
        to: datetime,
    ) -> list[AllocatableCapability]:
        stmt = select(self._type).where(
            self._resource_id_matches(allocatable_resource_id),
            self._time_slot_within(from_, to),
        )
        return list(self._session.execute(stmt).scalars().all())

    def _capability_matches(self, capability_name: str, capability_type: str) -> ColumnElement[bool]:
        return func.jsonb_path_exists(
            self._type.possible_capabilities,
            "$.capabilities[*] ? (@.name == $name && @.type == $type)",
            cast({"name": capability_name, "type": capability_type}, JSONB),
        )

    def _resource_id_matches(self, allocatable_resource_id: AllocatableResourceId) -> ColumnElement[bool]:
        return self._type.resource_id == allocatable_resource_id

    def _time_slot_within(self, from_: datetime, to: datetime) -> ColumnElement[bool]:
        return and_(self._type._from_date <= from_, self._type._to_date >= to)  # pyright: ignore [reportPrivateUsage]  # noqa: SLF001
