from .graph import Graph
from .graph_elements import Edge, Node


class GraphFacade:
    def __init__(self) -> None:
        self._graph = Graph()

    def add_node(self, name: str) -> None:
        node = Node(name=name)
        self._graph.add_node(node)

    def add_edge(self, from_node: str, to_node: str) -> None:
        edge = Edge(
            from_node=self._graph.nodes[from_node],
            to_node=self._graph.nodes[to_node],
        )
        self._graph.add_edge(edge)

    def sorted_stages(self) -> list[list[str]]:
        return self._graph.topological_sort()
