from __future__ import annotations

from uuid import UUID, uuid4

import attrs as a


@a.define(frozen=True)
class EmployeeId:
    _employee_id: UUID = a.field(alias="uuid")

    @staticmethod
    def new_one() -> EmployeeId:
        return EmployeeId(uuid4())

    @property
    def id(self) -> UUID:
        return self._employee_id
