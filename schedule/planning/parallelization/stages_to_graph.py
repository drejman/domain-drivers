from collections.abc import Sequence

from schedule.sorter import Graph, Node

from .stage import Stage


class StagesToGraph:
    def __init__(self, *stages: Stage) -> None:
        self._temporary_graph: dict[str, Node[Stage]] = {
            stage.name: Node(name=stage.name, content=stage) for stage in stages
        }
        self._stages: tuple[Stage, ...] = stages

    def transform(self) -> Graph[Stage]:
        graph: Graph[Stage] = Graph()

        for i, stage in enumerate(self._stages):
            self._map_explicit_dependencies(stage)
            self._map_shared_resources_dependencies(stage, self._stages[i + 1 :])

        for node in self._temporary_graph.values():
            graph.add_node(node)

        return graph

    def _map_explicit_dependencies(self, stage: Stage) -> None:
        if not stage.has_dependencies:
            return
        node = self._temporary_graph[stage.name]
        dependency_names = {dep.name for dep in stage.dependencies}
        self._temporary_graph[stage.name] = node.add_predecessors(
            *{node for node in self._temporary_graph.values() if node.name in dependency_names}
        )

    def _map_shared_resources_dependencies(
        self,
        stage: Stage,
        next_stages: Sequence[Stage],
    ) -> None:
        for next_stage in next_stages:
            if stage.resources.isdisjoint(next_stage.resources):
                continue
            node = self._temporary_graph[stage.name]
            next_node = self._temporary_graph[next_stage.name]
            if stage.count_of_resources > next_stage.count_of_resources:
                self._temporary_graph[stage.name] = node.add_predecessors(next_node)
            else:
                self._temporary_graph[next_stage.name] = next_node.add_predecessors(node)
