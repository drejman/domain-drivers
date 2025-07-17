from schedule.allocation.capability_scheduling import (
    CapabilityFinder,
)
from schedule.resource import ResourceFacade, Seniority
from schedule.shared.capability import Capability
from schedule.shared.timeslot import TimeSlot

from ..resouce_scheduling_facade import ResourceSchedulingFacade


class TestScheduleEmployeeCapabilities:
    def test_can_setup_capabilities_according_to_policy(
        self,
        resource_facade: ResourceFacade,
        resource_scheduling_facade: ResourceSchedulingFacade,
        capability_finder: CapabilityFinder,
    ) -> None:
        employee_id = resource_facade.add_employee(
            "resourceName",
            "lastName",
            Seniority.LEAD,
            Capability.skills("JAVA, PYTHON"),
            Capability.permissions("ADMIN"),
        )

        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        allocations = resource_scheduling_facade.schedule_capabilities(employee_id, one_day)

        loaded = capability_finder.find_by_id(allocations)
        assert len(loaded.all) == len(allocations)
