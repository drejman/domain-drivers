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
    def permission(cls, name: str) -> Capability:
        return cls(name=name, type=CapabilityType.PERMISSION)

    @classmethod
    def asset(cls, name: str) -> Capability:
        return cls(name=name, type=CapabilityType.ASSET)
