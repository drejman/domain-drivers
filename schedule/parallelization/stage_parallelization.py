from collections.abc import Collection

from schedule.graphs import GraphFacade
from .parallel_stages import ParallelStages
from .parallel_stages_seq import ParallelStagesSequence
from .stage import Stage


class StageParallelization:
    def from_stages(self, stages: Collection[Stage]) -> ParallelStagesSequence:
        stage_lookup = {stage.name: stage for stage in stages}
        graph = GraphFacade()

        for stage in stages:
            graph.add_node(name=stage.name)

        for stage in stages:
            for dependency in stage.dependencies:
                graph.add_edge(from_node=dependency.name, to_node=stage.name)

        sorted_stages = graph.sorted_stages()
        return ParallelStagesSequence(
            [
                ParallelStages(set(map(stage_lookup.get, stage)))
                for stage in sorted_stages
            ]
        )
