from dataclasses import dataclass, field
from uuid import UUID, uuid4

from schedule.shared.timeslot.time_slot import TimeSlot

from ..capacity_dimension import CapacityDimension
from ..weight_dimension import WeightDimension


@dataclass(frozen=True)
class CapabilityCapacityDimension(CapacityDimension):
    uuid: UUID = field(default_factory=uuid4, init=False)
    id: str
    capacity_name: str
    capacity_type: str


@dataclass(frozen=True)
class CapabilityWeightDimension(WeightDimension[CapabilityCapacityDimension]):
    name: str
    type: str

    def is_satisfied_by(self, capacity: CapabilityCapacityDimension) -> bool:
        return capacity.capacity_name == self.name and capacity.capacity_type == self.type


@dataclass(frozen=True)
class CapabilityTimedCapacityDimension(CapacityDimension):
    uuid: UUID = field(default_factory=uuid4, init=False)
    id: str
    capacity_name: str
    capacity_type: str
    time_slot: TimeSlot


@dataclass(frozen=True)
class CapabilityTimedWeightDimension(WeightDimension[CapabilityTimedCapacityDimension]):
    name: str
    type: str
    time_slot: TimeSlot

    def is_satisfied_by(self, capacity: CapabilityTimedCapacityDimension) -> bool:
        return (
            capacity.capacity_name == self.name
            and capacity.capacity_type == self.type
            and self.time_slot.within(capacity.time_slot)
        )
