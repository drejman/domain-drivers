from __future__ import annotations

import factory  # type: ignore

from ..demands import Demands
from ..project_id import ProjectId
from ..simulated_project import SimulatedProject


class SimulatedProjectFactory(factory.Factory):  # type: ignore
    class Meta:
        model = SimulatedProject

    class Params:
        value = 0

    project_id = factory.LazyAttribute(lambda _: ProjectId.new())
    value_function = factory.LazyAttribute(lambda o: lambda: o.value)
    missing_demands = factory.LazyAttribute(lambda _: Demands.of([]))
