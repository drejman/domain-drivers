from decimal import Decimal

import attrs as a

from .demands import Demands
from .project_id import ProjectId


@a.define(frozen=True)
class SimulatedProject:
    _project_id: ProjectId
    earnings: Decimal = a.field(hash=False)
    missing_demands: Demands = a.field(hash=False)

    @property
    def project_id(self) -> str:
        return str(self._project_id)
