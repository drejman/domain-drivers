from schedule.shared.capability import Capability

from .employee import Employee
from .employee_id import EmployeeId
from .employee_repository import EmployeeRepository
from .employee_summary import EmployeeSummary
from .seniority import Seniority


class EmployeeFacade:
    def __init__(self, repository: EmployeeRepository) -> None:
        self._repository: EmployeeRepository = repository

    def find_employee(self, employee_id: EmployeeId) -> EmployeeSummary:
        return self._repository.find_summary(employee_id)

    def find_all_capabilities(self) -> list[Capability]:
        return self._repository.find_all_capabilities()

    def add_employee(
        self,
        name: str,
        last_name: str,
        seniority: Seniority,
        skills: set[Capability],
        permissions: set[Capability],
    ) -> EmployeeId:
        employee_id = EmployeeId.new_one()
        capabilities = skills | permissions
        employee = Employee(employee_id, name, last_name, seniority, capabilities)
        self._repository.add(employee)
        return employee.id

    # TODO: add vacation, call availability  # noqa: FIX002, TD002
    # TODO: add sick leave, call availability  # noqa: FIX002, TD002
    # change skills
