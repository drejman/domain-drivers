from __future__ import annotations

from uuid import UUID, uuid4

import attrs as a


@a.define(frozen=True)
class DeviceId:
    _device_id: UUID = a.field(alias="uuid")

    @staticmethod
    def new_one() -> DeviceId:
        return DeviceId(uuid4())

    @property
    def id(self) -> UUID:
        return self._device_id
