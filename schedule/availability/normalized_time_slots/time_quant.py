from __future__ import annotations

from datetime import timedelta
from functools import partial
from typing import ClassVar

import attrs as a


def _convert_minutes_to_timedelta(minutes: int) -> timedelta:
    return timedelta(minutes=minutes)


def _validate_minutes(
    instance: TimeQuantumInMinutes,  # pyright: ignore[reportUnusedParameter]  # noqa: ARG001
    attribute: a.Attribute[timedelta],  # pyright: ignore[reportUnusedParameter]  # noqa: ARG001
    value: timedelta,
    default_duration: timedelta,
) -> timedelta:
    if value.total_seconds() <= 0:
        error = "SegmentInMinutesDuraton must be greater than 0"
        raise ValueError(error)
    if value.total_seconds() % default_duration.total_seconds() != 0:
        error = f"SegmentInMinutesDuration must be a multiple of {default_duration}"
        raise ValueError(error)
    return value


@a.frozen
class TimeQuantumInMinutes:
    DEFAULT_QUANTUM_DURATION_IN_MINUTES: ClassVar[timedelta] = timedelta(minutes=15)

    _value: timedelta = a.field(
        alias="minutes",
        converter=_convert_minutes_to_timedelta,
        validator=partial(_validate_minutes, default_duration=DEFAULT_QUANTUM_DURATION_IN_MINUTES),
    )

    @property
    def value(self) -> timedelta:
        return self._value

    @classmethod
    def default_segment(cls) -> TimeQuantumInMinutes:
        return TimeQuantumInMinutes(minutes=int(cls.DEFAULT_QUANTUM_DURATION_IN_MINUTES.total_seconds() / 60))
