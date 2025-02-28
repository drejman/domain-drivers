from collections.abc import Collection
from typing import Self

from .graphs import GraphFacade
from .stage import Stage


class StageParallelization:
    _sorted_stages: list[list[str]]

    def __init__(self) -> None:
        self._sorted_stages = []

    def from_stages(self, stages: Collection[Stage]) -> Self:
        graph = GraphFacade()

        for stage in stages:
            graph.add_node(name=stage.name)

        for stage in stages:
            for dependency in stage.dependencies:
                graph.add_edge(from_node=dependency.name, to_node=stage.name)

        self._sorted_stages = graph.sorted_stages()
        return self

    def __repr__(self) -> str:
        return " | ".join(", ".join(stage) for stage in self._sorted_stages)
