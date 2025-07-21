from lagom import Container

from schedule.shared.event import EventBus, EventPublisher


def build() -> Container:
    container = Container()
    container[EventPublisher] = EventBus  # type: ignore[type-abstract]
    return container
