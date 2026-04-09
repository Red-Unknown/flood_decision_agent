"""
性能测试脚本
用于测试WebSocket连接、决策链生成和任务执行的性能
"""

import asyncio
import json
import time
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import defaultdict
import websockets
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    success: bool
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation: str
    durations: List[float] = field(default_factory=list)

    @property
    def avg_duration(self) -> float:
        return statistics.mean(self.durations) if self.durations else 0

    @property
    def min_duration(self) -> float:
        return min(self.durations) if self.durations else 0

    @property
    def max_duration(self) -> float:
        return max(self.durations) if self.durations else 0

    @property
    def p95_duration(self) -> float:
        if not self.durations:
            return 0
        sorted_durations = sorted(self.durations)
        idx = int(len(sorted_durations) * 0.95)
        return sorted_durations[min(idx, len(sorted_durations) - 1)]


class WebSocketPerformanceTester:
    """WebSocket性能测试器"""

    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.metrics: Dict[str, PerformanceMetrics] = defaultdict(
            lambda: PerformanceMetrics(operation="")
        )

    async def test_connection_latency(self, iterations: int = 10) -> TestResult:
        """测试连接延迟"""
        test_name = "WebSocket连接延迟测试"
        latencies = []

        try:
            for i in range(iterations):
                start = time.time()
                async with websockets.connect(f"{self.base_url}/ws/chat") as ws:
                    latency = (time.time() - start) * 1000
                    latencies.append(latency)
                    self.metrics["connection"].durations.append(latency)
                await asyncio.sleep(0.1)

            return TestResult(
                test_name=test_name,
                success=True,
                duration_ms=statistics.mean(latencies),
                details={
                    "iterations": iterations,
                    "avg_latency_ms": statistics.mean(latencies),
                    "min_latency_ms": min(latencies),
                    "max_latency_ms": max(latencies)
                }
            )
        except Exception as e:
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=0,
                error=str(e)
            )

    async def test_message_roundtrip(self, iterations: int = 10) -> TestResult:
        """测试消息往返时间"""
        test_name = "WebSocket消息往返测试"
        roundtrip_times = []

        try:
            async with websockets.connect(f"{self.base_url}/ws/chat") as ws:
                # 等待连接确认
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                init_data = json.loads(response)

                if init_data.get("type") != "connection_established":
                    return TestResult(
                        test_name=test_name,
                        success=False,
                        duration_ms=0,
                        error="连接未正确建立"
                    )

                for i in range(iterations):
                    message = {
                        "type": "chat_message",
                        "content": f"性能测试消息 {i}",
                        "mode": "normal"
                    }

                    start = time.time()
                    await ws.send(json.dumps(message))

                    # 等待响应
                    response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    roundtrip = (time.time() - start) * 1000
                    roundtrip_times.append(roundtrip)
                    self.metrics["roundtrip"].durations.append(roundtrip)

            return TestResult(
                test_name=test_name,
                success=True,
                duration_ms=statistics.mean(roundtrip_times),
                details={
                    "iterations": iterations,
                    "avg_roundtrip_ms": statistics.mean(roundtrip_times),
                    "min_roundtrip_ms": min(roundtrip_times),
                    "max_roundtrip_ms": max(roundtrip_times)
                }
            )
        except Exception as e:
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=0,
                error=str(e)
            )

    async def test_concurrent_connections(self, num_connections: int = 50) -> TestResult:
        """测试并发连接"""
        test_name = f"WebSocket并发连接测试 ({num_connections} 连接)"
        start = time.time()
        successful = 0
        failed = 0
        errors = []

        async def connect_and_test(conn_id: int):
            nonlocal successful, failed
            try:
                async with websockets.connect(
                    f"{self.base_url}/ws/chat",
                    timeout=10
                ) as ws:
                    # 等待连接确认
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(response)

                    if data.get("type") == "connection_established":
                        successful += 1
                        # 发送测试消息
                        await ws.send(json.dumps({
                            "type": "ping",
                            "content": f"conn_{conn_id}"
                        }))
                    else:
                        failed += 1
            except Exception as e:
                failed += 1
                errors.append(f"Conn {conn_id}: {str(e)[:50]}")

        try:
            # 创建并发连接
            await asyncio.gather(*[
                connect_and_test(i) for i in range(num_connections)
            ])

            duration = (time.time() - start) * 1000

            return TestResult(
                test_name=test_name,
                success=successful == num_connections,
                duration_ms=duration,
                details={
                    "num_connections": num_connections,
                    "successful": successful,
                    "failed": failed,
                    "success_rate": successful / num_connections * 100,
                    "errors_sample": errors[:5]
                }
            )
        except Exception as e:
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            )

    async def test_chain_generation_performance(self) -> TestResult:
        """测试决策链生成性能"""
        test_name = "决策链生成性能测试"
        stage_times = defaultdict(list)

        try:
            async with websockets.connect(f"{self.base_url}/ws/chat") as ws:
                # 等待连接确认
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)

                start_total = time.time()

                # 发送消息触发决策链生成
                await ws.send(json.dumps({
                    "type": "chat_message",
                    "content": "分析长江流域洪水风险并生成应对方案",
                    "mode": "normal"
                }))

                # 收集所有消息直到完成
                message_count = 0
                last_message_time = time.time()

                while True:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                        message_count += 1
                        current_time = time.time()

                        data = json.loads(response)
                        msg_type = data.get("type", "unknown")

                        # 记录各阶段时间
                        stage_times[msg_type].append(
                            (current_time - last_message_time) * 1000
                        )
                        last_message_time = current_time

                        # 检查是否完成
                        if msg_type in ["execution_complete", "error"]:
                            break

                        # 防止无限等待
                        if message_count > 100:
                            break

                    except asyncio.TimeoutError:
                        break

                total_duration = (time.time() - start_total) * 1000

                return TestResult(
                    test_name=test_name,
                    success=True,
                    duration_ms=total_duration,
                    details={
                        "total_duration_ms": total_duration,
                        "message_count": message_count,
                        "stage_times": {
                            k: {
                                "count": len(v),
                                "avg_ms": statistics.mean(v) if v else 0,
                                "total_ms": sum(v)
                            }
                            for k, v in stage_times.items()
                        }
                    }
                )

        except Exception as e:
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=0,
                error=str(e)
            )

    async def run_all_tests(self) -> List[TestResult]:
        """运行所有测试"""
        print("开始性能测试...")
        print("-" * 80)

        # 测试1: 连接延迟
        print("测试1: WebSocket连接延迟...")
        result = await self.test_connection_latency(10)
        self.results.append(result)
        print(f"  结果: {'✓' if result.success else '✗'} "
              f"平均延迟: {result.details.get('avg_latency_ms', 0):.2f}ms")

        # 测试2: 消息往返
        print("测试2: WebSocket消息往返...")
        result = await self.test_message_roundtrip(5)
        self.results.append(result)
        print(f"  结果: {'✓' if result.success else '✗'} "
              f"平均往返: {result.details.get('avg_roundtrip_ms', 0):.2f}ms")

        # 测试3: 并发连接 (10)
        print("测试3: 并发连接 (10)...")
        result = await self.test_concurrent_connections(10)
        self.results.append(result)
        print(f"  结果: {'✓' if result.success else '✗'} "
              f"成功率: {result.details.get('success_rate', 0):.1f}%")

        # 测试4: 并发连接 (50)
        print("测试4: 并发连接 (50)...")
        result = await self.test_concurrent_connections(50)
        self.results.append(result)
        print(f"  结果: {'✓' if result.success else '✗'} "
              f"成功率: {result.details.get('success_rate', 0):.1f}%")

        # 测试5: 决策链生成
        print("测试5: 决策链生成性能...")
        result = await self.test_chain_generation_performance()
        self.results.append(result)
        print(f"  结果: {'✓' if result.success else '✗'} "
              f"总耗时: {result.details.get('total_duration_ms', 0):.2f}ms")

        print("-" * 80)
        return self.results

    def generate_report(self) -> str:
        """生成测试报告"""
        report = []
        report.append("=" * 80)
        report.append("性能测试报告")
        report.append("=" * 80)
        report.append("")

        # 汇总
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        report.append(f"## 测试汇总")
        report.append(f"- 总测试数: {total_tests}")
        report.append(f"- 通过: {passed_tests}")
        report.append(f"- 失败: {total_tests - passed_tests}")
        report.append("")

        # 详细结果
        report.append("## 详细结果")
        report.append("")

        for result in self.results:
            status = "✓ 通过" if result.success else "✗ 失败"
            report.append(f"### {result.test_name}")
            report.append(f"状态: {status}")
            report.append(f"耗时: {result.duration_ms:.2f}ms")

            if result.details:
                report.append("详细信息:")
                for key, value in result.details.items():
                    if key != "errors_sample":
                        report.append(f"  - {key}: {value}")

            if result.error:
                report.append(f"错误: {result.error}")

            report.append("")

        # 性能指标汇总
        if self.metrics:
            report.append("## 性能指标汇总")
            report.append("")

            for op, metric in self.metrics.items():
                if metric.durations:
                    report.append(f"### {op}")
                    report.append(f"- 平均: {metric.avg_duration:.2f}ms")
                    report.append(f"- 最小: {metric.min_duration:.2f}ms")
                    report.append(f"- 最大: {metric.max_duration:.2f}ms")
                    report.append(f"- P95: {metric.p95_duration:.2f}ms")
                    report.append(f"- 样本数: {len(metric.durations)}")
                    report.append("")

        report.append("=" * 80)

        return "\n".join(report)


async def main():
    """主函数"""
    # 检查后端是否运行
    tester = WebSocketPerformanceTester()

    try:
        # 测试连接
        async with websockets.connect("ws://localhost:8000/ws/chat", timeout=5):
            pass
    except Exception as e:
        print(f"错误: 无法连接到后端服务 (ws://localhost:8000/ws/chat)")
        print(f"请确保后端服务已启动: python -m web.backend.main")
        return 1

    # 运行测试
    await tester.run_all_tests()

    # 生成报告
    report = tester.generate_report()
    print(report)

    # 保存报告
    report_path = os.path.join(
        os.path.dirname(__file__),
        "performance_test_report.md"
    )
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存到: {report_path}")

    # 返回退出码
    failed = sum(1 for r in tester.results if not r.success)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
