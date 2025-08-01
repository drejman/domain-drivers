from __future__ import annotations

from typing import override
from uuid import UUID, uuid4

import attrs as a


@a.frozen(str=False)
class RiskPeriodicCheckSagaId:
    _project_risk_saga_id: UUID = a.field(alias="uuid")

    @property
    def id(self) -> UUID:
        return self._project_risk_saga_id

    @staticmethod
    def new_one() -> RiskPeriodicCheckSagaId:
        return RiskPeriodicCheckSagaId(uuid4())

    @override
    def __str__(self) -> str:
        return str(self._project_risk_saga_id)
