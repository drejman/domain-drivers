from datetime import timedelta

import pytest

from schedule.shared.timeslot.time_slot import TimeSlot

from ..availability_facade import AvailabilityFacade
from ..calendar import Calendar
from ..owner import Owner
from ..resource_id import ResourceId


class TestAvailabilityFacade:
    def test_creates_availability_slots(self, availability_facade: AvailabilityFacade) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        availability_facade.create_resource_slots(resource_id, one_day)

        entire_month = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)
        monthly_calendar = availability_facade.load_calendar(resource_id, entire_month)
        assert monthly_calendar == Calendar.with_available_slots(resource_id, one_day)

    @pytest.mark.xfail(reason="not yet correctly implemented")
    def test_creates_already_existing_availability_slots(self, availability_facade: AvailabilityFacade) -> None:
        resource_id = ResourceId.new_one()
        jan_1 = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        jan_2 = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 2)
        jan_1_2 = TimeSlot(jan_1.from_, jan_2.to)
        availability_facade.create_resource_slots(resource_id, jan_1)

        availability_facade.create_resource_slots(resource_id, jan_1_2)

        grouped = availability_facade.find(resource_id, jan_2)
        assert len(grouped) == 96

    def test_blocks_availabilities(self, availability_facade: AvailabilityFacade) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)

        result = availability_facade.block(resource_id, one_day, owner)

        assert result is True
        entire_month = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)
        monthly_calendar = availability_facade.load_calendar(resource_id, entire_month)
        assert len(monthly_calendar.available_slots()) == 0
        assert monthly_calendar.taken_by(owner) == (one_day,)

    def test_cant_block_when_no_slots_created(self, availability_facade: AvailabilityFacade) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()

        result = availability_facade.block(resource_id, one_day, owner)

        assert result is False

    def test_disable_availabilities(self, availability_facade: AvailabilityFacade) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)

        result = availability_facade.disable(resource_id, one_day, owner)

        assert result is True
        availabilities = availability_facade.find(resource_id, one_day)
        assert len(availabilities) == 96
        assert availabilities.is_disabled_entirely_by(owner)

    def test_cannot_block_when_even_just_small_segment_of_requested_slot_is_blocked(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)
        fifteen_minutes = TimeSlot(one_day.from_, one_day.from_ + timedelta(minutes=15))
        _ = availability_facade.block(resource_id, fifteen_minutes, owner)

        result = availability_facade.block(resource_id, one_day, Owner.new_one())

        assert result is False
        availabilites = availability_facade.find(resource_id, fifteen_minutes)
        assert availabilites.blocked_entirely_by(owner)

    def test_release_availability(self, availability_facade: AvailabilityFacade) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes = TimeSlot(one_day.from_, one_day.from_ + timedelta(minutes=15))
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, fifteen_minutes)
        _ = availability_facade.block(resource_id, fifteen_minutes, owner)

        result = availability_facade.block(resource_id, one_day, owner)

        assert result is True
        availabilities = availability_facade.find(resource_id, one_day)
        assert availabilities.is_entirely_available()

    def test_cant_release_when_just_part_of_slot_is_owned_by_another_requester(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        jan_1 = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        jan_2 = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 2)
        jan_1_2 = TimeSlot(jan_1.from_, jan_2.to)
        jan_1_owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, jan_1_2)
        _ = availability_facade.block(resource_id, jan_1, jan_1_owner)
        jan_2_owner = Owner.new_one()
        _ = availability_facade.block(resource_id, jan_2, jan_2_owner)

        result = availability_facade.release(resource_id, jan_1_2, jan_1_owner)

        assert result is False
        availabilities = availability_facade.find(resource_id, jan_1)
        assert availabilities.blocked_entirely_by(jan_1_owner)

    def test_one_segment_can_taken_by_someone_else_after_releasing(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes = TimeSlot(one_day.from_, one_day.from_ + timedelta(minutes=15))
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)
        _ = availability_facade.block(resource_id, one_day, owner)
        _ = availability_facade.release(resource_id, fifteen_minutes, owner)

        new_requester = Owner.new_one()
        result = availability_facade.block(resource_id, fifteen_minutes, new_requester)

        assert result is True
        daily_calendar = availability_facade.load_calendar(resource_id, one_day)
        assert len(daily_calendar.available_slots()) == 0
        taken_by_owner = daily_calendar.taken_by(owner)
        assert taken_by_owner == one_day.leftover_after_removing_common_with(fifteen_minutes)
        assert daily_calendar.taken_by(new_requester) == (fifteen_minutes,)
