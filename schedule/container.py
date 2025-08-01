from lagom import Container

from schedule.shared.event import EventBus, EventPublisher, SyncExecutor


def build() -> Container:
    container = Container()
    executor = SyncExecutor()
    container[EventPublisher] = lambda c: EventBus(c, executor)  # type: ignore[type-abstract]
    container[EventBus] = lambda c: EventBus(c, executor)
    return container
