from .parallel_stages import ParallelStages
from .parallel_stages_seq import ParallelStagesSequence
from .removal_suggestion import RemovalSuggestion, StageDependency
from .stage import Stage
from .stages_to_graph import StagesToGraph


class StageParallelization:
    @staticmethod
    def from_stages(*stages: Stage) -> ParallelStagesSequence:
        graph = StagesToGraph(*stages).transform()

        sorted_nodes = graph.topological_sort()

        return ParallelStagesSequence.of(
            *[ParallelStages.of(*(node.content for node in level)) for level in sorted_nodes]
        )

    @staticmethod
    def what_to_remove(*stages: Stage) -> RemovalSuggestion:
        graph = StagesToGraph(*stages).transform()

        edges_to_remove = graph.minimum_feedback_arc_set()

        return RemovalSuggestion(
            dependencies=tuple(
                StageDependency(stage=edge.target.content, dependency=edge.source.content) for edge in edges_to_remove
            )
        )
