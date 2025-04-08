import itertools
from collections.abc import Iterable
from graphlib import CycleError, TopologicalSorter
from typing import TypeVar

from .edge import Edge
from .node import Node

T = TypeVar("T")
type SortedNodes[T] = tuple[tuple[Node[T], ...], ...]


class Graph[T]:
    def __init__(self) -> None:
        self.nodes: dict[Node[T], set[Node[T]]] = {}

    def add_node(self, node: Node[T]) -> None:
        self.nodes[node] = self.nodes.get(node, set()).union(node.predecessors)

    def add_nodes(self, nodes: Iterable[Node[T]]) -> None:
        for node in nodes:
            self.add_node(node)

    def topological_sort(self) -> SortedNodes[T]:
        nodes: list[tuple[Node[T], ...]] = []

        ts = TopologicalSorter(self.nodes)
        ts.prepare()
        while ts.is_active():
            node_group = ts.get_ready()
            nodes.append(tuple(node_group))
            ts.done(*node_group)

        return tuple(nodes)

    def feedback_arc_set(self) -> tuple[Edge[T], ...]:
        try:
            _ = self.topological_sort()
        except CycleError as e:
            nodes: list[Node[T]] = e.args[1]
            edges: list[Edge[T]] = []
            for source, target in itertools.pairwise(nodes[:-1]):
                edges.append(Edge(source, target))
            return tuple(edges)
        else:
            return ()
