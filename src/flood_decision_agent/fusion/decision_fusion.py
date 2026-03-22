from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FusionResult:
    value: Any
    strategy: str


class DecisionFusion:
    def fuse(self, candidates: list[Any]) -> FusionResult:
        if not candidates:
            raise ValueError("candidates 为空，无法融合")
        return FusionResult(value=candidates[0], strategy="single_model_select")
