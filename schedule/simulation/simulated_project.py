from collections.abc import Callable
from decimal import Decimal

import attrs as a

from .demands import Demands
from .project_id import ProjectId


@a.define(frozen=True)
class SimulatedProject:
    _project_id: ProjectId
    _value_function: Callable[[], Decimal]
    missing_demands: Demands = a.field(hash=False)

    @property
    def project_id(self) -> str:
        return str(self._project_id)

    @property
    def value(self) -> Decimal:
        return self._value_function()
