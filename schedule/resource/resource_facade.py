from schedule.resource.device.device_facade import DeviceFacade
from schedule.resource.employee.employee_facade import EmployeeFacade
from schedule.shared.capability import Capability


class ResourceFacade:
    def __init__(self, employee_facade: EmployeeFacade, device_facade: DeviceFacade) -> None:
        self._employee_facade: EmployeeFacade = employee_facade
        self._device_facade: DeviceFacade = device_facade

    def find_all_capabilities(self) -> list[Capability]:
        employee_capabilities = self._employee_facade.find_all_capabilities()
        device_capabilities = self._device_facade.find_all_capabilities()
        return employee_capabilities + device_capabilities
