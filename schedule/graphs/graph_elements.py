import attrs as a


@a.define(frozen=True)
class Node:
    name: str


@a.define(frozen=True)
class Edge:
    from_node: Node
    to_node: Node
