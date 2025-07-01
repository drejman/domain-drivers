from collections.abc import Iterable

import attrs as a

from schedule.shared.capability import Capability

from .employee_id import EmployeeId
from .seniority import Seniority


def freeze_capabilities(capabilities: Iterable[Capability]) -> frozenset[Capability]:
    return frozenset(capabilities)


@a.define(frozen=True)
class EmployeeSummary:
    id: EmployeeId
    name: str
    last_name: str
    seniority: Seniority
    skills: frozenset[Capability] = a.field(converter=freeze_capabilities)
    permissions: frozenset[Capability] = a.field(converter=freeze_capabilities)
