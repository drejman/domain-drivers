from graphlib import TopologicalSorter
from typing import TypeVar

from .node import Node

T = TypeVar("T")
type SortedNodes[T] = tuple[tuple[Node[T], ...], ...]


class Graph[T]:
    def __init__(self) -> None:
        self.nodes: dict[Node[T], set[Node[T]]] = {}

    def add_node(self, node: Node[T]) -> None:
        self.nodes[node] = self.nodes.get(node, set()).union(node.predecessors)

    def topological_sort(self) -> SortedNodes[T]:
        nodes: list[tuple[Node[T], ...]] = []

        ts = TopologicalSorter(self.nodes)
        ts.prepare()
        while ts.is_active():
            node_group = ts.get_ready()
            nodes.append(tuple(node_group))
            ts.done(*node_group)

        return tuple(nodes)
