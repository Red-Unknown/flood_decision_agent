"""评估执行器 - 基于Anthropic第四步：构建健壮的评估框架.

在隔离环境中运行试验，混合使用代码基、模型基与人工评分器以提升可靠性。
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from flood_decision_agent.agents.decision_chain_generator import DecisionChainGeneratorAgent
from flood_decision_agent.agents.node_scheduler import NodeSchedulerAgent
from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.evaluation.metrics import (
    AutonomyMetrics,
    EffectivenessMetrics,
    EfficiencyMetrics,
    ExplainabilityMetrics,
    RobustnessMetrics,
    SafetyMetrics,
)
from flood_decision_agent.evaluation.test_cases import TestCase, TestSuite
from flood_decision_agent.infra.logging import get_logger


@dataclass
class TestResult:
    """单个测试结果."""

    test_case_id: str
    test_case_name: str
    success: bool
    execution_time_ms: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class AgentEvaluator:
    """Agent评估器.

    提供完整的评估框架，包括：
    1. 测试执行（隔离环境）
    2. 指标收集
    3. 结果验证
    4. 评分器校准
    """

    def __init__(
        self,
        chain_generator: Optional[DecisionChainGeneratorAgent] = None,
        node_scheduler: Optional[NodeSchedulerAgent] = None,
    ):
        self.logger = get_logger().bind(name=self.__class__.__name__)

        # Agent实例
        self.chain_generator = chain_generator or DecisionChainGeneratorAgent()
        self.node_scheduler = node_scheduler

        # 指标收集器
        self.effectiveness = EffectivenessMetrics()
        self.efficiency = EfficiencyMetrics()
        self.robustness = RobustnessMetrics()
        self.safety = SafetyMetrics()
        self.autonomy = AutonomyMetrics()
        self.explainability = ExplainabilityMetrics()

        # 测试结果
        self.test_results: List[TestResult] = []

        # 评分器校准数据
        self.calibration_data: Dict[str, Any] = {}

    def evaluate_test_case(self, test_case: TestCase) -> TestResult:
        """评估单个测试用例.

        在隔离环境中执行测试，收集各项指标。

        Args:
            test_case: 测试用例

        Returns:
            测试结果
        """
        self.logger.info(f"开始评估测试用例: {test_case.id} - {test_case.name}")

        start_time = time.time()
        data_pool = SharedDataPool()

        try:
            # 准备输入
            if test_case.input_type == "structured" and test_case.structured_input:
                import json

                user_input = json.dumps(test_case.structured_input)
            else:
                user_input = test_case.input_text

            # ========== 阶段1: 决策链生成 ==========
            generation_start = time.time()
            task_graph, metadata = self.chain_generator.generate_chain(
                user_input=user_input,
                input_type=test_case.input_type,
            )
            generation_time = (time.time() - generation_start) * 1000

            # 收集决策链指标
            self.effectiveness.record_chain_result(
                chain_id=test_case.id,
                is_complete=len(task_graph.get_all_nodes()) > 0,
                node_count=len(task_graph.get_all_nodes()),
                reliability_score=metadata.get("optimization", {}).get("reliability_score", 0.0),
            )

            # 收集意图识别指标
            intent_data = metadata.get("intent", {})
            if test_case.expected.expected_task_type:
                self.effectiveness.record_intent_result(
                    input_text=user_input,
                    expected_intent=test_case.expected.expected_task_type,
                    actual_intent=intent_data.get("task_type", "unknown"),
                )

            # 收集效率指标
            self.efficiency.record_execution(
                elapsed_time_ms=generation_time,
                node_count=len(task_graph.get_all_nodes()),
            )

            # ========== 阶段2: 任务执行（如果有调度器）==========
            execution_result = None
            if self.node_scheduler and len(task_graph.get_all_nodes()) > 0:
                execution_start = time.time()
                execution_result = self.node_scheduler.execute_task_graph(
                    task_graph, data_pool
                )
                execution_time = (time.time() - execution_start) * 1000

                # 收集执行指标
                self._collect_execution_metrics(execution_result, test_case)

                # 更新效率指标
                self.efficiency.record_execution(
                    elapsed_time_ms=execution_time,
                    step_count=execution_result.get("completed_count", 0),
                )

            # ========== 验证结果 ==========
            success = self._validate_result(
                test_case, task_graph, metadata, execution_result
            )

            # 记录任务结果
            self.effectiveness.record_task_result(
                task_id=test_case.id,
                success=success,
                metadata={
                    "test_case_type": test_case.case_type.value,
                    "generation_metadata": metadata,
                    "execution_result": execution_result,
                },
            )

            total_time = (time.time() - start_time) * 1000

            result = TestResult(
                test_case_id=test_case.id,
                test_case_name=test_case.name,
                success=success,
                execution_time_ms=total_time,
                metrics={
                    "generation_time_ms": generation_time,
                    "node_count": len(task_graph.get_all_nodes()),
                    "reliability_score": metadata.get("optimization", {}).get("reliability_score", 0.0),
                },
                details={
                    "task_graph_nodes": list(task_graph.get_all_nodes().keys()),
                    "metadata": metadata,
                },
            )

            self.logger.info(f"测试用例 {test_case.id} 评估完成: {'通过' if success else '失败'}")
            return result

        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            error_msg = f"{str(e)}\n{traceback.format_exc()}"

            # 记录错误
            self.robustness.record_error(
                task_id=test_case.id,
                error_type=type(e).__name__,
                is_recoverable=False,
                recovered=False,
            )

            self.effectiveness.record_task_result(
                task_id=test_case.id,
                success=False,
                metadata={"error": error_msg},
            )

            self.logger.error(f"测试用例 {test_case.id} 执行异常: {e}")

            return TestResult(
                test_case_id=test_case.id,
                test_case_name=test_case.name,
                success=False,
                execution_time_ms=total_time,
                error_message=str(e),
            )

    def _collect_execution_metrics(
        self,
        execution_result: Dict[str, Any],
        test_case: TestCase,
    ) -> None:
        """收集执行阶段的指标."""
        # 工具调用指标
        for node_id, node_result in execution_result.get("results", {}).items():
            metrics = node_result.get("metrics", {})

            # 工具使用
            tools_used = metrics.get("tools_used", [])
            for tool_name in tools_used:
                self.robustness.record_tool_call(
                    tool_name=tool_name,
                    success=node_result.get("status") == "success",
                )

            # 重试信息
            retry_count = metrics.get("retry_count", 0)
            if retry_count > 0:
                self.robustness.record_retry(
                    task_id=node_id,
                    retry_count=retry_count,
                    final_success=node_result.get("status") == "success",
                )

            # 自主性指标
            execution_strategy = metrics.get("execution_strategy", "auto")
            self.autonomy.record_tool_selection(
                task_id=node_id,
                auto_selected=execution_strategy == "auto",
                selected_tools=tools_used,
                task_type=node_result.get("task_type", "unknown"),
            )

        # 安全指标
        if test_case.expected.required_rules:
            for rule in test_case.expected.required_rules:
                self.safety.record_rule_check(
                    task_id=test_case.id,
                    rule_name=rule,
                    complied=execution_result.get("status") in ["success", "partial_failed"],
                )

    def _validate_result(
        self,
        test_case: TestCase,
        task_graph: Any,
        metadata: Dict[str, Any],
        execution_result: Optional[Dict[str, Any]],
    ) -> bool:
        """验证测试结果是否符合预期."""
        expected = test_case.expected

        # 1. 验证成功状态
        if expected.success:
            # 期望成功的情况
            if len(task_graph.get_all_nodes()) == 0:
                return False

            # 验证节点数量范围
            node_count = len(task_graph.get_all_nodes())
            min_nodes, max_nodes = expected.expected_node_count_range
            if not (min_nodes <= node_count <= max_nodes):
                return False

            # 验证可靠性评分
            reliability = metadata.get("optimization", {}).get("reliability_score", 0.0)
            if reliability < expected.min_reliability_score:
                return False

            # 验证执行结果
            if execution_result:
                if execution_result.get("status") == "failed":
                    return False

                # 验证响应时间
                elapsed_time = execution_result.get("metrics", {}).get("total_elapsed_time", 0) * 1000
                if elapsed_time > expected.max_response_time_ms:
                    return False
        else:
            # 期望失败的情况
            if execution_result and execution_result.get("status") == "success":
                return False

        return True

    def evaluate_test_suite(
        self,
        test_suite: TestSuite,
        use_balanced: bool = True,
    ) -> Dict[str, Any]:
        """评估整个测试集.

        Args:
            test_suite: 测试集
            use_balanced: 是否使用平衡的测试集

        Returns:
            评估结果汇总
        """
        self.logger.info(f"开始评估测试集: {test_suite.name}")

        # 重置结果
        self.test_results = []

        # 获取测试用例
        if use_balanced:
            test_cases = test_suite.get_balanced_suite()
            self.logger.info(f"使用平衡测试集，共 {len(test_cases)} 个用例")
        else:
            test_cases = test_suite.test_cases

        # 执行所有测试
        for test_case in test_cases:
            result = self.evaluate_test_case(test_case)
            self.test_results.append(result)

        # 汇总结果
        summary = self._generate_summary()

        self.logger.info(f"测试集评估完成: {summary['passed']}/{summary['total']} 通过")
        return summary

    def _generate_summary(self) -> Dict[str, Any]:
        """生成评估结果汇总."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.success)
        failed = total - passed

        # 按类型统计
        type_stats: Dict[str, Dict[str, int]] = {}
        for result in self.test_results:
            # 从test_case_id推断类型
            case_type = result.test_case_id.split("_")[0].lower()
            if case_type not in type_stats:
                type_stats[case_type] = {"total": 0, "passed": 0}
            type_stats[case_type]["total"] += 1
            if result.success:
                type_stats[case_type]["passed"] += 1

        # 收集所有指标
        all_metrics = {
            "effectiveness": self.effectiveness.get_all_metrics(),
            "efficiency": self.efficiency.get_all_metrics(),
            "robustness": self.robustness.get_all_metrics(),
            "safety": self.safety.get_all_metrics(),
            "autonomy": self.autonomy.get_all_metrics(),
            "explainability": self.explainability.get_all_metrics(),
        }

        # 转换为可序列化的格式
        metrics_serializable = {}
        for category, metrics in all_metrics.items():
            metrics_serializable[category] = {
                name: {
                    "value": metric.value,
                    "unit": metric.unit,
                    "description": metric.description,
                }
                for name, metric in metrics.items()
            }

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "type_stats": type_stats,
            "metrics": metrics_serializable,
            "test_results": [
                {
                    "test_case_id": r.test_case_id,
                    "test_case_name": r.test_case_name,
                    "success": r.success,
                    "execution_time_ms": r.execution_time_ms,
                    "error_message": r.error_message,
                }
                for r in self.test_results
            ],
        }

    def calibrate_scorer(
        self,
        reference_cases: List[TestCase],
        human_scores: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """校准评分器.

        使用参考解法和人工评分校准自动评分器。

        Args:
            reference_cases: 带参考解法的测试用例
            human_scores: 人工评分 {case_id: score}

        Returns:
            校准结果
        """
        self.logger.info("开始评分器校准")

        calibration_results = []

        for case in reference_cases:
            if not case.reference_solution:
                continue

            # 执行测试
            result = self.evaluate_test_case(case)

            # 计算自动评分
            auto_score = self._calculate_auto_score(result)

            # 对比人工评分
            human_score = human_scores.get(case.id) if human_scores else None

            calibration_results.append({
                "case_id": case.id,
                "auto_score": auto_score,
                "human_score": human_score,
                "difference": abs(auto_score - human_score) if human_score else None,
            })

        # 计算校准指标
        if human_scores:
            differences = [r["difference"] for r in calibration_results if r["difference"] is not None]
            avg_difference = sum(differences) / len(differences) if differences else 0.0
        else:
            avg_difference = None

        self.calibration_data = {
            "results": calibration_results,
            "avg_difference": avg_difference,
            "calibration_date": time.time(),
        }

        self.logger.info(f"评分器校准完成，平均差异: {avg_difference}")
        return self.calibration_data

    def _calculate_auto_score(self, result: TestResult) -> float:
        """计算自动评分."""
        # 基于多个维度计算综合评分
        scores = []

        # 1. 任务成功率
        scores.append(1.0 if result.success else 0.0)

        # 2. 执行时间评分（越快越好）
        time_score = max(0.0, 1.0 - result.execution_time_ms / 30000.0)
        scores.append(time_score)

        # 3. 可靠性评分
        reliability = result.metrics.get("reliability_score", 0.0)
        scores.append(reliability)

        # 加权平均
        weights = [0.5, 0.2, 0.3]
        final_score = sum(s * w for s, w in zip(scores, weights))

        return final_score

    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标数据."""
        return {
            "effectiveness": self.effectiveness.get_all_metrics(),
            "efficiency": self.efficiency.get_all_metrics(),
            "robustness": self.robustness.get_all_metrics(),
            "safety": self.safety.get_all_metrics(),
            "autonomy": self.autonomy.get_all_metrics(),
            "explainability": self.explainability.get_all_metrics(),
        }
