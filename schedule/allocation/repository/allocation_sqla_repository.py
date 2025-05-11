from sqlalchemy import Column, Integer, Table
from sqlalchemy.orm import synonym

from schedule.shared.sqla_repository import AsJSON, EmbeddedUUID
from schedule.shared.sqla_repository.mappers import mapper_registry
from schedule.shared.sqla_repository.sqla_repository import SQLAlchemyRepository

from ...shared.timeslot import TimeSlot
from ..allocations import Allocations
from ..demands import Demands
from ..project_allocations import ProjectAllocations
from ..project_allocations_id import ProjectAllocationsId

project_allocations = Table(
    "project_allocations",
    mapper_registry.metadata,
    Column("project_id", EmbeddedUUID[ProjectAllocationsId], primary_key=True),
    Column("version", Integer, nullable=False),
    Column("allocations", AsJSON[Allocations]),
    Column("demands", AsJSON[Demands]),
    Column("time_slot", AsJSON[TimeSlot]),
)


_ = mapper_registry.map_imperatively(
    ProjectAllocations,
    project_allocations,
    version_id_col=project_allocations.c.version,
    properties={
        "_project_id": project_allocations.c.project_id,
        "_id": synonym("_project_id"),
        "_version": project_allocations.c.version,
        "_allocations": project_allocations.c.allocations,
        "_demands": project_allocations.c.demands,
        "_time_slot": project_allocations.c.time_slot,
    },
)


class ProjectAllocationsRepository(SQLAlchemyRepository[ProjectAllocations, ProjectAllocationsId]):
    pass
