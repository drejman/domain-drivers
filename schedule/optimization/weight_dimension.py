from typing import Protocol

from .capacity_dimension import CapacityDimension


class WeightDimension[T: CapacityDimension](Protocol):
    def is_satisfied_by(self, capacity: T) -> bool: ...
