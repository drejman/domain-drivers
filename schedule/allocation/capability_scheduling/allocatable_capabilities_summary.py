from __future__ import annotations

from collections.abc import Iterable

import attrs as a

from .allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)


def freeze_allocatable_capability_summary(
    values: Iterable[AllocatableCapabilitySummary],
) -> tuple[AllocatableCapabilitySummary, ...]:
    return tuple(values)


@a.frozen
class AllocatableCapabilitiesSummary:
    all: tuple[AllocatableCapabilitySummary, ...] = a.field(converter=freeze_allocatable_capability_summary)
