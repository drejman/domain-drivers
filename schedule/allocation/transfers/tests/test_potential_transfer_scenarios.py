from datetime import timedelta

import pytest
from lagom import Container

from schedule.allocation.allocated_capability import AllocatedCapability
from schedule.allocation.allocation_facade import AllocationFacade
from schedule.allocation.capability_scheduling import AllocatableCapabilityId, CapabilitySelector
from schedule.allocation.capability_scheduling.allocatable_resource_id import AllocatableResourceId
from schedule.allocation.cashflow.earnings import Earnings
from schedule.allocation.demand import Demand
from schedule.allocation.demands import Demands
from schedule.allocation.project_allocations_id import ProjectAllocationsId
from schedule.allocation.tests.conftest import AllocatableResourceFactory, allocatable_resource_factory  # noqa: F401
from schedule.allocation.transfers.transfer_simulation_service import TransferSimulationService
from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot


@pytest.fixture
def jan_1() -> TimeSlot:
    return TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)


@pytest.fixture
def fifteen_minutes_in_jan(jan_1: TimeSlot) -> TimeSlot:
    return TimeSlot(jan_1.from_, jan_1.from_ + timedelta(minutes=15))


@pytest.fixture
def demand_for_java_just_for_15min_in_jan(fifteen_minutes_in_jan: TimeSlot) -> Demands:
    return Demands([Demand(Capability.skill("JAVA-MID"), fifteen_minutes_in_jan)])


@pytest.fixture
def demand_for_java_mid_in_jan(jan_1: TimeSlot) -> Demands:
    return Demands([Demand(Capability.skill("JAVA-MID"), jan_1)])


@pytest.fixture
def demands_for_java_and_python_in_jan(jan_1: TimeSlot) -> Demands:
    return Demands(
        [
            Demand(Capability.skill("JAVA-MID"), jan_1),
            Demand(Capability.skill("PYTHON-MID"), jan_1),
        ]
    )


@pytest.fixture
def banking_soft_id() -> ProjectAllocationsId:
    return ProjectAllocationsId.new_one()


@pytest.fixture
def insurance_soft_id() -> ProjectAllocationsId:
    return ProjectAllocationsId.new_one()


@pytest.fixture
def staszek_java_mid(jan_1: TimeSlot) -> AllocatedCapability:
    return AllocatedCapability(
        AllocatableCapabilityId.new_one(), CapabilitySelector.can_just_perform(Capability.skill("JAVA-MID")), jan_1
    )


@pytest.fixture
def staszek_resource() -> AllocatableResourceId:
    return AllocatableResourceId.new_one()


@pytest.fixture
def transfer_simulation_service(container: Container) -> TransferSimulationService:
    return container.resolve(TransferSimulationService)


class TestPotentialTransferScenarios:
    def test_simulates_moving_capabilities_to_different_project(
        self,
        demand_for_java_mid_in_jan: Demands,
        banking_soft_id: ProjectAllocationsId,
        insurance_soft_id: ProjectAllocationsId,
        staszek_java_mid: AllocatedCapability,
        staszek_resource: AllocatableResourceId,
        transfer_simulation_service: TransferSimulationService,
        allocation_facade: AllocationFacade,
        allocatable_resource_factory: AllocatableResourceFactory,  # noqa: F811
    ) -> None:
        allocation_facade.schedule_project_allocations_demands(
            project_id=banking_soft_id, demands=demand_for_java_mid_in_jan
        )
        allocation_facade.schedule_project_allocations_demands(
            project_id=insurance_soft_id, demands=demand_for_java_mid_in_jan
        )
        allocation_uuid = allocation_facade.allocate_to_project(
            project_id=banking_soft_id,
            allocatable_capability_id=allocatable_resource_factory(
                staszek_java_mid.time_slot, staszek_java_mid.capability, staszek_resource
            ),
            time_slot=staszek_java_mid.time_slot,
        )
        summary = allocation_facade.find_projects_allocations_by_ids(banking_soft_id)
        allocated_capability = summary.project_allocations[banking_soft_id].find(
            AllocatableCapabilityId(allocation_uuid)
        )
        result = transfer_simulation_service.simulate_potential_transfer(
            project_from=banking_soft_id,
            project_to=insurance_soft_id,
            project_from_earnings=Earnings(9),
            project_to_earnings=Earnings(90),
            capability=allocated_capability,
            for_slot=staszek_java_mid.time_slot,
        )

        assert result == 81

    def test_simulates_moving_capabilities_to_different_project_just_for_a_while(
        self,
        demand_for_java_mid_in_jan: Demands,
        demand_for_java_just_for_15min_in_jan: Demands,
        banking_soft_id: ProjectAllocationsId,
        insurance_soft_id: ProjectAllocationsId,
        staszek_java_mid: AllocatedCapability,
        staszek_resource: AllocatableResourceId,
        fifteen_minutes_in_jan: TimeSlot,
        transfer_simulation_service: TransferSimulationService,
        allocation_facade: AllocationFacade,
        allocatable_resource_factory: AllocatableResourceFactory,  # noqa: F811
    ) -> None:
        allocation_facade.schedule_project_allocations_demands(
            project_id=banking_soft_id, demands=demand_for_java_mid_in_jan
        )
        allocation_facade.schedule_project_allocations_demands(
            project_id=insurance_soft_id, demands=demand_for_java_just_for_15min_in_jan
        )
        allocation_uuid = allocation_facade.allocate_to_project(
            project_id=banking_soft_id,
            allocatable_capability_id=allocatable_resource_factory(
                staszek_java_mid.time_slot, staszek_java_mid.capability, staszek_resource
            ),
            time_slot=staszek_java_mid.time_slot,
        )
        summary = allocation_facade.find_projects_allocations_by_ids(banking_soft_id)
        allocated_capability = summary.project_allocations[banking_soft_id].find(
            AllocatableCapabilityId(allocation_uuid)
        )
        result = transfer_simulation_service.simulate_potential_transfer(
            project_from=banking_soft_id,
            project_to=insurance_soft_id,
            project_from_earnings=Earnings(9),
            project_to_earnings=Earnings(19),
            capability=allocated_capability,
            for_slot=fifteen_minutes_in_jan,
        )

        assert result == 10

    def test_the_move_gives_zero_profit_when_there_are_still_missing_demands(
        self,
        demand_for_java_mid_in_jan: Demands,
        demands_for_java_and_python_in_jan: Demands,
        banking_soft_id: ProjectAllocationsId,
        insurance_soft_id: ProjectAllocationsId,
        staszek_java_mid: AllocatedCapability,
        staszek_resource: AllocatableResourceId,
        jan_1: TimeSlot,
        transfer_simulation_service: TransferSimulationService,
        allocation_facade: AllocationFacade,
        allocatable_resource_factory: AllocatableResourceFactory,  # noqa: F811
    ) -> None:
        allocation_facade.schedule_project_allocations_demands(
            project_id=banking_soft_id, demands=demand_for_java_mid_in_jan
        )
        allocation_facade.schedule_project_allocations_demands(
            project_id=insurance_soft_id, demands=demands_for_java_and_python_in_jan
        )
        allocation_uuid = allocation_facade.allocate_to_project(
            project_id=banking_soft_id,
            allocatable_capability_id=allocatable_resource_factory(
                staszek_java_mid.time_slot, staszek_java_mid.capability, staszek_resource
            ),
            time_slot=staszek_java_mid.time_slot,
        )
        summary = allocation_facade.find_projects_allocations_by_ids(banking_soft_id)
        allocated_capability = summary.project_allocations[banking_soft_id].find(
            AllocatableCapabilityId(allocation_uuid)
        )
        result = transfer_simulation_service.simulate_potential_transfer(
            project_from=banking_soft_id,
            project_to=insurance_soft_id,
            project_from_earnings=Earnings(9),
            project_to_earnings=Earnings(19),
            capability=allocated_capability,
            for_slot=jan_1,
        )

        assert result == -9
