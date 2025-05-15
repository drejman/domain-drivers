from sqlalchemy import Column, Integer, Table
from sqlalchemy.orm import synonym

from schedule.allocation.cashflow.cashflow import Cashflow
from schedule.allocation.cashflow.cost import Cost
from schedule.allocation.cashflow.income import Income
from schedule.allocation.project_allocations_id import ProjectAllocationsId
from schedule.shared.sqla_repository import AsJSON, EmbeddedUUID
from schedule.shared.sqla_repository.mappers import mapper_registry
from schedule.shared.sqla_repository.sqla_repository import SQLAlchemyRepository

cashflows = Table(
    "cashflows",
    mapper_registry.metadata,
    Column("project_id", EmbeddedUUID[ProjectAllocationsId], primary_key=True),
    Column("version", Integer, nullable=False),
    Column("income", AsJSON[Income]),
    Column("cost", AsJSON[Cost]),
)


_ = mapper_registry.map_imperatively(
    Cashflow,
    cashflows,
    version_id_col=cashflows.c.version,
    properties={
        "_id": synonym("project_id"),
    },
)


class CashflowRepository(SQLAlchemyRepository[Cashflow, ProjectAllocationsId]):
    pass
