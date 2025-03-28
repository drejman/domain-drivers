from __future__ import annotations

import attrs as a

from .available_resource_capability import (
    AvailableResourceCapability,
)


@a.define(frozen=True)
class SimulatedCapabilities:
    capabilities: frozenset[AvailableResourceCapability]

    def add(
        self, *new_capabilities: AvailableResourceCapability
    ) -> SimulatedCapabilities:
        new_availabilities = list(self.capabilities) + list(new_capabilities)
        return SimulatedCapabilities(frozenset(new_availabilities))
