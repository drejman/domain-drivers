from __future__ import annotations

from collections.abc import Iterable
from operator import attrgetter
from typing import override

import attrs as a

from .stage import Stage


def stages_converter(stages: Iterable[Stage]) -> tuple[Stage, ...]:
    return tuple(sorted(stages, key=attrgetter("name")))


@a.define(frozen=True)
class ParallelStages:
    stages: tuple[Stage, ...] = a.field(converter=stages_converter)

    @staticmethod
    def of(*stages: Stage) -> ParallelStages:
        return ParallelStages(stages)

    @override
    def __str__(self) -> str:
        return ", ".join([str(stage) for stage in self.stages])
