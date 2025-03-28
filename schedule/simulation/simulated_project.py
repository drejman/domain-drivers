import attrs as a
from decimal import Decimal

from .demands import Demands
from .project_id import ProjectId


@a.define(frozen=True)
class SimulatedProject:
    project_id: ProjectId
    earnings: Decimal = a.field(hash=False)
    missing_demands: Demands = a.field(hash=False)
