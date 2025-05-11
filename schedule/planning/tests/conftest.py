import pytest
from lagom.container import Container

from ..planning_facade import PlanningFacade


@pytest.fixture
def planning_facade(container: Container) -> PlanningFacade:
    return container.resolve(PlanningFacade)
