import pytest

from ..graph import Graph
from ..node import Node


@pytest.fixture
def graph() -> Graph[str]:
    return Graph[str]()


class TestFeedbackArcSet:
    def test_can_find_minimum_number_of_edges_to_remove_to_make_the_graph_acyclic(self, graph: Graph[str]) -> None:
        node1 = Node("1", "node1")
        node2 = Node("2", "node2")
        node3 = Node("3", "node3")
        node4 = Node("4", "node4")
        node1 = node1.add_predecessors(node2)
        node2 = node2.add_predecessors(node3)
        node4 = node4.add_predecessors(node3)
        node1 = node1.add_predecessors(node4)
        node3 = node3.add_predecessors(node1)
        graph.add_nodes({node1, node2, node3, node4})

        to_remove = graph.feedback_arc_set()

        assert len(to_remove) == 2

    def test_when_graph_is_acyclic_there_is_nothing_to_remove(self, graph: Graph[str]) -> None:
        node1 = Node("1", "node1")
        node2 = Node("2", "node2")
        node3 = Node("3", "node3")
        node4 = Node("4", "node4")
        node1 = node1.add_predecessors(node2)
        node2 = node2.add_predecessors(node3)
        node1 = node1.add_predecessors(node4)
        graph.add_nodes({node1, node2, node3, node4})

        to_remove = graph.feedback_arc_set()

        assert len(to_remove) == 0
