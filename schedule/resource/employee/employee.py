from typing import ClassVar, final

from sqlalchemy.orm import Mapped, mapped_column

from schedule.shared.capability.capability import Capability
from schedule.shared.sqla_repository import AsJSON, EmbeddedUUID, mapper_registry

from .employee_id import EmployeeId
from .seniority import Seniority


@final
@mapper_registry.mapped_as_dataclass()
class Employee:
    __tablename__ = "employees"

    _id: Mapped[EmployeeId] = mapped_column(EmbeddedUUID[EmployeeId], primary_key=True)
    _version: Mapped[int] = mapped_column(name="version")
    name: Mapped[str]
    last_name: Mapped[str]
    seniority: Mapped[Seniority] = mapped_column(AsJSON[Seniority])
    _capabilities: Mapped[set[Capability]] = mapped_column(AsJSON[set[Capability]], name="capabilities")

    __mapper_args__: ClassVar[dict[str, Mapped[int]]] = {"version_id_col": _version}

    def __init__(
        self, employee_id: EmployeeId, name: str, last_name: str, seniority: Seniority, capabilities: set[Capability]
    ) -> None:
        self._id = employee_id
        self.name = name
        self.last_name = last_name
        self.seniority = seniority
        self._capabilities = capabilities

    @property
    def capabilities(self) -> set[Capability]:
        return self._capabilities

    @property
    def id(self) -> EmployeeId:
        return self._id
