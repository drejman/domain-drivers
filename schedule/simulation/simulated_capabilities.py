from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

if TYPE_CHECKING:
    from .available_resource_capability import (
        AvailableResourceCapability,
    )


@a.define(frozen=True)
class SimulatedCapabilities:
    capabilities: frozenset[AvailableResourceCapability]

    def add(self, *new_capabilities: AvailableResourceCapability) -> SimulatedCapabilities:
        new_availabilities = list(self.capabilities) + list(new_capabilities)
        return SimulatedCapabilities(frozenset(new_availabilities))
