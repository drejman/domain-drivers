from functools import singledispatchmethod
from typing import overload

from schedule.resource.device import DeviceFacade, DeviceId, DeviceSummary
from schedule.resource.employee import EmployeeFacade, EmployeeId, Seniority
from schedule.resource.employee.employee_summary import EmployeeSummary
from schedule.shared.capability import Capability

ResourceId = DeviceId | EmployeeId
ResourceSummary = DeviceSummary | EmployeeSummary


class ResourceFacade:
    def __init__(self, employee_facade: EmployeeFacade, device_facade: DeviceFacade) -> None:
        self._employee_facade: EmployeeFacade = employee_facade
        self._device_facade: DeviceFacade = device_facade

    def add_device(self, model: str, assets: set[Capability]) -> DeviceId:
        return self._device_facade.create_device(model, assets)

    def add_employee(
        self, name: str, last_name: str, seniority: Seniority, skills: set[Capability], permissions: set[Capability]
    ) -> EmployeeId:
        return self._employee_facade.add_employee(
            name=name, last_name=last_name, seniority=seniority, skills=skills, permissions=permissions
        )

    def find_all_capabilities(self) -> list[Capability]:
        employee_capabilities = self._employee_facade.find_all_capabilities()
        device_capabilities = self._device_facade.find_all_capabilities()
        return employee_capabilities + device_capabilities

    @overload
    def find_resource_summary(self, resource_id: DeviceId) -> DeviceSummary: ...

    @overload
    def find_resource_summary(self, resource_id: EmployeeId) -> EmployeeSummary: ...

    def find_resource_summary(self, resource_id: ResourceId) -> ResourceSummary:
        return self._find_resource_summary(resource_id)

    @singledispatchmethod
    def _find_resource_summary(self, resource_id: ResourceId) -> ResourceSummary:
        msg = f"{type(resource_id)} is not a valid ResourceId type: supported are {ResourceId}"
        raise TypeError(msg)

    @_find_resource_summary.register
    def _find_device_summary(self, resource_id: DeviceId) -> DeviceSummary:
        return self._device_facade.find_device(resource_id)

    @_find_resource_summary.register
    def _find_employee_summary(self, resource_id: EmployeeId) -> EmployeeSummary:
        return self._employee_facade.find_employee(resource_id)
