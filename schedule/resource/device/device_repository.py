import itertools

from schedule.shared.capability import Capability
from schedule.shared.sqla_repository import SQLAlchemyRepository

from .device import Device
from .device_id import DeviceId
from .device_summary import DeviceSummary


class DeviceRepository(SQLAlchemyRepository[Device, DeviceId]):
    def find_summary(self, device_id: DeviceId) -> DeviceSummary:
        device = self.get(device_id)
        return DeviceSummary(device.id, device.model, device.capabilities)

    def find_all_capabilities(self) -> list[Capability]:
        devices = self.get_all()
        capabilities_sets = [device.capabilities for device in devices]
        return list(itertools.chain(*capabilities_sets))
