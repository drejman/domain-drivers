import uuid
from collections.abc import Sequence
from typing import overload, override

from sqlalchemy import Boolean, Column, DateTime, Integer, Table, UniqueConstraint, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import composite
from sqlalchemy.sql.functions import func

from schedule.availability.blockade import Blockade
from schedule.availability.grouped_resource_availability import GroupedResourceAvailability
from schedule.availability.owner import Owner
from schedule.availability.resource_availability import ResourceAvailability
from schedule.availability.resource_availability_id import ResourceAvailabilityId
from schedule.availability.resource_id import ResourceId
from schedule.availability.time_blocks.atomic_time_block import AtomicTimeBlock
from schedule.availability.time_blocks.normalized_slot import NormalizedSlot
from schedule.shared.sqla_repository import EmbeddedUUID
from schedule.shared.sqla_repository.mappers import mapper_registry
from schedule.shared.sqla_repository.sqla_repository import SQLAlchemyRepository

availabilities = Table(
    "availabilities",
    mapper_registry.metadata,
    Column("id", EmbeddedUUID[ResourceAvailabilityId], primary_key=True),
    Column("resource_id", EmbeddedUUID[ResourceId], nullable=False),
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
        "_time_block": composite(AtomicTimeBlock, availabilities.c.from_date, availabilities.c.to_date),
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
                self.add_all(model.resource_availabilities)

    def load_all_within_slot(
        self, resource_id: ResourceId, time_slot: NormalizedSlot
    ) -> Sequence[ResourceAvailability]:
        stmt = select(ResourceAvailability).where(
            availabilities.c.resource_id == resource_id,
            availabilities.c.from_date >= time_slot.from_,
            availabilities.c.to_date <= time_slot.to,
        )
        return self._session.execute(stmt).scalars().all()

    def load_by_id(self, resource_availability_id: ResourceAvailabilityId) -> ResourceAvailability:
        stmt = select(ResourceAvailability).where(availabilities.c.id == resource_availability_id)
        availability: ResourceAvailability = self._session.execute(stmt).one()[0]
        return availability

    def load_availabilities_of_random_resources_within(
        self, time_slot: NormalizedSlot, *resource_ids: ResourceId
    ) -> Sequence[ResourceAvailability]:
        # CTE to find resource_ids that have matching availabilities
        available_resources = (
            select(availabilities.c.resource_id)
            .where(
                availabilities.c.resource_id.in_(resource_ids),
                availabilities.c.taken_by == Owner.none().id,
                availabilities.c.from_date >= time_slot.from_,
                availabilities.c.to_date <= time_slot.to,
            )
            .group_by(availabilities.c.resource_id)
            .cte()
        )

        # CTE to select one random resource from those available
        random_resource = (
            select(available_resources.c.resource_id).order_by(func.random()).limit(1).cte("random_resource")
        )

        # Main query joining with the random resource
        stmt = (
            select(ResourceAvailability)
            .select_from(
                availabilities.join(random_resource, availabilities.c.resource_id == random_resource.c.resource_id)
            )
            .where(
                availabilities.c.taken_by == Owner.none().id,
                availabilities.c.from_date >= time_slot.from_,
                availabilities.c.to_date <= time_slot.to,
            )
        )

        return self._session.execute(stmt).scalars().all()

    def expire(self, model: ResourceAvailability | GroupedResourceAvailability) -> None:
        match model:
            case ResourceAvailability():
                self._session.expire(model)
            case GroupedResourceAvailability():
                for obj in model.resource_availabilities:
                    self._session.expire(obj)
