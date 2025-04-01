from __future__ import annotations

from datetime import UTC

import factory  # type: ignore

from ..available_resource_capability import (
    AvailableResourceCapability,
)
from ..simulated_capabilities import SimulatedCapabilities


class AvailableResourceCapabilityFactory(factory.Factory):  # type: ignore
    class Meta:
        model = AvailableResourceCapability

    resource_id = factory.Faker("uuid4")
    time_slot = factory.Faker("date_time_this_year", tzinfo=UTC)


class SimulatedCapabilitiesFactory(factory.Factory):  # type: ignore
    class Meta:
        model = SimulatedCapabilities

    class Params:
        num_capabilities = 0

    @factory.lazy_attribute  # type: ignore
    def capabilities(self) -> list[AvailableResourceCapability]:
        result = []
        argument_src = self._Resolver__declarations["capabilities"].context
        for index in range(self.num_capabilities):
            capability = AvailableResourceCapabilityFactory.build(
                resource_id=argument_src[f"{index}__resource_id"],
                capability=argument_src[f"{index}__capability"],
                time_slot=argument_src[f"{index}__time_slot"],
            )
            result.append(capability)
        return result
