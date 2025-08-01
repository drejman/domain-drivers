from collections.abc import Iterable, Sequence

from sqlalchemy import Column, DateTime, Integer, Table, select
from sqlalchemy.exc import NoResultFound

from schedule.allocation import Demands, ProjectAllocationsId
from schedule.allocation.cashflow import Earnings
from schedule.shared.sqla_repository import AsJSON, EmbeddedUUID, SQLAlchemyRepository, mapper_registry

from .risk_periodic_check_saga import RiskPeriodicCheckSaga
from .risk_periodic_check_saga_id import RiskPeriodicCheckSagaId

project_risk_sagas = Table(
    "project_risk_sagas",
    mapper_registry.metadata,
    Column("id", EmbeddedUUID[RiskPeriodicCheckSagaId], primary_key=True),
    Column("version", Integer, nullable=False),
    Column("project_id", EmbeddedUUID[ProjectAllocationsId]),
    Column("missing_demands", AsJSON[Demands]),
    Column("earnings", AsJSON[Earnings]),
    Column("deadline", DateTime(timezone=True), nullable=True),
)


_ = mapper_registry.map_imperatively(
    RiskPeriodicCheckSaga,
    project_risk_sagas,
    version_id_col=project_risk_sagas.c.version,
    properties={
        "_id": project_risk_sagas.c.id,
        "_version": project_risk_sagas.c.version,
        "_project_id": project_risk_sagas.c.project_id,
        "_missing_demands": project_risk_sagas.c.missing_demands,
        "_earnings": project_risk_sagas.c.earnings,
        "_deadline": project_risk_sagas.c.deadline,
    },
)


class RiskPeriodicCheckSagaRepository(SQLAlchemyRepository[RiskPeriodicCheckSaga, RiskPeriodicCheckSagaId]):
    def find_by_project_id(self, project_id: ProjectAllocationsId) -> RiskPeriodicCheckSaga:
        stmt = select(self._type).where(project_risk_sagas.c.project_id == project_id)
        try:
            return self._session.execute(stmt).scalar_one()
        except NoResultFound as e:
            raise self.NotFoundError from e

    def find_by_project_id_in(self, project_ids: Iterable[ProjectAllocationsId]) -> Sequence[RiskPeriodicCheckSaga]:
        stmt = select(self._type).where(project_risk_sagas.c.project_id.in_(project_ids))
        return self._session.execute(stmt).scalars().all()
