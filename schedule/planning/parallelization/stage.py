from __future__ import annotations

from typing import override

import attrs as a


@a.define
class Stage:
    _name: str
    _dependencies: set[Stage] = a.field(factory=set, eq=False)
    _resources: set[ResourceName] = a.field(factory=set, eq=False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def dependencies(self) -> set[Stage]:
        return self._dependencies

    @property
    def has_dependencies(self) -> bool:
        return len(self._dependencies) > 0

    @property
    def resources(self) -> set[ResourceName]:
        return self._resources

    @property
    def count_of_resources(self) -> int:
        return len(self._resources)

    def depends_on(self, stage: Stage) -> Stage:
        self._dependencies.add(stage)
        return self

    @override
    def __hash__(self) -> int:
        return hash(self._name)

    @override
    def __str__(self) -> str:
        return self._name

    def with_chosen_resource_capabilities(self, *resources: ResourceName) -> Stage:
        self._resources |= set(resources)
        return self


ResourceName = str
