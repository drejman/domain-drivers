from typing import Protocol

from schedule.shared.capability.capability import Capability


class CapabilityPerformer(Protocol):
    def can_perform(self, *capabilities: Capability) -> bool: ...
