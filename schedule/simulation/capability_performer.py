from typing import Protocol

from schedule.shared.capability.capability import Capability


class CapabilityPerformer(Protocol):
    def perform(self, capability: Capability) -> bool: ...
