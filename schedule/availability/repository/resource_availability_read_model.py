from __future__ import annotations

import uuid
from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime
from typing import NamedTuple, cast

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Integer,
    Select,
    Table,
    UniqueConstraint,
    case,
    func,
    select,
)
from sqlalchemy.orm import Session

from schedule.shared.timeslot.time_slot import TimeSlot

from ...shared.sqla_repository.mappers import read_registry
from ..calendar import Calendar
from ..calendars import Calendars
from ..owner import Owner
from ..resource_id import ResourceId

availabilities = Table(
    "availabilities",
    read_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("resource_id", UUID(as_uuid=True), nullable=False),
    Column("resource_parent_id", UUID(as_uuid=True)),
    Column("version", Integer, nullable=False),
    Column("from_date", DateTime(timezone=True), nullable=False),
    Column("to_date", DateTime(timezone=True), nullable=False),
    Column("taken_by", UUID(as_uuid=True), nullable=False),
    Column("disabled", Boolean, nullable=False),
    UniqueConstraint("resource_id", "from_date", "to_date"),
)


class ResourceAvailabilityReadModel:
    def __init__(self, session: Session) -> None:
        self._session: Session = session

    def load(self, resource_id: ResourceId, within: TimeSlot) -> Calendar:
        calendars = self.load_all({resource_id}, within)
        return calendars.get(resource_id)

    def load_all(self, resource_ids: set[ResourceId], within: TimeSlot) -> Calendars:
        calendars: dict[ResourceId, dict[Owner, list[TimeSlot]]] = defaultdict(lambda: defaultdict(list))

        stmt = self._stmt(resource_ids, within)
        rows: Sequence[ReadModelRow] = cast(Sequence[ReadModelRow], self._session.execute(stmt).all())

        for row in rows:
            key = ResourceId(row.resource_id)
            owner = Owner(row.taken_by)
            loaded_slot = TimeSlot(row.start_date, row.end_date)
            calendars[key][owner].append(loaded_slot)

        return Calendars({resource_id: Calendar(resource_id, calendar) for resource_id, calendar in calendars.items()})

    def _stmt(self, resource_ids: set[ResourceId], within: TimeSlot) -> Select[ReadModelRow]:
        availability_with_lag = (
            select(
                availabilities.c.resource_id,
                availabilities.c.taken_by,
                availabilities.c.from_date,
                availabilities.c.to_date,
                func.coalesce(
                    func.lag(availabilities.c.to_date).over(
                        partition_by=[
                            availabilities.c.resource_id,
                            availabilities.c.taken_by,
                        ],
                        order_by=availabilities.c.from_date,
                    ),
                    availabilities.c.from_date,
                ).label("prev_to_date"),
            )
            .filter(
                availabilities.c.resource_id.in_([resource_id.id for resource_id in resource_ids]),
                availabilities.c.from_date >= within.from_,
                availabilities.c.to_date <= within.to,
            )
            .cte("availability_with_lag")
        )

        grouped_availability = select(
            availability_with_lag.c.resource_id,
            availability_with_lag.c.taken_by,
            availability_with_lag.c.from_date,
            availability_with_lag.c.to_date,
            availability_with_lag.c.prev_to_date,
            case(
                (
                    availability_with_lag.c.from_date == availability_with_lag.c.prev_to_date,
                    0,
                ),
                else_=1,
            ).label("new_group_flag"),
            func.sum(
                case(
                    (
                        availability_with_lag.c.from_date == availability_with_lag.c.prev_to_date,
                        0,
                    ),
                    else_=1,
                )
            )
            .over(
                partition_by=[
                    availability_with_lag.c.resource_id,
                    availability_with_lag.c.taken_by,
                ],
                order_by=availability_with_lag.c.from_date,
            )
            .label("grp"),
        ).cte("grouped_availability")

        stmt = (
            select(
                grouped_availability.c.resource_id,
                grouped_availability.c.taken_by,
                func.min(grouped_availability.c.from_date).label("start_date"),
                func.max(grouped_availability.c.to_date).label("end_date"),
            )
            .group_by(
                grouped_availability.c.resource_id,
                grouped_availability.c.taken_by,
                grouped_availability.c.grp,
            )
            .order_by("start_date")
        )

        return cast(Select[ReadModelRow], stmt)


class ReadModelRow(NamedTuple):
    resource_id: uuid.UUID
    taken_by: uuid.UUID
    start_date: datetime
    end_date: datetime
