from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class FusionResult:
    value: Any
    strategy: str


class DecisionFusion:
    def fuse(self, candidates: List[Dict[str, Any]]) -> FusionResult:
        if not candidates:
            raise ValueError("candidates 为空，无法融合")
        
        if len(candidates) == 1:
            return FusionResult(value=candidates[0], strategy="single_model_select")
        
        merged: Dict[str, Any] = {}
        for candidate in candidates:
            if isinstance(candidate, dict):
                merged.update(candidate)
            else:
                merged["data"] = candidate
        
        return FusionResult(value=merged, strategy="merge_all")
