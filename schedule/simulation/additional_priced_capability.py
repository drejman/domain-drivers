from __future__ import annotations

from typing import TYPE_CHECKING

import attrs as a

if TYPE_CHECKING:
    from decimal import Decimal

    from .available_resource_capability import AvailableResourceCapability


@a.define(frozen=True)
class AdditionalPricedCapability:
    value: Decimal
    available_resource_capability: AvailableResourceCapability
