from typing import Sequence

from schedule.sorter import Graph, Node
from .parallel_stages import ParallelStages
from .parallel_stages_seq import ParallelStagesSequence
from .stage import Stage


class StageParallelization:
    def from_stages(self, stages: Sequence[Stage]) -> ParallelStagesSequence:
        temporary_graph: dict[str, Node[Stage]] = {
            stage.name: Node(name=stage.name, content=stage) for stage in stages
        }
        graph: Graph[Stage] = Graph()

        for i, stage in enumerate(stages):
            self._map_explicit_dependencies(stage, temporary_graph)
            self._map_shared_resources_dependencies(
                stage, stages[i + 1 :], temporary_graph
            )

        for node in temporary_graph.values():
            graph.add_node(node)

        sorted_nodes = graph.topological_sort()

        return ParallelStagesSequence(
            [ParallelStages(node.content for node in level) for level in sorted_nodes]
        )

    def _map_explicit_dependencies(
        self, stage: Stage, temporary_graph: dict[str, Node[Stage]]
    ) -> None:
        if not stage.has_dependencies:
            return
        node = temporary_graph[stage.name]
        dependency_names = {dep.name for dep in stage.dependencies}
        temporary_graph[stage.name] = node.add_predecessors(
            *{
                node
                for node in temporary_graph.values()
                if node.name in dependency_names
            }
        )

    def _map_shared_resources_dependencies(
        self,
        stage: Stage,
        next_stages: Sequence[Stage],
        temporary_graph: dict[str, Node[Stage]],
    ) -> None:
        for next_stage in next_stages:
            if stage.resources.isdisjoint(next_stage.resources):
                continue
            node = temporary_graph[stage.name]
            next_node = temporary_graph[next_stage.name]
            if stage.count_of_resources > next_stage.count_of_resources:
                temporary_graph[stage.name] = node.add_predecessors(next_node)
            else:
                temporary_graph[next_stage.name] = next_node.add_predecessors(node)
