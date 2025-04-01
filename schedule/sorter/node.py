from __future__ import annotations

import attrs as a


@a.define(frozen=True)
class Node[T]:
    name: str
    content: T = a.field(eq=False, hash=False)
    predecessors: frozenset[Node[T]] = a.field(factory=frozenset, eq=False, hash=False)

    def add_predecessors(self, *predecessors: Node[T]) -> Node[T]:
        updated_predecessors = self.predecessors.union({*predecessors})
        return Node(self.name, self.content, updated_predecessors)
