from __future__ import annotations

from typing import TYPE_CHECKING, override

import attrs as a

if TYPE_CHECKING:
    from .node import Node


@a.define(frozen=True)
class Edge[T]:
    _source: Node[T]
    _target: Node[T]

    @override
    def __str__(self) -> str:
        return f"({self._source.name} -> {self._target.name})"

    @property
    def source(self) -> Node[T]:
        return self._source

    @property
    def target(self) -> Node[T]:
        return self._target
