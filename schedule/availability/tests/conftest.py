import pytest
from lagom import Container

from schedule.availability.repository.availability_sqla_repository import ResourceAvailabilityRepository


@pytest.fixture
def repository(container: Container) -> ResourceAvailabilityRepository:
    return container.resolve(ResourceAvailabilityRepository)
