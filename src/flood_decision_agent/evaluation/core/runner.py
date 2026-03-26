"""评估运行器 - 管理评估执行流程.

提供高级接口用于运行评估、批量处理和结果聚合。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from flood_decision_agent.evaluation.core.evaluator import AgentEvaluator, TestResult
from flood_decision_agent.evaluation.test_cases import TestCase, TestSuite
from flood_decision_agent.infra.logging import get_logger


@dataclass
class RunConfig:
    """运行配置."""

    name: str = "default_run"
    use_balanced: bool = True
    parallel: bool = False
    max_workers: int = 4
    timeout_ms: float = 60000.0
    continue_on_error: bool = True
    save_intermediate: bool = True
    intermediate_dir: str = "evaluation/intermediate"


@dataclass
class RunResult:
    """运行结果."""

    run_id: str
    config: RunConfig
    start_time: str
    end_time: str
    summary: Dict[str, Any] = field(default_factory=dict)
    test_results: List[TestResult] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class EvaluationRunner:
    """评估运行器.

    管理评估的完整生命周期：
    1. 配置管理
    2. 执行控制
    3. 结果聚合
    4. 中间状态保存
    """

    def __init__(
        self,
        evaluator: Optional[AgentEvaluator] = None,
        config: Optional[RunConfig] = None,
    ):
        self.logger = get_logger().bind(name=self.__class__.__name__)
        self.evaluator = evaluator or AgentEvaluator()
        self.config = config or RunConfig()
        self._run_history: List[RunResult] = []

    def run(
        self,
        test_suite: TestSuite,
        progress_callback: Optional[Callable[[int, int, TestResult], None]] = None,
    ) -> RunResult:
        """运行评估.

        Args:
            test_suite: 测试集
            progress_callback: 进度回调函数(current, total, result)

        Returns:
            运行结果
        """
        from datetime import datetime

        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger.info(f"开始评估运行: {run_id}")

        start_time = datetime.now().isoformat()

        # 获取测试用例
        if self.config.use_balanced:
            test_cases = test_suite.get_balanced_suite()
            self.logger.info(f"使用平衡测试集，共 {len(test_cases)} 个用例")
        else:
            test_cases = test_suite.test_cases

        total = len(test_cases)
        results: List[TestResult] = []

        # 执行测试
        for i, test_case in enumerate(test_cases):
            self.logger.info(f"[{i+1}/{total}] 执行测试: {test_case.id}")

            try:
                result = self.evaluator.evaluate_test_case(test_case)
                results.append(result)

                # 进度回调
                if progress_callback:
                    progress_callback(i + 1, total, result)

                # 保存中间结果
                if self.config.save_intermediate:
                    self._save_intermediate_result(run_id, i, result)

            except Exception as e:
                self.logger.error(f"测试 {test_case.id} 执行失败: {e}")
                if not self.config.continue_on_error:
                    raise

        end_time = datetime.now().isoformat()

        # 生成汇总
        summary = self._generate_summary(results)
        metrics = self.evaluator.get_all_metrics()

        run_result = RunResult(
            run_id=run_id,
            config=self.config,
            start_time=start_time,
            end_time=end_time,
            summary=summary,
            test_results=results,
            metrics=metrics,
        )

        self._run_history.append(run_result)
        self.logger.info(f"评估运行完成: {run_id}")

        return run_result

    def run_batch(
        self,
        test_suites: List[TestSuite],
        aggregate: bool = True,
    ) -> List[RunResult]:
        """批量运行多个测试集.

        Args:
            test_suites: 测试集列表
            aggregate: 是否聚合结果

        Returns:
            运行结果列表
        """
        results = []

        for suite in test_suites:
            self.logger.info(f"执行测试集: {suite.name}")
            result = self.run(suite)
            results.append(result)

        if aggregate and len(results) > 1:
            aggregated = self._aggregate_results(results)
            results.append(aggregated)

        return results

    def rerun_failed(
        self,
        previous_result: RunResult,
        test_suite: TestSuite,
    ) -> RunResult:
        """重新运行失败的测试.

        Args:
            previous_result: 之前的运行结果
            test_suite: 原始测试集

        Returns:
            新的运行结果
        """
        failed_ids = {
            r.test_case_id
            for r in previous_result.test_results
            if not r.success
        }

        if not failed_ids:
            self.logger.info("没有失败的测试需要重跑")
            return previous_result

        # 创建只包含失败用例的测试集
        failed_cases = [
            tc for tc in test_suite.test_cases
            if tc.id in failed_ids
        ]

        new_suite = TestSuite(name=f"{test_suite.name}_retry")
        new_suite.test_cases = failed_cases

        self.logger.info(f"重跑 {len(failed_cases)} 个失败测试")
        return self.run(new_suite)

    def compare_runs(
        self,
        run_results: List[RunResult],
    ) -> Dict[str, Any]:
        """对比多次运行结果.

        Args:
            run_results: 运行结果列表

        Returns:
            对比结果
        """
        comparison = {
            "runs": [],
            "trends": {},
            "improvements": [],
            "regressions": [],
        }

        for run in run_results:
            comparison["runs"].append({
                "run_id": run.run_id,
                "start_time": run.start_time,
                "pass_rate": run.summary.get("pass_rate", 0),
                "total": run.summary.get("total", 0),
                "passed": run.summary.get("passed", 0),
            })

        # 计算趋势
        if len(run_results) >= 2:
            first = run_results[0]
            last = run_results[-1]

            first_rate = first.summary.get("pass_rate", 0)
            last_rate = last.summary.get("pass_rate", 0)

            comparison["trends"]["pass_rate_change"] = last_rate - first_rate
            comparison["trends"]["improved"] = last_rate > first_rate

        return comparison

    def get_run_history(self) -> List[RunResult]:
        """获取运行历史."""
        return self._run_history.copy()

    def _generate_summary(self, results: List[TestResult]) -> Dict[str, Any]:
        """生成运行汇总."""
        total = len(results)
        passed = sum(1 for r in results if r.success)
        failed = total - passed

        # 执行时间统计
        execution_times = [r.execution_time_ms for r in results]
        if execution_times:
            import numpy as np
            avg_time = np.mean(execution_times)
            max_time = np.max(execution_times)
            min_time = np.min(execution_times)
        else:
            avg_time = max_time = min_time = 0

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "avg_execution_time_ms": avg_time,
            "max_execution_time_ms": max_time,
            "min_execution_time_ms": min_time,
        }

    def _save_intermediate_result(
        self,
        run_id: str,
        index: int,
        result: TestResult,
    ) -> None:
        """保存中间结果."""
        import json

        dir_path = Path(self.config.intermediate_dir) / run_id
        dir_path.mkdir(parents=True, exist_ok=True)

        file_path = dir_path / f"{index:04d}_{result.test_case_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({
                "test_case_id": result.test_case_id,
                "test_case_name": result.test_case_name,
                "success": result.success,
                "execution_time_ms": result.execution_time_ms,
                "metrics": result.metrics,
                "error_message": result.error_message,
            }, f, ensure_ascii=False, indent=2)

    def _aggregate_results(self, results: List[RunResult]) -> RunResult:
        """聚合多个运行结果."""
        from datetime import datetime

        all_test_results = []
        for r in results:
            all_test_results.extend(r.test_results)

        summary = self._generate_summary(all_test_results)

        return RunResult(
            run_id=f"aggregated_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            config=self.config,
            start_time=results[0].start_time if results else "",
            end_time=results[-1].end_time if results else "",
            summary=summary,
            test_results=all_test_results,
            metrics=self.evaluator.get_all_metrics(),
        )
