from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

from dateutil import relativedelta


@dataclass(frozen=True, eq=True)
class TimeSlot:
    from_: datetime
    to: datetime

    @staticmethod
    def empty() -> TimeSlot:
        return TimeSlot(datetime.min, datetime.min)

    @classmethod
    def create_daily_time_slot_at_utc(cls, year: int, month: int, day: int) -> TimeSlot:
        this_day = date(year, month, day)
        day_start_in_utc = time.min.replace(tzinfo=UTC)
        from_ = datetime.combine(this_day, day_start_in_utc)
        return TimeSlot(from_, from_ + timedelta(days=1))

    @classmethod
    def create_monthly_time_slot_at_utc(cls, year: int, month: int) -> TimeSlot:
        start_of_month = date(year, month, 1)
        end_of_month = start_of_month + relativedelta.relativedelta(months=1)
        day_start_in_utc = time.min.replace(tzinfo=UTC)
        from_ = datetime.combine(start_of_month, day_start_in_utc)
        to = datetime.combine(end_of_month, day_start_in_utc)
        return TimeSlot(from_, to)

    def within(self, other: TimeSlot) -> bool:
        return not self.from_ < other.from_ and not self.to > other.to

    def overlaps(self, other: TimeSlot) -> bool:
        return self.from_ <= other.to and self.to >= other.from_

    def leftover_after_removing_common_with(self, other: TimeSlot) -> tuple[TimeSlot, ...]:
        result: list[TimeSlot] = []
        if self == other:
            return ()
        if not other.overlaps(self):
            return (self, other)
        if self.from_ < other.from_:
            result.append(TimeSlot(self.from_, other.from_))
        elif other.from_ < self.from_:
            result.append(TimeSlot(other.from_, self.from_))
        if self.to > other.to:
            result.append(TimeSlot(other.to, self.to))
        elif other.to > self.to:
            result.append(TimeSlot(self.to, other.to))
        return tuple(result)

    def common_part_with(self, other: TimeSlot) -> TimeSlot:
        if not self.overlaps(other):
            return TimeSlot(self.from_, self.from_)
        return TimeSlot(max(self.from_, other.from_), min(self.to, other.to))

    @property
    def duration(self) -> timedelta:
        return self.to - self.from_

    def stretch(self, duration: timedelta) -> TimeSlot:
        return TimeSlot(self.from_ - duration, self.to + duration)

    def is_empty(self) -> bool:
        return self.from_ == self.to
