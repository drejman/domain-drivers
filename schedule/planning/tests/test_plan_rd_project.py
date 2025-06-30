from datetime import UTC, datetime, timedelta
from typing import Final

from schedule.availability.resource_id import ResourceId
from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot

from ...availability import AvailabilityFacade
from ..parallelization.stage import Stage
from ..planning_facade import PlanningFacade
from ..project_card import ProjectCard
from ..project_id import ProjectId
from .assertions.schedule_assert import ScheduleAssert


class TestRd:
    JANUARY: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 31))
    FEBRUARY: Final = TimeSlot(datetime(2020, 2, 1), datetime(2020, 2, 29))
    MARCH: Final = TimeSlot(datetime(2020, 3, 1), datetime(2020, 3, 31))
    Q1: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 3, 31))
    JAN_1_4: Final = TimeSlot(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 1, 4, tzinfo=UTC))
    FEB_1_15: Final = TimeSlot(datetime(2020, 2, 1, tzinfo=UTC), datetime(2020, 2, 15, tzinfo=UTC))
    MAR_1_6: Final = TimeSlot(datetime(2020, 3, 1, tzinfo=UTC), datetime(2020, 3, 6, tzinfo=UTC))

    def test_research_and_development_project_process(
        self, planning_facade: PlanningFacade, availability_facade: AvailabilityFacade
    ) -> None:
        project_id = planning_facade.add_new_project("R&D")
        r1 = ResourceId.new_one()
        java_available_in_january = self._resource_available_for_capability_in_period(
            r1, Capability.skill("JAVA"), self.JANUARY, availability_facade
        )
        r2 = ResourceId.new_one()
        php_available_in_february = self._resource_available_for_capability_in_period(
            r2, Capability.skill("PHP"), self.FEBRUARY, availability_facade
        )
        r3 = ResourceId.new_one()
        csharp_available_in_march = self._resource_available_for_capability_in_period(
            r3, Capability.skill("CSHARP"), self.MARCH, availability_facade
        )
        all_resources = {r1, r2, r3}

        planning_facade.define_resources_within_dates(project_id, all_resources, self.JANUARY)

        self._verify_that_resources_are_missing(project_id, {php_available_in_february, csharp_available_in_march})

        planning_facade.define_resources_within_dates(project_id, all_resources, self.FEBRUARY)

        self._verify_that_resources_are_missing(project_id, {java_available_in_january, csharp_available_in_march})

        planning_facade.define_resources_within_dates(project_id, all_resources, self.Q1)

        self._verify_that_no_resources_are_missing(project_id)

        planning_facade.adjust_stages_to_resource_availability(
            project_id,
            self.Q1,
            Stage("Stage1", duration=timedelta(days=3), resources=frozenset({r1})),
            Stage("Stage2", duration=timedelta(days=14), resources=frozenset({r2})),
            Stage("Stage3", duration=timedelta(days=5), resources=frozenset({r3})),
        )

        loaded = planning_facade.load(project_id)
        schedule_assert = ScheduleAssert(loaded.schedule)
        schedule_assert.assert_has_stage("Stage1").assert_with_slot(self.JAN_1_4)
        schedule_assert.assert_has_stage("Stage2").assert_with_slot(self.FEB_1_15)
        schedule_assert.assert_has_stage("Stage3").assert_with_slot(self.MAR_1_6)
        self._assert_project_is_not_parallelized(loaded)

    def _resource_available_for_capability_in_period(
        self,
        resource_id: ResourceId,
        capability: Capability,
        time_slot: TimeSlot,
        availability_facade: AvailabilityFacade,
    ) -> None:
        availability_facade.create_resource_slots(resource_id, time_slot)

    def _assert_project_is_not_parallelized(self, project_card: ProjectCard) -> None:
        __tracebackhide__ = True

        assert len(project_card.parallelized_stages.all) == 0, "Project should not be parallelized"

    def _verify_that_no_resources_are_missing(self, project_id: ProjectId) -> None:
        # TODO: add assertion
        pass

    def _verify_that_resources_are_missing(self, project_id: ProjectId, missing_resources: set[ResourceId]) -> None:
        # TODO: add assertion
        pass
