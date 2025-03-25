
from .graph_elements import Node, Edge


class Graph:
    nodes: dict[str, Node]
    edges: list[Edge]

    def __init__(self) -> None:
        self.nodes = {}
        self.edges = []

    def add_node(self, node: Node) -> None:
        if node.name not in self.nodes:
            self.nodes[node.name] = node

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

    def topological_sort(self) -> list[list[str]]:
        graph: dict[str, list[str]] = {node.name: [] for node in self.nodes.values()}
        in_degree = {node.name: 0 for node in self.nodes.values()}

        for edge in self.edges:
            graph[edge.from_node.name].append(edge.to_node.name)
            in_degree[edge.to_node.name] += 1

        zero_in_degree_nodes = [
            node.name for node in self.nodes.values() if in_degree[node.name] == 0
        ]
        sorted_stages = []

        while zero_in_degree_nodes:
            current_level = []
            next_zero_in_degree_nodes = []

            for node_name in zero_in_degree_nodes:
                current_level.append(node_name)
                for neighbor in graph[node_name]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_zero_in_degree_nodes.append(neighbor)

            sorted_stages.append(current_level)
            zero_in_degree_nodes = next_zero_in_degree_nodes

        return sorted_stages
