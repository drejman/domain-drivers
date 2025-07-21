# pyright: reportExplicitAny=false, reportAny=false
# TODO: reconsider typing  # noqa: FIX002, TD002

import inspect
import logging
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import Executor
from concurrent.futures._base import Future
from dataclasses import dataclass
from typing import Any, ClassVar, Final, ParamSpec, TypeVar, override

from lagom import Container

from .event import Event
from .event_publisher import EventPublisher

logger = logging.getLogger(__name__)

type ClassWithEventHandlers = type[object]
type EventHandler = Callable[[Any, Event], None]


P = ParamSpec("P")
T = TypeVar("T")


class SyncExecutor(Executor):
    @override
    def submit(self, fn: Callable[P, T], /, *args: P.args, **kwargs: P.kwargs) -> Future[T]:
        result = fn(*args, **kwargs)
        future: Future[T] = Future()
        future.set_result(result)
        return future


@dataclass(frozen=True)
class ClassBasedHandler:
    class_: ClassWithEventHandlers
    method: EventHandler


EVENT_HANDLER_EVENT_TYPE_ATTR: Final = "__event_bus_handling_event__"

F = TypeVar("F", bound=Callable[..., Any])


class EventBus(EventPublisher):
    __handlers: ClassVar[dict[type[Event], list[ClassBasedHandler]]] = defaultdict(list)

    def __init__(self, container: Container, executor: Executor) -> None:
        self._container: Container = container
        self._executor: Executor = executor

    @override
    def publish(self, event: Event) -> None:
        handlers = self.__handlers[type(event)]
        for handler in handlers:

            def task(handler: ClassBasedHandler = handler, event: Event = event) -> None:
                try:
                    instance = self._container.resolve(handler.class_)
                    handler.method(instance, event)
                except Exception:
                    logger.exception("Error while handling event %r in handler %r", event, handler)

            _ = self._executor.submit(task)

    @classmethod
    def has_event_handlers(cls, class_: type[T]) -> type[T]:
        # iter over methods
        # if method has __event_bus_handling_event__ attribute
        # add to __handlers
        methods = inspect.getmembers(class_, predicate=inspect.isfunction)
        event_handlers = [method for _, method in methods if hasattr(method, EVENT_HANDLER_EVENT_TYPE_ATTR)]
        for handler in event_handlers:
            event_type = getattr(handler, EVENT_HANDLER_EVENT_TYPE_ATTR)
            cls.__handlers[event_type].append(ClassBasedHandler(class_, handler))

        return class_

    @classmethod
    def async_event_handler(cls, func: F) -> F:
        arg_spec = inspect.getfullargspec(func)
        annotations = {k: v for k, v in arg_spec.annotations.items() if k != "return"}
        if len(annotations) != 1:
            msg = "Event handler must accept exactly one argument"
            raise ValueError(msg)

        event_type = next(iter(annotations.values()))
        setattr(func, EVENT_HANDLER_EVENT_TYPE_ATTR, event_type)
        return func
