from typing import Any, Protocol, Self, cast, override
from uuid import UUID

from sqlalchemy import Dialect, types


class EmbeddableUUID(Protocol):
    def __init__(self, uuid: UUID, *args: Any, **kwargs: Any) -> None: ...  # pyright: ignore [reportExplicitAny, reportAny]  # noqa: ANN401

    @property
    def id(self) -> UUID: ...


class EmbeddedUUID[T: EmbeddableUUID](types.TypeDecorator[T]):
    """Manages identifiers as UUIDs in the database.

    Type is expected to have a `id` attribute that is a UUID.
    `.id` can be read-only, e.g. property.

    It must be possible for the type to be constructed with
    a single argument of UUID type.
    """

    impl = types.UUID(as_uuid=True)  # pyright: ignore[reportUnannotatedClassAttribute]
    cache_ok = True  # pyright: ignore[reportUnannotatedClassAttribute]

    _type: type[T]  # pyright: ignore[reportUninitializedInstanceVariable]

    @override
    def __class_getitem__(cls, type_: type[T]) -> Self:
        specialized_class = type(
            f"EmbeddedUUID[{type_.__name__}]",
            (cls,),
            {"_type": type_, "cache_ok": True},
        )
        return cast(Self, specialized_class)

    @override
    def process_bind_param(self, value: T | None, dialect: Dialect) -> UUID | None:
        if value is not None:
            return value.id
        return value

    @override
    def process_result_value(self, value: UUID | None, dialect: Dialect) -> T | None:
        if value is not None:
            return self._type(value)
        return value
