from collections.abc import Sequence
from typing import Self, cast

from sqlalchemy import select
from sqlalchemy.orm import Session


class SQLAlchemyRepository[TModel, TIdentity]:
    _session: Session
    _type: type[TModel]  # pyright: ignore[reportUninitializedInstanceVariable]

    def __class_getitem__(cls, type_arg: tuple[type[TModel], type[TIdentity]]) -> Self:
        model_type, identity_type = type_arg

        specialized_class = type(
            f"SQLAlchemyRepository[{model_type.__name__}, {identity_type}]",
            (cls,),
            {"_type": model_type},
        )
        return cast(Self, specialized_class)

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, model: TModel) -> None:
        self._session.add(model)
        self._session.flush([model])

    def get(self, id: TIdentity) -> TModel:  # noqa: A002
        stmt = select(self._type).filter_by(_id=id)
        return self._session.execute(stmt).scalar_one()

    def get_all(self, ids: list[TIdentity]) -> Sequence[TModel]:
        stmt = select(self._type).filter(self._type._id.in_(ids))  # type: ignore[attr-defined] # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue] # noqa: SLF001
        return self._session.execute(stmt).scalars().all()
