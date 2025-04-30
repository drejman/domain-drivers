from __future__ import annotations

type JSON = dict[str, JSON] | list[JSON] | str | int | float | bool | None
