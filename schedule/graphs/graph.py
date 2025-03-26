from graphlib import TopologicalSorter

from .graph_elements import Node


class Graph[T]:
    def __init__(self) -> None:
        self.nodes: dict[Node[T], set[Node[T]]] = {}

    def add_node(self, node: Node[T]) -> None:
        self.nodes[node] = self.nodes.get(node, set()).union(node.predecessors)

    def topological_sort(self) -> list[list[Node[T]]]:
        nodes = []

        ts = TopologicalSorter(self.nodes)
        ts.prepare()
        while ts.is_active():
            node_group = ts.get_ready()
            nodes.append(list(node_group))
            ts.done(*node_group)

        return nodes
