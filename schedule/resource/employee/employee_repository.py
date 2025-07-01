import itertools

from schedule.shared.capability import Capability
from schedule.shared.sqla_repository import SQLAlchemyRepository

from .employee import Employee
from .employee_id import EmployeeId
from .employee_summary import EmployeeSummary


class EmployeeRepository(SQLAlchemyRepository[Employee, EmployeeId]):
    def find_summary(self, employee_id: EmployeeId) -> EmployeeSummary:
        employee = self.get(employee_id)
        skills = {capability for capability in employee.capabilities if capability.is_a_skill()}
        permissions = {capability for capability in employee.capabilities if capability.is_a_permission()}
        return EmployeeSummary(
            id=employee.id,
            name=employee.name,
            last_name=employee.last_name,
            seniority=employee.seniority,
            skills=skills,
            permissions=permissions,
        )

    def find_all_capabilities(self) -> list[Capability]:
        employees = self.get_all()
        capabilities_sets = (employee.capabilities for employee in employees)
        return list(itertools.chain(*capabilities_sets))
