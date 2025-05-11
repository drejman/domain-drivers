from datetime import timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from schedule.optimization.optimization_facade import OptimizationFacade
from schedule.shared.capability.capability import Capability
from schedule.shared.timeslot.time_slot import TimeSlot
from schedule.simulation.simulation_facade import SimulationFacade

from ..allocated_capability import AllocatedCapability
from ..demand import Demand
from ..demands import Demands
from ..project import Project
from ..simulated_transfer import SimulatedProjectAllocations
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
def banking_soft_id() -> UUID:
    return uuid4()


@pytest.fixture
def insurance_soft_id() -> UUID:
    return uuid4()


@pytest.fixture
def staszek_java_mid(jan_1: TimeSlot) -> AllocatedCapability:
    return AllocatedCapability(uuid4(), Capability.skill("JAVA-MID"), jan_1)


@pytest.fixture
def transfer_simulation_service() -> TransferSimulationService:
    return TransferSimulationService(SimulationFacade(OptimizationFacade()))


@pytest.mark.skip(reason="Fix service to load projects")
class TestPotentialTransferScenarios:
    def test_simulates_moving_capabilities_to_different_project(
        self,
        demand_for_java_mid_in_jan: Demands,
        banking_soft_id: UUID,
        insurance_soft_id: UUID,
        staszek_java_mid: AllocatedCapability,
        jan_1: TimeSlot,
        transfer_simulation_service: TransferSimulationService,
    ) -> None:
        banking_soft = Project(demand_for_java_mid_in_jan, Decimal(9))
        insurance_soft = Project(demand_for_java_mid_in_jan, Decimal(90))
        projects = SimulatedProjectAllocations({banking_soft_id: banking_soft, insurance_soft_id: insurance_soft})
        banking_soft.add(staszek_java_mid)

        result = transfer_simulation_service.simulate_potential_transfer(
            projects, banking_soft_id, insurance_soft_id, staszek_java_mid, jan_1
        )

        assert result == 81

    def test_simulates_moving_capabilities_to_different_project_just_for_a_while(
        self,
        demand_for_java_mid_in_jan: Demands,
        demand_for_java_just_for_15min_in_jan: Demands,
        banking_soft_id: UUID,
        insurance_soft_id: UUID,
        staszek_java_mid: AllocatedCapability,
        fifteen_minutes_in_jan: TimeSlot,
        transfer_simulation_service: TransferSimulationService,
    ) -> None:
        banking_soft = Project(demand_for_java_mid_in_jan, Decimal(9))
        insurance_soft = Project(demand_for_java_just_for_15min_in_jan, Decimal(99))
        projects = SimulatedProjectAllocations({banking_soft_id: banking_soft, insurance_soft_id: insurance_soft})
        banking_soft.add(staszek_java_mid)

        result = transfer_simulation_service.simulate_potential_transfer(
            projects,
            banking_soft_id,
            insurance_soft_id,
            staszek_java_mid,
            fifteen_minutes_in_jan,
        )

        assert result == 90

    def test_the_move_gives_zero_profit_when_there_are_still_missing_demands(
        self,
        demand_for_java_mid_in_jan: Demands,
        demands_for_java_and_python_in_jan: Demands,
        banking_soft_id: UUID,
        insurance_soft_id: UUID,
        staszek_java_mid: AllocatedCapability,
        jan_1: TimeSlot,
        transfer_simulation_service: TransferSimulationService,
    ) -> None:
        banking_soft = Project(demand_for_java_mid_in_jan, Decimal(9))
        insurance_soft = Project(demands_for_java_and_python_in_jan, Decimal(99))
        projects = SimulatedProjectAllocations({banking_soft_id: banking_soft, insurance_soft_id: insurance_soft})
        banking_soft.add(staszek_java_mid)

        result = transfer_simulation_service.simulate_potential_transfer(
            projects, banking_soft_id, insurance_soft_id, staszek_java_mid, jan_1
        )

        assert result == -9
