from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from schedule.optimization.optimization_facade import OptimizationFacade
from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot
from schedule.simulation.simulation_facade import SimulationFacade

from ..allocated_capability import AllocatedCapability
from ..allocation_facade import AllocationFacade
from ..demand import Demand
from ..demands import Demands
from ..project_allocations_id import ProjectAllocationsId
from ..resource_id import ResourceId
from ..transfer_simulation_service import TransferSimulationService


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
    return AllocatedCapability(uuid4(), Capability.skill("JAVA-MID"), jan_1)


@pytest.fixture
def transfer_simulation_service(allocation_facade: AllocationFacade) -> TransferSimulationService:
    return TransferSimulationService(SimulationFacade(OptimizationFacade()), allocation_facade=allocation_facade)


class TestPotentialTransferScenarios:
    def test_simulates_moving_capabilities_to_different_project(
        self,
        demand_for_java_mid_in_jan: Demands,
        banking_soft_id: ProjectAllocationsId,
        insurance_soft_id: ProjectAllocationsId,
        staszek_java_mid: AllocatedCapability,
        transfer_simulation_service: TransferSimulationService,
        allocation_facade: AllocationFacade,
    ) -> None:
        allocation_facade.schedule_project_allocations_demands(
            project_id=banking_soft_id, demands=demand_for_java_mid_in_jan
        )
        allocation_facade.schedule_project_allocations_demands(
            project_id=insurance_soft_id, demands=demand_for_java_mid_in_jan
        )
        allocation_uuid = allocation_facade.allocate_to_project(
            project_id=banking_soft_id,
            resource_id=ResourceId(staszek_java_mid.resource_id),
            capability=staszek_java_mid.capability,
            time_slot=staszek_java_mid.time_slot,
        )
        summary = allocation_facade.find_projects_allocations_by_ids(banking_soft_id)
        allocated_capability = summary.project_allocations[banking_soft_id].find(allocation_uuid)
        result = transfer_simulation_service.simulate_potential_transfer(
            project_from=banking_soft_id,
            project_to=insurance_soft_id,
            project_from_earnings=Decimal(9),
            project_to_earnings=Decimal(90),
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
        fifteen_minutes_in_jan: TimeSlot,
        transfer_simulation_service: TransferSimulationService,
        allocation_facade: AllocationFacade,
    ) -> None:
        allocation_facade.schedule_project_allocations_demands(
            project_id=banking_soft_id, demands=demand_for_java_mid_in_jan
        )
        allocation_facade.schedule_project_allocations_demands(
            project_id=insurance_soft_id, demands=demand_for_java_just_for_15min_in_jan
        )
        allocation_uuid = allocation_facade.allocate_to_project(
            project_id=banking_soft_id,
            resource_id=ResourceId(staszek_java_mid.resource_id),
            capability=staszek_java_mid.capability,
            time_slot=staszek_java_mid.time_slot,
        )
        summary = allocation_facade.find_projects_allocations_by_ids(banking_soft_id)
        allocated_capability = summary.project_allocations[banking_soft_id].find(allocation_uuid)
        result = transfer_simulation_service.simulate_potential_transfer(
            project_from=banking_soft_id,
            project_to=insurance_soft_id,
            project_from_earnings=Decimal(9),
            project_to_earnings=Decimal(19),
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
        jan_1: TimeSlot,
        transfer_simulation_service: TransferSimulationService,
        allocation_facade: AllocationFacade,
    ) -> None:
        allocation_facade.schedule_project_allocations_demands(
            project_id=banking_soft_id, demands=demand_for_java_mid_in_jan
        )
        allocation_facade.schedule_project_allocations_demands(
            project_id=insurance_soft_id, demands=demands_for_java_and_python_in_jan
        )
        allocation_uuid = allocation_facade.allocate_to_project(
            project_id=banking_soft_id,
            resource_id=ResourceId(staszek_java_mid.resource_id),
            capability=staszek_java_mid.capability,
            time_slot=staszek_java_mid.time_slot,
        )
        summary = allocation_facade.find_projects_allocations_by_ids(banking_soft_id)
        allocated_capability = summary.project_allocations[banking_soft_id].find(allocation_uuid)
        result = transfer_simulation_service.simulate_potential_transfer(
            project_from=banking_soft_id,
            project_to=insurance_soft_id,
            project_from_earnings=Decimal(9),
            project_to_earnings=Decimal(19),
            capability=allocated_capability,
            for_slot=jan_1,
        )

        assert result == -9
