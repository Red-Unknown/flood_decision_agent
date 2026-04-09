"""模式检测API.

提供输入模式自动检测功能，判断用户输入应该使用哪种处理模式。
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

router = APIRouter()


class ModeDetectRequest(BaseModel):
    """模式检测请求."""

    user_input: str = Field(..., description="用户输入文本")


class ModeDetectResponse(BaseModel):
    """模式检测响应."""

    recommended_mode: str = Field(..., description="推荐模式: simple/plan/spec")
    confidence: float = Field(..., description="置信度 0-1")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="检测指标")


def detect_mode_simple(user_input: str) -> Dict[str, Any]:
    """简单的模式检测逻辑.

    基于关键词和输入长度进行模式判断。

    Args:
        user_input: 用户输入文本

    Returns:
        检测结果字典
    """
    user_input_lower = user_input.lower().strip()

    # 1. 检查明确的命令
    if user_input_lower.startswith('/plan'):
        return {
            "recommended_mode": "plan",
            "confidence": 1.0,
            "metrics": {"trigger": "command", "command": "/plan"}
        }

    if user_input_lower.startswith('/spec'):
        return {
            "recommended_mode": "spec",
            "confidence": 1.0,
            "metrics": {"trigger": "command", "command": "/spec"}
        }

    # 2. 检查 Plan 模式关键词
    plan_keywords = [
        "计划", "规划", "方案", "策略", "步骤", "流程",
        "制定", "设计", "安排", "准备", "规划书",
        "plan", "schedule", "strategy", "blueprint"
    ]
    plan_score = sum(1 for kw in plan_keywords if kw in user_input_lower)

    # 3. 检查 Spec 模式关键词
    spec_keywords = [
        "规格", "规范", "标准", "需求", "文档", "说明",
        "详细", "具体", "定义", "接口", "API",
        "spec", "specification", "standard", "requirement", "document"
    ]
    spec_score = sum(1 for kw in spec_keywords if kw in user_input_lower)

    # 4. 基于输入长度判断
    input_length = len(user_input)
    length_score = min(input_length / 200, 1.0)  # 200字以上得满分

    # 5. 综合判断
    if plan_score > 0 and plan_score >= spec_score:
        confidence = min(0.5 + plan_score * 0.15 + length_score * 0.2, 0.95)
        return {
            "recommended_mode": "plan",
            "confidence": round(confidence, 2),
            "metrics": {
                "trigger": "keyword",
                "plan_score": plan_score,
                "spec_score": spec_score,
                "length_score": round(length_score, 2)
            }
        }

    if spec_score > 0 and spec_score > plan_score:
        confidence = min(0.5 + spec_score * 0.15 + length_score * 0.2, 0.95)
        return {
            "recommended_mode": "spec",
            "confidence": round(confidence, 2),
            "metrics": {
                "trigger": "keyword",
                "plan_score": plan_score,
                "spec_score": spec_score,
                "length_score": round(length_score, 2)
            }
        }

    # 6. 默认简单模式
    return {
        "recommended_mode": "simple",
        "confidence": round(0.7 + length_score * 0.2, 2),
        "metrics": {
            "trigger": "default",
            "plan_score": plan_score,
            "spec_score": spec_score,
            "length_score": round(length_score, 2)
        }
    }


@router.post("/mode/detect", response_model=ModeDetectResponse)
async def detect_mode(request: ModeDetectRequest) -> ModeDetectResponse:
    """检测用户输入应该使用的模式.

    Args:
        request: 包含用户输入的请求

    Returns:
        推荐的模式和置信度
    """
    try:
        result = detect_mode_simple(request.user_input)
        return ModeDetectResponse(
            recommended_mode=result["recommended_mode"],
            confidence=result["confidence"],
            metrics=result["metrics"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模式检测失败: {str(e)}")
