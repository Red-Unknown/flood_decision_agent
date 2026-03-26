"""评估指标模块 - 六大维度指标体系.

基于Anthropic评估框架和Google Agent Quality白皮书，
定义六大维度的量化指标计算逻辑。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class MetricValue:
    """指标值数据类."""

    name: str
    value: float
    unit: str = ""
    description: str = ""
    timestamp: float = field(default_factory=time.time)


class BaseMetrics:
    """指标基类."""

    def get_all_metrics(self) -> Dict[str, MetricValue]:
        """获取所有指标."""
        raise NotImplementedError


class EffectivenessMetrics(BaseMetrics):
    """有效性指标 - 衡量任务完成质量和准确性."""

    def __init__(self):
        self.task_results: List[Dict[str, Any]] = []
        self.intent_results: List[Dict[str, Any]] = []
        self.chain_results: List[Dict[str, Any]] = []

    def record_task_result(
        self,
        task_id: str,
        success: bool,
        expected_output: Optional[Any] = None,
        actual_output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """记录任务执行结果."""
        self.task_results.append({
            "task_id": task_id,
            "success": success,
            "expected": expected_output,
            "actual": actual_output,
            "metadata": metadata or {},
        })

    def record_intent_result(
        self,
        input_text: str,
        expected_intent: str,
        actual_intent: str,
        confidence: float = 1.0,
    ) -> None:
        """记录意图识别结果."""
        self.intent_results.append({
            "input": input_text,
            "expected": expected_intent,
            "actual": actual_intent,
            "confidence": confidence,
            "correct": expected_intent == actual_intent,
        })

    def record_chain_result(
        self,
        chain_id: str,
        is_complete: bool,
        node_count: int,
        reliability_score: float,
    ) -> None:
        """记录决策链生成结果."""
        self.chain_results.append({
            "chain_id": chain_id,
            "is_complete": is_complete,
            "node_count": node_count,
            "reliability_score": reliability_score,
        })

    @property
    def task_success_rate(self) -> MetricValue:
        """任务成功率."""
        if not self.task_results:
            return MetricValue("task_success_rate", 0.0, "ratio", "任务成功率")
        success_count = sum(1 for r in self.task_results if r["success"])
        rate = success_count / len(self.task_results)
        return MetricValue("task_success_rate", rate, "ratio", "任务成功率")

    @property
    def intent_accuracy(self) -> MetricValue:
        """意图识别准确率."""
        if not self.intent_results:
            return MetricValue("intent_accuracy", 0.0, "ratio", "意图识别准确率")
        correct_count = sum(1 for r in self.intent_results if r["correct"])
        rate = correct_count / len(self.intent_results)
        return MetricValue("intent_accuracy", rate, "ratio", "意图识别准确率")

    @property
    def chain_completeness(self) -> MetricValue:
        """决策链完整性."""
        if not self.chain_results:
            return MetricValue("chain_completeness", 0.0, "ratio", "决策链完整性")
        complete_count = sum(1 for r in self.chain_results if r["is_complete"])
        rate = complete_count / len(self.chain_results)
        return MetricValue("chain_completeness", rate, "ratio", "决策链完整性")

    @property
    def avg_reliability_score(self) -> MetricValue:
        """平均可靠性评分."""
        if not self.chain_results:
            return MetricValue("avg_reliability_score", 0.0, "score", "平均可靠性评分")
        scores = [r["reliability_score"] for r in self.chain_results]
        avg_score = np.mean(scores) if scores else 0.0
        return MetricValue("avg_reliability_score", avg_score, "score", "平均可靠性评分")

    def get_all_metrics(self) -> Dict[str, MetricValue]:
        """获取所有有效性指标."""
        return {
            "task_success_rate": self.task_success_rate,
            "intent_accuracy": self.intent_accuracy,
            "chain_completeness": self.chain_completeness,
            "avg_reliability_score": self.avg_reliability_score,
        }


class EfficiencyMetrics(BaseMetrics):
    """效率指标 - 衡量时间和资源消耗."""

    def __init__(self):
        self.execution_times: List[float] = []
        self.token_counts: List[int] = []
        self.node_counts: List[int] = []
        self.step_counts: List[int] = []

    def record_execution(
        self,
        elapsed_time_ms: float,
        token_count: int = 0,
        node_count: int = 0,
        step_count: int = 0,
    ) -> None:
        """记录执行指标."""
        self.execution_times.append(elapsed_time_ms)
        if token_count > 0:
            self.token_counts.append(token_count)
        if node_count > 0:
            self.node_counts.append(node_count)
        if step_count > 0:
            self.step_counts.append(step_count)

    @property
    def avg_response_time(self) -> MetricValue:
        """平均响应时间."""
        if not self.execution_times:
            return MetricValue("avg_response_time", 0.0, "ms", "平均响应时间")
        avg_time = np.mean(self.execution_times)
        return MetricValue("avg_response_time", avg_time, "ms", "平均响应时间")

    @property
    def p95_response_time(self) -> MetricValue:
        """P95响应时间."""
        if not self.execution_times:
            return MetricValue("p95_response_time", 0.0, "ms", "P95响应时间")
        p95 = np.percentile(self.execution_times, 95)
        return MetricValue("p95_response_time", p95, "ms", "P95响应时间")

    @property
    def avg_token_count(self) -> MetricValue:
        """平均Token消耗."""
        if not self.token_counts:
            return MetricValue("avg_token_count", 0.0, "tokens", "平均Token消耗")
        avg_tokens = np.mean(self.token_counts)
        return MetricValue("avg_token_count", avg_tokens, "tokens", "平均Token消耗")

    @property
    def avg_node_count(self) -> MetricValue:
        """平均任务图节点数."""
        if not self.node_counts:
            return MetricValue("avg_node_count", 0.0, "count", "平均任务图节点数")
        avg_nodes = np.mean(self.node_counts)
        return MetricValue("avg_node_count", avg_nodes, "count", "平均任务图节点数")

    @property
    def avg_step_count(self) -> MetricValue:
        """平均执行步数."""
        if not self.step_counts:
            return MetricValue("avg_step_count", 0.0, "count", "平均执行步数")
        avg_steps = np.mean(self.step_counts)
        return MetricValue("avg_step_count", avg_steps, "count", "平均执行步数")

    def get_all_metrics(self) -> Dict[str, MetricValue]:
        """获取所有效率指标."""
        return {
            "avg_response_time": self.avg_response_time,
            "p95_response_time": self.p95_response_time,
            "avg_token_count": self.avg_token_count,
            "avg_node_count": self.avg_node_count,
            "avg_step_count": self.avg_step_count,
        }


class RobustnessMetrics(BaseMetrics):
    """鲁棒性指标 - 衡量系统稳定性和容错能力."""

    def __init__(self):
        self.error_records: List[Dict[str, Any]] = []
        self.tool_calls: List[Dict[str, Any]] = []
        self.retry_records: List[Dict[str, Any]] = []

    def record_error(
        self,
        task_id: str,
        error_type: str,
        is_recoverable: bool,
        recovered: bool = False,
    ) -> None:
        """记录错误信息."""
        self.error_records.append({
            "task_id": task_id,
            "error_type": error_type,
            "is_recoverable": is_recoverable,
            "recovered": recovered,
        })

    def record_tool_call(
        self,
        tool_name: str,
        success: bool,
        execution_time_ms: float = 0.0,
    ) -> None:
        """记录工具调用."""
        self.tool_calls.append({
            "tool_name": tool_name,
            "success": success,
            "execution_time_ms": execution_time_ms,
        })

    def record_retry(
        self,
        task_id: str,
        retry_count: int,
        final_success: bool,
    ) -> None:
        """记录重试信息."""
        self.retry_records.append({
            "task_id": task_id,
            "retry_count": retry_count,
            "final_success": final_success,
        })

    @property
    def exception_rate(self) -> MetricValue:
        """异常率."""
        if not self.error_records:
            return MetricValue("exception_rate", 0.0, "ratio", "异常率")
        rate = len(self.error_records) / max(len(self.error_records), 1)
        return MetricValue("exception_rate", rate, "ratio", "异常率")

    @property
    def tool_failure_rate(self) -> MetricValue:
        """工具调用失败率."""
        if not self.tool_calls:
            return MetricValue("tool_failure_rate", 0.0, "ratio", "工具调用失败率")
        failure_count = sum(1 for c in self.tool_calls if not c["success"])
        rate = failure_count / len(self.tool_calls)
        return MetricValue("tool_failure_rate", rate, "ratio", "工具调用失败率")

    @property
    def recovery_rate(self) -> MetricValue:
        """恢复成功率."""
        recoverable_errors = [e for e in self.error_records if e["is_recoverable"]]
        if not recoverable_errors:
            return MetricValue("recovery_rate", 1.0, "ratio", "恢复成功率")
        recovered_count = sum(1 for e in recoverable_errors if e["recovered"])
        rate = recovered_count / len(recoverable_errors)
        return MetricValue("recovery_rate", rate, "ratio", "恢复成功率")

    @property
    def pass_at_k(self, k: int = 3) -> MetricValue:
        """pass@k - k次尝试至少一次成功概率."""
        if not self.retry_records:
            return MetricValue(f"pass_at_{k}", 0.0, "ratio", f"Pass@{k}")
        success_count = sum(1 for r in self.retry_records if r["final_success"])
        rate = success_count / len(self.retry_records)
        return MetricValue(f"pass_at_{k}", rate, "ratio", f"Pass@{k}")

    def get_all_metrics(self) -> Dict[str, MetricValue]:
        """获取所有鲁棒性指标."""
        return {
            "exception_rate": self.exception_rate,
            "tool_failure_rate": self.tool_failure_rate,
            "recovery_rate": self.recovery_rate,
            "pass_at_3": self.pass_at_k(3),
        }


class SafetyMetrics(BaseMetrics):
    """安全性指标 - 衡量行为合规和安全."""

    def __init__(self):
        self.rule_checks: List[Dict[str, Any]] = []
        self.risk_operations: List[Dict[str, Any]] = []
        self.hallucination_checks: List[Dict[str, Any]] = []

    def record_rule_check(
        self,
        task_id: str,
        rule_name: str,
        complied: bool,
        severity: str = "normal",
    ) -> None:
        """记录规则遵循检查."""
        self.rule_checks.append({
            "task_id": task_id,
            "rule_name": rule_name,
            "complied": complied,
            "severity": severity,
        })

    def record_risk_operation(
        self,
        task_id: str,
        operation_type: str,
        risk_level: str,
        authorized: bool,
    ) -> None:
        """记录风险操作."""
        self.risk_operations.append({
            "task_id": task_id,
            "operation_type": operation_type,
            "risk_level": risk_level,
            "authorized": authorized,
        })

    def record_hallucination_check(
        self,
        task_id: str,
        has_hallucination: bool,
        confidence: float,
    ) -> None:
        """记录幻觉检查."""
        self.hallucination_checks.append({
            "task_id": task_id,
            "has_hallucination": has_hallucination,
            "confidence": confidence,
        })

    @property
    def rule_compliance_rate(self) -> MetricValue:
        """规则遵循率."""
        if not self.rule_checks:
            return MetricValue("rule_compliance_rate", 1.0, "ratio", "规则遵循率")
        complied_count = sum(1 for c in self.rule_checks if c["complied"])
        rate = complied_count / len(self.rule_checks)
        return MetricValue("rule_compliance_rate", rate, "ratio", "规则遵循率")

    @property
    def unauthorized_operation_rate(self) -> MetricValue:
        """未授权操作率."""
        if not self.risk_operations:
            return MetricValue("unauthorized_operation_rate", 0.0, "ratio", "未授权操作率")
        unauthorized_count = sum(1 for o in self.risk_operations if not o["authorized"])
        rate = unauthorized_count / len(self.risk_operations)
        return MetricValue("unauthorized_operation_rate", rate, "ratio", "未授权操作率")

    @property
    def hallucination_rate(self) -> MetricValue:
        """幻觉率."""
        if not self.hallucination_checks:
            return MetricValue("hallucination_rate", 0.0, "ratio", "幻觉率")
        hallucination_count = sum(1 for c in self.hallucination_checks if c["has_hallucination"])
        rate = hallucination_count / len(self.hallucination_checks)
        return MetricValue("hallucination_rate", rate, "ratio", "幻觉率")

    def get_all_metrics(self) -> Dict[str, MetricValue]:
        """获取所有安全性指标."""
        return {
            "rule_compliance_rate": self.rule_compliance_rate,
            "unauthorized_operation_rate": self.unauthorized_operation_rate,
            "hallucination_rate": self.hallucination_rate,
        }


class AutonomyMetrics(BaseMetrics):
    """自主性与智能性指标 - 衡量自主决策能力."""

    def __init__(self):
        self.tool_selections: List[Dict[str, Any]] = []
        self.adjustments: List[Dict[str, Any]] = []
        self.unknown_scenarios: List[Dict[str, Any]] = []

    def record_tool_selection(
        self,
        task_id: str,
        auto_selected: bool,
        selected_tools: List[str],
        task_type: str,
    ) -> None:
        """记录工具选择."""
        self.tool_selections.append({
            "task_id": task_id,
            "auto_selected": auto_selected,
            "selected_tools": selected_tools,
            "task_type": task_type,
        })

    def record_adjustment(
        self,
        task_id: str,
        adjustment_type: str,
        reason: str,
    ) -> None:
        """记录动态调整."""
        self.adjustments.append({
            "task_id": task_id,
            "adjustment_type": adjustment_type,
            "reason": reason,
        })

    def record_unknown_scenario(
        self,
        task_id: str,
        scenario_type: str,
        handled: bool,
    ) -> None:
        """记录未知场景处理."""
        self.unknown_scenarios.append({
            "task_id": task_id,
            "scenario_type": scenario_type,
            "handled": handled,
        })

    @property
    def auto_tool_selection_rate(self) -> MetricValue:
        """工具自主选用率."""
        if not self.tool_selections:
            return MetricValue("auto_tool_selection_rate", 0.0, "ratio", "工具自主选用率")
        auto_count = sum(1 for s in self.tool_selections if s["auto_selected"])
        rate = auto_count / len(self.tool_selections)
        return MetricValue("auto_tool_selection_rate", rate, "ratio", "工具自主选用率")

    @property
    def dynamic_adjustment_rate(self) -> MetricValue:
        """动态调整率."""
        # 基于总任务数和调整次数计算
        total_tasks = len(set(s["task_id"] for s in self.tool_selections))
        if total_tasks == 0:
            return MetricValue("dynamic_adjustment_rate", 0.0, "ratio", "动态调整率")
        adjusted_tasks = len(set(a["task_id"] for a in self.adjustments))
        rate = adjusted_tasks / total_tasks
        return MetricValue("dynamic_adjustment_rate", rate, "ratio", "动态调整率")

    @property
    def unknown_scenario_handling_rate(self) -> MetricValue:
        """未知场景适配率."""
        if not self.unknown_scenarios:
            return MetricValue("unknown_scenario_handling_rate", 1.0, "ratio", "未知场景适配率")
        handled_count = sum(1 for s in self.unknown_scenarios if s["handled"])
        rate = handled_count / len(self.unknown_scenarios)
        return MetricValue("unknown_scenario_handling_rate", rate, "ratio", "未知场景适配率")

    def get_all_metrics(self) -> Dict[str, MetricValue]:
        """获取所有自主性指标."""
        return {
            "auto_tool_selection_rate": self.auto_tool_selection_rate,
            "dynamic_adjustment_rate": self.dynamic_adjustment_rate,
            "unknown_scenario_handling_rate": self.unknown_scenario_handling_rate,
        }


class ExplainabilityMetrics(BaseMetrics):
    """可解释性指标 - 衡量推理透明度."""

    def __init__(self):
        self.reasoning_records: List[Dict[str, Any]] = []
        self.interaction_records: List[Dict[str, Any]] = []

    def record_reasoning(
        self,
        task_id: str,
        has_reasoning_chain: bool,
        reasoning_quality_score: float,
    ) -> None:
        """记录推理过程."""
        self.reasoning_records.append({
            "task_id": task_id,
            "has_reasoning_chain": has_reasoning_chain,
            "reasoning_quality_score": reasoning_quality_score,
        })

    def record_interaction(
        self,
        task_id: str,
        turn_count: int,
        intent_clarity_score: float,
    ) -> None:
        """记录交互质量."""
        self.interaction_records.append({
            "task_id": task_id,
            "turn_count": turn_count,
            "intent_clarity_score": intent_clarity_score,
        })

    @property
    def reasoning_transparency_rate(self) -> MetricValue:
        """推理透明度."""
        if not self.reasoning_records:
            return MetricValue("reasoning_transparency_rate", 0.0, "ratio", "推理透明度")
        transparent_count = sum(1 for r in self.reasoning_records if r["has_reasoning_chain"])
        rate = transparent_count / len(self.reasoning_records)
        return MetricValue("reasoning_transparency_rate", rate, "ratio", "推理透明度")

    @property
    def avg_reasoning_quality(self) -> MetricValue:
        """平均推理质量."""
        if not self.reasoning_records:
            return MetricValue("avg_reasoning_quality", 0.0, "score", "平均推理质量")
        scores = [r["reasoning_quality_score"] for r in self.reasoning_records]
        avg_score = np.mean(scores) if scores else 0.0
        return MetricValue("avg_reasoning_quality", avg_score, "score", "平均推理质量")

    @property
    def avg_intent_clarity(self) -> MetricValue:
        """平均意图清晰度."""
        if not self.interaction_records:
            return MetricValue("avg_intent_clarity", 0.0, "score", "平均意图清晰度")
        scores = [r["intent_clarity_score"] for r in self.interaction_records]
        avg_score = np.mean(scores) if scores else 0.0
        return MetricValue("avg_intent_clarity", avg_score, "score", "平均意图清晰度")

    def get_all_metrics(self) -> Dict[str, MetricValue]:
        """获取所有可解释性指标."""
        return {
            "reasoning_transparency_rate": self.reasoning_transparency_rate,
            "avg_reasoning_quality": self.avg_reasoning_quality,
            "avg_intent_clarity": self.avg_intent_clarity,
        }
