from typing import ClassVar, final

from sqlalchemy.orm import Mapped, mapped_column

from schedule.shared.capability.capability import Capability
from schedule.shared.sqla_repository import AsJSON, EmbeddedUUID, mapper_registry

from .device_id import DeviceId


@final
@mapper_registry.mapped_as_dataclass()
class Device:
    __tablename__ = "devices"

    _id: Mapped[DeviceId] = mapped_column(EmbeddedUUID[DeviceId], primary_key=True)
    _version: Mapped[int] = mapped_column(name="version")
    model: Mapped[str]
    _capabilities: Mapped[set[Capability]] = mapped_column(AsJSON[set[Capability]], name="capabilities")

    __mapper_args__: ClassVar[dict[str, Mapped[int]]] = {"version_id_col": _version}

    def __init__(self, device_id: DeviceId, model: str, capabilities: set[Capability]) -> None:
        self._id = device_id
        self.model = model
        self._capabilities = capabilities

    @property
    def capabilities(self) -> set[Capability]:
        return self._capabilities

    @property
    def id(self) -> DeviceId:
        return self._id
