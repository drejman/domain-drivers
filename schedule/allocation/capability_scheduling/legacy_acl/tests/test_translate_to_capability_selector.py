import factory  # type: ignore

from schedule.allocation.capability_scheduling.capability_selector import CapabilitySelector
from schedule.shared.capability import Capability
from schedule.shared.timeslot import TimeSlot

from ..employee_data_from_legacy_esb_message import (
    EmployeeDataFromLegacyEsbMessage,
)
from ..translate_to_capability_selector import (
    translate,
)


class EmployeeDataFromLegacyEsbMessageFactory(factory.Factory[EmployeeDataFromLegacyEsbMessage]):  # type: ignore
    class Meta:
        model = EmployeeDataFromLegacyEsbMessage

    resource_id = factory.Faker("uuid4")
    skills_performed_together = factory.LazyFunction(tuple)
    exclusive_skills = factory.LazyFunction(tuple)
    permissions = factory.LazyFunction(tuple)
    time_slot = TimeSlot.empty()


class TestTranslateToCapabilitySelector:
    def test_translate_legacy_esb_message_to_capability_selector_model(self) -> None:
        legacy_permissions = ("ADMIN<>2", "ROOT<>1")
        legacy_skills_performed_together = (
            ("JAVA", "CSHARP", "PYTHON"),
            ("RUST", "CSHARP", "PYTHON"),
        )
        legacy_exclusive_skills = ("YT DRAMA COMMENTS",)
        message = EmployeeDataFromLegacyEsbMessageFactory(
            permissions=legacy_permissions,
            skills_performed_together=legacy_skills_performed_together,
            exclusive_skills=legacy_exclusive_skills,
        )

        result = translate(message)

        assert len(result) == 6
        assert result.count(CapabilitySelector.can_perform_one_of({Capability.permission("ADMIN")})) == 2
        assert set(result) == {
            CapabilitySelector.can_perform_one_of({Capability.skill("YT DRAMA COMMENTS")}),
            CapabilitySelector.can_perform_all_at_the_time(Capability.skills("JAVA", "CSHARP", "PYTHON")),
            CapabilitySelector.can_perform_all_at_the_time(Capability.skills("RUST", "CSHARP", "PYTHON")),
            CapabilitySelector.can_perform_one_of({Capability.permission("ADMIN")}),
            CapabilitySelector.can_perform_one_of({Capability.permission("ROOT")}),
        }

    def test_zero_means_no_permission_nowhere(self) -> None:
        legacy_permissions = ["ADMIN<>0"]
        message = EmployeeDataFromLegacyEsbMessageFactory(permissions=legacy_permissions)

        result = translate(message)

        assert len(result) == 0
