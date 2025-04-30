from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import synonym

from schedule.planning.parallelization.parallel_stages_seq import ParallelStagesSequence
from schedule.planning.schedule import Schedule
from schedule.shared.sqla_repository import AsJSON, EmbeddedUUID
from schedule.shared.sqla_repository.mappers import mapper_registry
from schedule.shared.sqla_repository.sqla_repository import SQLAlchemyRepository

from ..chosen_resources import ChosenResources
from ..demands import Demands
from ..demands_per_stage import DemandsPerStage
from ..project import Project
from ..project_id import ProjectId

projects = Table(
    "projects",
    mapper_registry.metadata,
    Column("id", EmbeddedUUID[ProjectId], primary_key=True),
    Column("version", Integer, nullable=False),
    Column("name", String(), nullable=False),
    Column("parallelized_stages", AsJSON[ParallelStagesSequence]),
    Column("demands_per_stage", AsJSON[DemandsPerStage]),
    Column("all_demands", AsJSON[Demands]),
    Column("chosen_resources", AsJSON[ChosenResources]),
    Column("schedule", AsJSON[Schedule]),
)


_ = mapper_registry.map_imperatively(
    Project,
    projects,
    version_id_col=projects.c.version,
    properties={
        "_id": projects.c.id,
        "_domain_id": synonym("_id"),
        "_version": projects.c.version,
    },
)


class ProjectRepository(SQLAlchemyRepository[Project, ProjectId]):
    pass
