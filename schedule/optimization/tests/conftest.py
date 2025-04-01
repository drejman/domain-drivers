import pytest

from ..optimization_facade import OptimizationFacade


@pytest.fixture
def optimization_facade() -> OptimizationFacade:
    return OptimizationFacade()
