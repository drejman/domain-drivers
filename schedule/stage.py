from typing import Self

import attrs as a


@a.define
class Stage:
    _name: str
    _stages_before: list[Self] = a.field(factory=list)

    @property
    def name(self) -> str:
        return self._name

    @property
    def dependencies(self) -> list[Self]:
        return self._stages_before

    def depends_on(self, stage: Self) -> None:
        self._stages_before.append(stage)
