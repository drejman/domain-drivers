from graphlib import CycleError

import pytest

from ..graph import Graph
from ..node import Node


@pytest.fixture
def graph() -> Graph[str]:
    return Graph[str]()


class TestGraphTopologicalSort:
    def test_topological_sort_with_simple_dependencies(self, graph: Graph[str]) -> None:
        node1 = Node("Node1", "node1")
        node2 = Node("Node2", "node2")
        node3 = Node("Node3", "node3")
        node4 = Node("Node4", "node4")
        node2 = node2.add_predecessors(node1)
        node3 = node3.add_predecessors(node1)
        node4 = node4.add_predecessors(node2)

        graph.add_nodes({node1, node2, node3, node4})

        sorted_nodes = graph.topological_sort()

        assert len(sorted_nodes) == 3

        assert len(sorted_nodes[0]) == 1
        assert node1 in sorted_nodes[0]

        assert len(sorted_nodes[1]) == 2
        assert node2 in sorted_nodes[1]
        assert node3 in sorted_nodes[1]

        assert len(sorted_nodes[2]) == 1
        assert node4 in sorted_nodes[2]

    def test_topological_sort_with_linear_dependencies(self, graph: Graph[str]) -> None:
        node1 = Node("Node1", "node1")
        node2 = Node("Node2", "node2")
        node3 = Node("Node3", "node3")
        node4 = Node("Node4", "node4")
        node5 = Node("Node5", "node5")
        node1 = node1.add_predecessors(node2)
        node2 = node2.add_predecessors(node3)
        node3 = node3.add_predecessors(node4)
        node4 = node4.add_predecessors(node5)

        graph.add_nodes({node1, node2, node3, node4, node5})

        sorted_nodes = graph.topological_sort()

        assert len(sorted_nodes) == 5

        assert len(sorted_nodes[0]) == 1
        assert node5 in sorted_nodes[0]

        assert len(sorted_nodes[1]) == 1
        assert node4 in sorted_nodes[1]

        assert len(sorted_nodes[2]) == 1
        assert node3 in sorted_nodes[2]

        assert len(sorted_nodes[3]) == 1
        assert node2 in sorted_nodes[3]

        assert len(sorted_nodes[4]) == 1
        assert node1 in sorted_nodes[4]

    def test_nodes_without_dependencies(self, graph: Graph[str]) -> None:
        node1 = Node("Node1", "node1")
        node2 = Node("Node2", "node2")
        graph.add_nodes({node1, node2})

        sorted_nodes = graph.topological_sort()

        assert len(sorted_nodes) == 1

    def test_cyclic_dependency(self, graph: Graph[str]) -> None:
        node1 = Node("Node1", "node1")
        node2 = Node("Node2", "node2")
        node2 = node2.add_predecessors(node1)
        node1 = node1.add_predecessors(node2)
        graph.add_nodes({node1, node2})

        with pytest.raises(CycleError):
            _ = graph.topological_sort()
