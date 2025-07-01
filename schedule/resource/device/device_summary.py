from collections.abc import Iterable

import attrs as a

from schedule.shared.capability import Capability

from .device_id import DeviceId


def freeze_capabilities(capabilities: Iterable[Capability]) -> frozenset[Capability]:
    return frozenset(capabilities)


@a.define(frozen=True)
class DeviceSummary:
    id: DeviceId
    model: str
    assets: frozenset[Capability] = a.field(converter=freeze_capabilities)
