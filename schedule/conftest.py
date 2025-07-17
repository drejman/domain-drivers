import time
from collections.abc import Callable, Iterator

import pytest
from lagom import Container
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from schedule.allocation import AllocationFacade
from schedule.allocation.capability_scheduling import CapabilityFinder, CapabilityScheduler
from schedule.availability import AvailabilityFacade
from schedule.resource import ResourceFacade
from schedule.resource_scheduling import ResourceSchedulingFacade
from schedule.shared.sqla_repository import mapper_registry


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("postgres:15") as container:
        yield container


@pytest.fixture(scope="session")
def engine_for_tests(postgres_container: PostgresContainer) -> Engine:
    url = postgres_container.get_connection_url()
    engine = create_engine(url)

    # There seems to be some race condition. Fine, let's wait.
    start = time.monotonic()
    while time.monotonic() - start < 30:
        try:
            _ = engine.connect()
            break
        except Exception:  # noqa: BLE001
            time.sleep(0.1)

    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def session_factory(engine_for_tests: Engine) -> Callable[[], Session]:
    return sessionmaker(bind=engine_for_tests)


@pytest.fixture
def session(session_factory: Callable[[], Session]) -> Iterator[Session]:
    a_session = session_factory()
    yield a_session
    a_session.close()


@pytest.fixture
def container(session: Session) -> Container:
    container = Container()
    container[Session] = session
    return container


@pytest.fixture
def availability_facade(container: Container) -> AvailabilityFacade:
    return container.resolve(AvailabilityFacade)


@pytest.fixture
def allocation_facade(container: Container) -> AllocationFacade:
    return container.resolve(AllocationFacade)


@pytest.fixture
def capability_scheduler(container: Container) -> CapabilityScheduler:
    return container.resolve(CapabilityScheduler)


@pytest.fixture
def resource_facade(container: Container) -> ResourceFacade:
    return container.resolve(ResourceFacade)


@pytest.fixture
def resource_scheduling_facade(container: Container) -> ResourceSchedulingFacade:
    return container.resolve(ResourceSchedulingFacade)


@pytest.fixture
def capability_finder(container: Container) -> CapabilityFinder:
    return container.resolve(CapabilityFinder)
