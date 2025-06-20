import random
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from schedule.shared.timeslot import TimeSlot

from ..owner import Owner
from ..repository.availability_sqla_repository import (
    ResourceAvailabilityRepository,
)
from ..resource_availability import ResourceAvailability
from ..resource_availability_id import ResourceAvailabilityId
from ..time_blocks.atomic_time_block import AtomicTimeBlock
from ..time_blocks.duration_unit import DurationUnit


class TestResourceAvailabilityLoading:
    ONE_MONTH = AtomicTimeBlock.split(
        time_slot=TimeSlot.create_monthly_time_slot_at_utc(2021, 1), duration_unit=DurationUnit(minutes=60 * 24 * 31)
    )[0]

    def test_saves_and_loads_by_id(self, repository: ResourceAvailabilityRepository) -> None:
        resource_availablity_id = ResourceAvailabilityId.new_one()
        resource_id = ResourceAvailabilityId.new_one()
        resource_availability = ResourceAvailability(resource_availablity_id, resource_id, self.ONE_MONTH)

        repository.add(resource_availability)

        loaded = repository.load_by_id(resource_availability.id)
        assert loaded == resource_availability
        assert loaded._time_block == self.ONE_MONTH
        assert loaded._resource_id == resource_availability._resource_id
        assert loaded.blocked_by == resource_availability.blocked_by


class TestResourceAvailabilityOptimisticLocking:
    ONE_MONTH = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)

    def test_update_bumps_version(self, repository: ResourceAvailabilityRepository) -> None:
        resource_availability_id = ResourceAvailabilityId.new_one()
        resource_id = ResourceAvailabilityId.new_one()
        resource_availability = ResourceAvailability(resource_availability_id, resource_id, self.ONE_MONTH)
        repository.add(resource_availability)

        loaded = repository.load_by_id(resource_availability.id)
        assert loaded._version == 1
        loaded.block(Owner.new_one())
        repository.add(loaded)

        loaded_again = repository.load_by_id(resource_availability.id)
        assert loaded_again._version == 2

    def test_cant_update_concurrently(self, session_factory: Callable[[], Session]) -> None:
        resource_availability_id = ResourceAvailabilityId.new_one()
        resource_id = ResourceAvailabilityId.new_one()
        resource_availability = ResourceAvailability(resource_availability_id, resource_id, self.ONE_MONTH)
        session = session_factory()
        repository = ResourceAvailabilityRepository(session)
        repository.add(resource_availability)
        session.commit()
        initial_obj = repository.load_by_id(resource_availability_id)
        expected_initial_version = 1
        assert initial_obj._version == expected_initial_version
        session.close()

        # Thread-safe counters
        success_count = 0
        failure_count = 0
        lock = threading.Lock()

        def try_to_block() -> None:
            nonlocal success_count, failure_count
            session = session_factory()
            repo = ResourceAvailabilityRepository(session)
            try:
                loaded = repo.load_by_id(resource_availability_id)
                result = loaded.block(Owner.new_one())
                if result is False:
                    return
                repo.add(loaded)
                time.sleep(random.uniform(0, 0.001))  # simulate race conditions
                session.commit()
                with lock:
                    success_count += 1
            except StaleDataError:
                with lock:
                    failure_count += 1
            finally:
                session.close()

        # Run 10 concurrent attempts
        pool = ThreadPoolExecutor(max_workers=10)
        futures = [pool.submit(try_to_block) for _ in range(10)]
        for f in futures:
            f.result()

        assert success_count >= 1, "At least one update should succeed"
        assert failure_count >= 1, "At least one update should fail due to optimistic locking"

        session = session_factory()
        repository = ResourceAvailabilityRepository(session)

        # Final version check
        final_obj = repository.load_by_id(resource_availability_id)
        print(f"Success count: {success_count}, final version: {final_obj._version}")  # noqa: T201
        assert final_obj._version == success_count + expected_initial_version


class TestResourceAvailabilityUniqueness:
    ONE_MONTH = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)

    def test_cant_save_two_availabilities_with_the_same_resource_id_and_segment(
        self, repository: ResourceAvailabilityRepository
    ) -> None:
        resource_id = ResourceAvailabilityId.new_one()
        another_resource_id = ResourceAvailabilityId.new_one()
        resource_availability_id = ResourceAvailabilityId.new_one()
        resource_availability = ResourceAvailability(resource_availability_id, resource_id, self.ONE_MONTH)
        repository.add(resource_availability)

        another_resource_availability = ResourceAvailability(
            resource_availability_id, another_resource_id, self.ONE_MONTH
        )

        with pytest.raises(IntegrityError):
            repository.add(another_resource_availability)
