from __future__ import annotations

import abc
from itertools import chain
from typing import override

from schedule.allocation.capability_scheduling import CapabilitySelector
from schedule.resource import EmployeeSummary


class EmployeeAllocationPolicy(abc.ABC):
    @abc.abstractmethod
    def simultaneous_capabilities_of(self, summary: EmployeeSummary) -> list[CapabilitySelector]:
        pass

    @staticmethod
    def default_policy() -> EmployeeAllocationPolicy:
        return DefaultPolicy()

    @staticmethod
    def permissions_in_multiple_projects(how_many: int) -> EmployeeAllocationPolicy:
        return PermissionsInMultipleProjectsPolicy(how_many)

    @staticmethod
    def one_of_skills() -> EmployeeAllocationPolicy:
        return OneOfSkillsPolicy()

    @staticmethod
    def simultaneous(*policies: EmployeeAllocationPolicy) -> EmployeeAllocationPolicy:
        return CompositePolicy(*policies)


class DefaultPolicy(EmployeeAllocationPolicy):
    @override
    def simultaneous_capabilities_of(self, summary: EmployeeSummary) -> list[CapabilitySelector]:
        all_capabilities = summary.skills | summary.permissions
        return [CapabilitySelector.can_perform_one_of(all_capabilities)]


class PermissionsInMultipleProjectsPolicy(EmployeeAllocationPolicy):
    def __init__(self, how_many: int) -> None:
        self._how_many: int = how_many

    @override
    def simultaneous_capabilities_of(self, summary: EmployeeSummary) -> list[CapabilitySelector]:
        flattened = list(chain(*[[permission] * self._how_many for permission in summary.permissions]))
        return [CapabilitySelector.can_just_perform(permisson) for permisson in flattened]


class OneOfSkillsPolicy(EmployeeAllocationPolicy):
    @override
    def simultaneous_capabilities_of(self, summary: EmployeeSummary) -> list[CapabilitySelector]:
        return [CapabilitySelector.can_perform_one_of(summary.skills)]


class CompositePolicy(EmployeeAllocationPolicy):
    def __init__(self, *policies: EmployeeAllocationPolicy) -> None:
        self._policies: tuple[EmployeeAllocationPolicy, ...] = policies

    @override
    def simultaneous_capabilities_of(self, summary: EmployeeSummary) -> list[CapabilitySelector]:
        return list(chain(*[policy.simultaneous_capabilities_of(summary) for policy in self._policies]))
