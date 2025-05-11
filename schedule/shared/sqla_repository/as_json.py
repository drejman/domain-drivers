from datetime import timedelta
from typing import Self, TypeVar, cast, final, override
from uuid import UUID

from cattrs.preconf.json import JsonConverter, make_converter  # pyright: ignore[reportUnknownVariableType]
from sqlalchemy import Dialect, types

from schedule.shared.typing_extensions import JSON

T = TypeVar("T")


def timedelta_to_seconds(td: timedelta) -> float:
    return td.total_seconds()


def seconds_to_timedelta(val: float, _: type) -> timedelta:
    return timedelta(seconds=val)


def uuid_to_string(uuid: UUID) -> str:
    return str(uuid)


def string_to_uuid(string: str, _: type) -> UUID:
    return UUID(string)


@final
class AsJSON[T](types.TypeDecorator[T]):
    """Will serialize to JSON and back everything that cattrs handles."""

    impl = types.JSON
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

        specialized_class = type(
            f"JSONSerializable[{type_.__name__}]",
            (cls,),
            {"_converter": converter, "_type": type_},
        )
        return cast(Self, specialized_class)

    @override
    def process_bind_param(self, value: T | None, dialect: Dialect) -> JSON | None:
        if value is None:
            return value

        return cast(JSON, self._converter.dumps(value))

    @override
    def process_result_value(self, value: str | None, dialect: Dialect) -> T | None:
        if value is None:
            return value

        return self._converter.loads(value, self._type)
