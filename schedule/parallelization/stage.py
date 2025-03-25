from typing import Self

import attrs as a


@a.define
class Stage:
    _name: str
    _dependencies: set[Self] = a.field(factory=set, init=False, eq=False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def dependencies(self):
        return self._dependencies

    def depends_on(self, stage: Self) -> Self:
        self._dependencies.add(stage)
        return self

    def __hash__(self):
        return hash(self._name)

    def __str__(self):
        return self._name
