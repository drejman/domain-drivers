from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .parallel_stages import ParallelStages


def convert_all(all_: Sequence[ParallelStages]) -> tuple[ParallelStages, ...]:
    return tuple(all_)


@a.define(frozen=True)
class ParallelStagesSequence:
    _all: tuple[ParallelStages, ...] = a.field(factory=tuple, converter=convert_all)

    @classmethod
    def empty(cls) -> ParallelStagesSequence:
        return ParallelStagesSequence()

    @property
    def all(self) -> tuple[ParallelStages, ...]:
        return self._all

    def __str__(self) -> str:
        return " | ".join([str(parallel_stages) for parallel_stages in self._all])
