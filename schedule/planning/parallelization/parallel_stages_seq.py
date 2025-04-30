from __future__ import annotations

from collections.abc import Iterable
from typing import override

import attrs as a

from .parallel_stages import ParallelStages


def convert_all(all_: Iterable[ParallelStages]) -> tuple[ParallelStages, ...]:
    return tuple(all_)


@a.define(frozen=True)
class ParallelStagesSequence:
    _all: tuple[ParallelStages, ...] = a.field(factory=tuple, converter=convert_all)

    @staticmethod
    def of(*stages: ParallelStages) -> ParallelStagesSequence:
        return ParallelStagesSequence(stages)

    @staticmethod
    def empty() -> ParallelStagesSequence:
        return ParallelStagesSequence()

    @property
    def all(self) -> tuple[ParallelStages, ...]:
        return self._all

    @override
    def __str__(self) -> str:
        return " | ".join([str(parallel_stages) for parallel_stages in self._all])
