from typing import Self

import attrs as a

from .parallel_stages import ParallelStages


@a.define(frozen=True)
class ParallelStagesSequence:
    _all: tuple[ParallelStages, ...] = a.field(factory=tuple)

    @classmethod
    def empty(cls) -> Self:
        return ParallelStagesSequence()

    @property
    def all(self) -> tuple[ParallelStages, ...]:
        return self._all

    def __str__(self):
        return " | ".join([str(parallel_stages) for parallel_stages in self._all])
