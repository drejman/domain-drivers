import abc

from .event import Event


class EventPublisher(abc.ABC):
    @abc.abstractmethod
    def publish(self, event: Event) -> None:
        pass
