from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .available_resource_capability import (
        AvailableResourceCapability,
    )


def freeze_capabilities(capabilities: Iterable[AvailableResourceCapability]) -> frozenset[AvailableResourceCapability]:
    return frozenset(capabilities)


@a.define(frozen=True)
class SimulatedCapabilities:
    capabilities: frozenset[AvailableResourceCapability] = a.field(converter=freeze_capabilities)

    def add(self, *new_capabilities: AvailableResourceCapability) -> SimulatedCapabilities:
        new_availabilities = list(self.capabilities) + list(new_capabilities)
        return SimulatedCapabilities(new_availabilities)

    @classmethod
    def none(cls) -> SimulatedCapabilities:
        return cls(frozenset())
