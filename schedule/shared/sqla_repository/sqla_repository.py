from collections.abc import Sequence
from typing import TYPE_CHECKING, Self, cast

from sqlalchemy import inspect, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from sqlalchemy.sql.schema import Column


class SQLAlchemyRepository[TModel, TIdentity]:
    class NotFoundError(Exception):
        pass

    def __class_getitem__(cls, type_arg: tuple[type[TModel], type[TIdentity]]) -> Self:
        model_type, identity_type = type_arg

        mapper = inspect(model_type)
        if not mapper:
            msg = f"Model type {model_type} is not mapped correctly"
            raise RuntimeError(msg)
        primary_key_columns: tuple[Column[TIdentity], ...] = mapper.primary_key  # pyright: ignore [reportAny]
        if len(primary_key_columns) != 1:
            msg = "Only single column primary keys are supported"
            raise RuntimeError(msg)
        pk_col = primary_key_columns[0]

        specialized_class = type(
            f"SQLAlchemyRepository[{model_type.__name__}, {identity_type}]",
            (cls,),
            {"_type": model_type, "_pk_col": pk_col},
        )
        return cast("Self", specialized_class)

    def __init__(self, session: Session) -> None:
        self._session: Session = session
        self._type: type[TModel]
        self._pk_col: Column[TIdentity]

    def add(self, model: TModel) -> None:
        self._session.add(model)
        self._session.flush([model])

    def add_all(self, models: Sequence[TModel]) -> None:
        self._session.add_all(models)
        self._session.flush(models)

    def exists(self, id: TIdentity) -> bool:  # noqa: A002
        stmt = select(self._pk_col).filter(self._pk_col == id).exists()
        return self._session.execute(select(stmt)).scalar() or False

    def get(self, id: TIdentity) -> TModel:  # noqa: A002
        stmt = select(self._type).filter_by(_id=id)
        try:
            return self._session.execute(stmt).scalar_one()
        except NoResultFound as e:
            raise self.NotFoundError from e

    def get_all(self, ids: list[TIdentity] | None = None) -> Sequence[TModel]:
        stmt = select(self._type) if ids is None else select(self._type).filter(self._type._id.in_(ids))  # type: ignore[attr-defined] # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue] # noqa: SLF001
        return self._session.execute(stmt).scalars().all()
