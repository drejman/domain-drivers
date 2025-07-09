from datetime import datetime
from typing import final

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from schedule.allocation.capability_scheduling.capability_selector import CapabilitySelector
from schedule.shared.capability.capability import Capability
from schedule.shared.sqla_repository import AsJSON, EmbeddedUUID, mapper_registry
from schedule.shared.timeslot.time_slot import TimeSlot

from .allocatable_capability_id import (
    AllocatableCapabilityId,
)
from .allocatable_resource_id import (
    AllocatableResourceId,
)


@final
@mapper_registry.mapped_as_dataclass()
class AllocatableCapability:
    __tablename__ = "allocatable_capabilities"

    _id: Mapped[AllocatableCapabilityId] = mapped_column(EmbeddedUUID[AllocatableCapabilityId], primary_key=True)
    possible_capabilities: Mapped[CapabilitySelector] = mapped_column(AsJSON[CapabilitySelector])
    resource_id: Mapped[AllocatableResourceId] = mapped_column(EmbeddedUUID[AllocatableResourceId])
    _from_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="from_date")
    _to_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="to_date")

    def __init__(
        self,
        resource_id: AllocatableResourceId,
        possible_capabilities: CapabilitySelector,
        time_slot: TimeSlot,
    ) -> None:
        self._id = AllocatableCapabilityId.new_one()
        self.resource_id = resource_id
        self.possible_capabilities = possible_capabilities
        self._from_date = time_slot.from_
        self._to_date = time_slot.to

    @property
    def id(self) -> AllocatableCapabilityId:
        return self._id

    @property
    def time_slot(self) -> TimeSlot:
        return TimeSlot(self._from_date, self._to_date)

    def can_perform(self, capabilities: set[Capability]) -> bool:
        return self.possible_capabilities.can_perform(*capabilities)
