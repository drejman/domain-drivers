from __future__ import annotations

from typing import override

import attrs as a

from schedule.planning.parallelization.stage import Stage


@a.frozen
class StageDependency:
    stage: Stage
    dependency: Stage


@a.frozen(str=False)
class RemovalSuggestion:
    dependencies: tuple[StageDependency, ...]

    @override
    def __str__(self) -> str:
        return f"[{', '.join(str(dep) for dep in self.dependencies)}]"
