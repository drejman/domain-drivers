from datetime import timedelta
from decimal import Decimal
from typing import Self, TypeVar, cast, final, override
from uuid import UUID

from cattrs.preconf.json import JsonConverter, make_converter  # pyright: ignore[reportUnknownVariableType]
from sqlalchemy import Dialect, types
from sqlalchemy.dialects.postgresql import JSONB

T = TypeVar("T")


def timedelta_to_seconds(td: timedelta) -> float:
    return td.total_seconds()


def seconds_to_timedelta(val: float, _: type) -> timedelta:
    return timedelta(seconds=val)


def uuid_to_string(uuid: UUID) -> str:
    return str(uuid)


def string_to_uuid(string: str, _: type) -> UUID:
    return UUID(string)


def decimal_to_string(decimal: Decimal) -> str:
    return str(decimal)


def string_to_decimal(string: str, _: type) -> Decimal:
    return Decimal(string)


@final
class AsJSON[T](types.TypeDecorator[T]):
    """Will serialize to JSON and back everything that cattrs handles."""

    impl = JSONB
    cache_ok = True

    _converter: JsonConverter  # pyright: ignore[reportUninitializedInstanceVariable]
    _type: type[T]  # pyright: ignore[reportUninitializedInstanceVariable]

    @override
    def __class_getitem__(cls, type_: type[T]) -> Self:
        converter = make_converter()

        converter.register_unstructure_hook(timedelta, timedelta_to_seconds)
        converter.register_structure_hook(timedelta, seconds_to_timedelta)

        converter.register_unstructure_hook(UUID, uuid_to_string)
        converter.register_structure_hook(UUID, string_to_uuid)

        converter.register_unstructure_hook(Decimal, decimal_to_string)
        converter.register_structure_hook(Decimal, string_to_decimal)

        specialized_class = type(
            f"JSONSerializable[{type_.__name__}]",
            (cls,),
            {"_converter": converter, "_type": type_},
        )
        return cast(Self, specialized_class)

    @override
    def process_bind_param(self, value: T | None, dialect: Dialect) -> JSONB | None:
        if value is None:
            return value

        return cast(JSONB, self._converter.unstructure(value))

    @override
    def process_result_value(self, value: str | None, dialect: Dialect) -> T | None:
        if value is None:
            return value

        return self._converter.structure(value, self._type)
