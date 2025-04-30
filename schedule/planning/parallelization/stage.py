from __future__ import annotations

from datetime import timedelta
from typing import override

import attrs as a

from schedule.shared.resource_name import ResourceName


@a.define(frozen=True)
class Stage:
    _name: str
    _dependencies: set[Stage] = a.field(factory=set, eq=False, hash=False)
    _resources: set[ResourceName] = a.field(factory=set, eq=False, hash=False)
    _duration: timedelta = a.field(factory=timedelta, eq=False, hash=False)

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

    @property
    def duration(self) -> timedelta:
        return self._duration

    def depends_on(self, stage: Stage) -> Stage:
        new_dependencies = self._dependencies.union({stage})
        self._dependencies.add(stage)
        return Stage(self._name, new_dependencies, self._resources, self._duration)

    def with_chosen_resource_capabilities(self, *resources: ResourceName) -> Stage:
        return Stage(self._name, self._dependencies, set(resources), self._duration)

    def of_duration(self, duration: timedelta) -> Stage:
        return Stage(self._name, self._dependencies, self._resources, duration)

    @override
    def __str__(self) -> str:
        return self._name
