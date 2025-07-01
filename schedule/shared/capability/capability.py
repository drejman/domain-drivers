from __future__ import annotations

from enum import StrEnum

import attrs as a


class CapabilityType(StrEnum):
    SKILL = "SKILL"
    PERMISSION = "PERMISSION"
    ASSET = "ASSET"


@a.define(frozen=True)
class Capability:
    name: str
    type: CapabilityType

    @classmethod
    def skill(cls, name: str) -> Capability:
        return cls(name=name, type=CapabilityType.SKILL)

    @classmethod
    def skills(cls, *names: str) -> set[Capability]:
        return {cls.skill(name) for name in names}

    @classmethod
    def permission(cls, name: str) -> Capability:
        return cls(name=name, type=CapabilityType.PERMISSION)

    @classmethod
    def permissions(cls, *names: str) -> set[Capability]:
        return {cls.permission(name) for name in names}

    @classmethod
    def asset(cls, name: str) -> Capability:
        return cls(name=name, type=CapabilityType.ASSET)

    @classmethod
    def assets(cls, *names: str) -> set[Capability]:
        return {cls.asset(name) for name in names}

    def is_of_type(self, type: CapabilityType) -> bool:  # noqa: A002
        return self.type == type

    def is_a_skill(self) -> bool:
        return self.type == CapabilityType.SKILL

    def is_a_permission(self) -> bool:
        return self.type == CapabilityType.PERMISSION
