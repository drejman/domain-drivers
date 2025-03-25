from operator import attrgetter

import attrs as a

from .stage import Stage


def stages_converter(stages: set[Stage]) -> tuple[Stage, ...]:
    return tuple(sorted(stages, key=attrgetter("name")))


@a.define(frozen=True)
class ParallelStages:
    stages: tuple[Stage, ...] = a.field(converter=stages_converter)

    def __str__(self):
        return ", ".join([str(stage) for stage in self.stages])
