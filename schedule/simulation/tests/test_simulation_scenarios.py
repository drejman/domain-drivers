from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from schedule.optimization.optimization_facade import OptimizationFacade
from schedule.shared.capability.capability import Capability

from ...shared.timeslot import TimeSlot
from ..additional_priced_capability import AdditionalPricedCapability
from ..available_resource_capability import AvailableResourceCapability
from ..demand import Demand
from ..demands import Demands
from ..project_id import ProjectId
from ..simulation_facade import SimulationFacade
from .available_capabilities_factory import (
    AvailableResourceCapabilityFactory,
    FakeCapabilityPerformer,
    SimulatedCapabilitiesFactory,
)
from .simulated_projects_factory import (
    SimulatedProjectFactory,
)


@pytest.fixture
def jan_1_time_slot() -> TimeSlot:
    return TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)


@pytest.fixture
def project_1_id() -> ProjectId:
    return ProjectId.new()


@pytest.fixture
def project_2_id() -> ProjectId:
    return ProjectId.new()


@pytest.fixture
def project_3_id() -> ProjectId:
    return ProjectId.new()


@pytest.fixture
def staszek_id() -> UUID:
    return uuid4()


@pytest.fixture
def leon_id() -> UUID:
    return uuid4()


@pytest.fixture
def simulation_facade() -> SimulationFacade:
    return SimulationFacade(optimization_facade=OptimizationFacade())


class TestSimulationScenarios:
    def test_picks_optimal_project_based_on_earnings(
        self,
        staszek_id: UUID,
        jan_1_time_slot: TimeSlot,
        leon_id: UUID,
        simulation_facade: SimulationFacade,
        project_1_id: ProjectId,
        project_2_id: ProjectId,
        project_3_id: ProjectId,
    ) -> None:
        simulated_projects = [
            SimulatedProjectFactory.build(
                project_id=project_1_id,
                value=Decimal(9),
                missing_demands=Demands([Demand.demand_for(Capability.skill("JAVA-MID"), jan_1_time_slot)]),
            ),
            SimulatedProjectFactory.build(
                project_id=project_2_id,
                value=Decimal(99),
                missing_demands=Demands([Demand.demand_for(Capability.skill("JAVA-MID"), jan_1_time_slot)]),
            ),
            SimulatedProjectFactory.build(
                project_id=project_3_id,
                value=Decimal(2),
                missing_demands=Demands([Demand.demand_for(Capability.skill("JAVA-MID"), jan_1_time_slot)]),
            ),
        ]

        simulated_availability = SimulatedCapabilitiesFactory.build(
            num_capabilities=2,
            capabilities__0__resource_id=staszek_id,
            capabilities__0__capability=FakeCapabilityPerformer(Capability.skill("JAVA-MID")),
            capabilities__0__time_slot=jan_1_time_slot,
            capabilities__1__resource_id=leon_id,
            capabilities__1__capability=FakeCapabilityPerformer(Capability.skill("JAVA-MID")),
            capabilities__1__time_slot=jan_1_time_slot,
        )

        result = simulation_facade.what_is_the_optimal_setup(simulated_projects, simulated_availability)

        assert result.profit == 108
        assert len(result.chosen_projects) == 2

    def test_picks_all_when_enough_capabilities(
        self,
        project_1_id: ProjectId,
        jan_1_time_slot: TimeSlot,
        simulation_facade: SimulationFacade,
    ) -> None:
        simulated_projects = [
            SimulatedProjectFactory.build(
                project_id=project_1_id,
                value=Decimal(99),
                missing_demands=Demands([Demand.demand_for(Capability.skill("JAVA-MID"), jan_1_time_slot)]),
            ),
        ]

        simulated_availability = SimulatedCapabilitiesFactory.build(
            num_capabilities=2,
            capabilities__0__resource_id=uuid4(),
            capabilities__0__capability=FakeCapabilityPerformer(Capability.skill("JAVA-MID")),
            capabilities__0__time_slot=jan_1_time_slot,
            capabilities__1__resource_id=uuid4(),
            capabilities__1__capability=FakeCapabilityPerformer(Capability.skill("JAVA-MID")),
            capabilities__1__time_slot=jan_1_time_slot,
        )

        result = simulation_facade.what_is_the_optimal_setup(simulated_projects, simulated_availability)

        assert result.profit == 99
        assert len(result.chosen_projects) == 1

    def test_can_simulate_having_extra_resources(
        self,
        project_1_id: ProjectId,
        project_2_id: ProjectId,
        jan_1_time_slot: TimeSlot,
        staszek_id: UUID,
        simulation_facade: SimulationFacade,
    ) -> None:
        simulated_projects = [
            SimulatedProjectFactory.build(
                project_id=project_1_id,
                value=Decimal(9),
                missing_demands=Demands([Demand.demand_for(Capability.skill("YT DRAMA COMMENTS"), jan_1_time_slot)]),
            ),
            SimulatedProjectFactory.build(
                project_id=project_2_id,
                value=Decimal(99),
                missing_demands=Demands([Demand.demand_for(Capability.skill("YT DRAMA COMMENTS"), jan_1_time_slot)]),
            ),
        ]

        simulated_availability = SimulatedCapabilitiesFactory.build(
            num_capabilities=1,
            capabilities__0__resource_id=staszek_id,
            capabilities__0__capability=FakeCapabilityPerformer(Capability.skill("YT DRAMA COMMENTS")),
            capabilities__0__time_slot=jan_1_time_slot,
        )

        extra_capability = AvailableResourceCapabilityFactory.build(
            resource_id=uuid4(),
            capability=FakeCapabilityPerformer(Capability.skill("YT DRAMA COMMENTS")),
            time_slot=jan_1_time_slot,
        )

        result_without_extra_resource = simulation_facade.what_is_the_optimal_setup(
            simulated_projects, simulated_availability
        )
        result_with_extra_resource = simulation_facade.what_is_the_optimal_setup(
            simulated_projects, simulated_availability.add(extra_capability)
        )

        assert result_without_extra_resource.profit == 99
        assert result_with_extra_resource.profit == 108

    def test_if_it_pays_off_to_pay_for_capability(
        self,
        project_1_id: ProjectId,
        project_2_id: ProjectId,
        jan_1_time_slot: TimeSlot,
        staszek_id: UUID,
        simulation_facade: SimulationFacade,
    ) -> None:
        simulated_projects = [
            SimulatedProjectFactory.build(
                project_id=project_1_id,
                value=Decimal(100),
                missing_demands=Demands([Demand.demand_for(Capability.skill("JAVA-MID"), jan_1_time_slot)]),
            ),
            SimulatedProjectFactory.build(
                project_id=project_2_id,
                value=Decimal(40),
                missing_demands=Demands([Demand.demand_for(Capability.skill("JAVA-MID"), jan_1_time_slot)]),
            ),
        ]

        simulated_availability = SimulatedCapabilitiesFactory.build(
            num_capabilities=1,
            capabilities__0__resource_id=staszek_id,
            capabilities__0__capability=FakeCapabilityPerformer(Capability.skill("JAVA-MID")),
            capabilities__0__time_slot=jan_1_time_slot,
        )

        slawek = AdditionalPricedCapability(
            Decimal(9999),
            AvailableResourceCapability(
                uuid4(), FakeCapabilityPerformer(Capability.skill("JAVA-MID")), jan_1_time_slot
            ),
        )
        staszek = AdditionalPricedCapability(
            Decimal(3),
            AvailableResourceCapability(
                uuid4(), FakeCapabilityPerformer(Capability.skill("JAVA-MID")), jan_1_time_slot
            ),
        )

        buying_slawek_profit = simulation_facade.profit_after_buying_new_capability(
            simulated_projects, simulated_availability, slawek
        )
        buying_staszek_profit = simulation_facade.profit_after_buying_new_capability(
            simulated_projects, simulated_availability, staszek
        )

        # We get 40 from project 2 and lose 9999 for buying Slawek
        assert buying_slawek_profit == -9959
        # We get 40 from project 2 and lose 3 for buying Staszek
        assert buying_staszek_profit == 37
