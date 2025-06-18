import uuid
from collections.abc import Sequence
from typing import overload, override

from sqlalchemy import Boolean, Column, DateTime, Integer, Table, UniqueConstraint, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import composite

from schedule.availability.blockade import Blockade
from schedule.availability.grouped_resource_availability import GroupedResourceAvailability
from schedule.availability.normalized_time_slots.normalized_time_slot import QuantizedTimeSlot
from schedule.availability.owner import Owner
from schedule.availability.resource_availability import ResourceAvailability
from schedule.availability.resource_availability_id import ResourceAvailabilityId
from schedule.shared.sqla_repository import EmbeddedUUID
from schedule.shared.sqla_repository.mappers import mapper_registry
from schedule.shared.sqla_repository.sqla_repository import SQLAlchemyRepository
from schedule.shared.timeslot import TimeSlot

availabilities = Table(
    "availabilities",
    mapper_registry.metadata,
    Column("id", EmbeddedUUID[ResourceAvailabilityId], primary_key=True),
    Column("resource_id", EmbeddedUUID[ResourceAvailabilityId], nullable=False),
    Column("from_date", DateTime(timezone=True), nullable=False),
    Column("to_date", DateTime(timezone=True), nullable=False),
    Column("taken_by", UUID(as_uuid=True), nullable=False),
    Column("disabled", Boolean, nullable=False),
    Column("version", Integer, nullable=False),
    UniqueConstraint("resource_id", "from_date", "to_date"),
)


def create_blockade(taken_by: uuid.UUID, disabled: bool) -> Blockade:  # noqa: FBT001
    return Blockade(taken_by=Owner(taken_by), disabled=disabled)


_ = mapper_registry.map_imperatively(
    ResourceAvailability,
    availabilities,
    version_id_col=availabilities.c.version,
    properties={
        "_id": availabilities.c.id,
        "_resource_id": availabilities.c.resource_id,
        "_time_slot": composite(QuantizedTimeSlot, availabilities.c.from_date, availabilities.c.to_date),
        "_blockade": composite(create_blockade, availabilities.c.taken_by, availabilities.c.disabled),
        "_version": availabilities.c.version,
    },
)


class ResourceAvailabilityRepository(SQLAlchemyRepository[ResourceAvailability, ResourceAvailabilityId]):
    @overload
    def add(self, model: ResourceAvailability) -> None: ...

    @overload
    def add(self, model: GroupedResourceAvailability) -> None: ...

    @override
    def add(self, model: ResourceAvailability | GroupedResourceAvailability) -> None:
        match model:
            case ResourceAvailability():
                super().add(model=model)
            case GroupedResourceAvailability():
                self.add_many(model.resource_availabilities)

    def load_all_within_slot(
        self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot
    ) -> Sequence[ResourceAvailability]:
        # TODO: think about better solution once we get to transactions  # noqa: FIX002, TD002
        self._session.expire_all()
        stmt = select(ResourceAvailability).filter(
            availabilities.c.resource_id == resource_id,
            availabilities.c.from_date >= time_slot.from_,
            availabilities.c.to_date <= time_slot.to,
        )
        return self._session.execute(stmt).scalars().all()
