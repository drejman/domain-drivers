from __future__ import annotations

from datetime import UTC, datetime
from functools import partial

utcnow = partial(datetime.now, tz=UTC)
