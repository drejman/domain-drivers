from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum, auto

import attrs as a

from schedule.shared.capability import Capability


class SelectingPolicy(StrEnum):
    ALL_SIMULTANEOUSLY = auto()
    ONE_OF_ALL = auto()


def freeze_capabilities(capabilites: Iterable[Capability]) -> frozenset[Capability]:
    return frozenset(capabilites)


@a.frozen
class CapabilitySelector:
    capabilities: frozenset[Capability] = a.field(converter=freeze_capabilities)
    selecting_policy: SelectingPolicy

    @staticmethod
    def can_perform_all_at_the_time(
        capabilities: set[Capability],
    ) -> CapabilitySelector:
        return CapabilitySelector(capabilities, SelectingPolicy.ALL_SIMULTANEOUSLY)

    @staticmethod
    def can_just_perform(capability: Capability) -> CapabilitySelector:
        return CapabilitySelector({capability}, SelectingPolicy.ONE_OF_ALL)

    @staticmethod
    def can_perform_one_of(capabilities: set[Capability]) -> CapabilitySelector:
        return CapabilitySelector(capabilities, SelectingPolicy.ONE_OF_ALL)

    def can_perform(self, *capabilities: Capability) -> bool:
        # TODO: consider extracting algorithms into Policy functions using Strategy pattern  # noqa: FIX002, TD002
        if len(capabilities) == 1:
            return capabilities[0] in self.capabilities

        return self.selecting_policy == SelectingPolicy.ALL_SIMULTANEOUSLY and self.capabilities.issuperset(
            set(capabilities)
        )
