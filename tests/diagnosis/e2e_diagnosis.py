"""
端到端诊断测试
测试完整的决策链生成和执行流程，检测阻塞问题
"""

import asyncio
import json
import time
import sys
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import defaultdict
import websockets

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@dataclass
class MessageTiming:
    """消息时间记录"""
    message_type: str
    timestamp: float
    latency_from_previous: float
    data_size: int


@dataclass
class DiagnosisResult:
    """诊断结果"""
    test_name: str
    success: bool
    total_duration_ms: float
    message_timings: List[MessageTiming] = field(default_factory=list)
    blocking_detected: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class BlockingDetector:
    """阻塞检测器"""

    def __init__(self, threshold_ms: float = 500.0):
        self.threshold_ms = threshold_ms
        self.blocking_events: List[Dict] = []

    def check_latency(self, message_type: str, latency_ms: float, context: str = ""):
        """检查延迟是否超过阈值"""
        if latency_ms > self.threshold_ms:
            severity = "HIGH" if latency_ms > 5000 else "MEDIUM" if latency_ms > 1000 else "LOW"
            self.blocking_events.append({
                "message_type": message_type,
                "latency_ms": latency_ms,
                "severity": severity,
                "context": context,
                "timestamp": time.time()
            })

    def get_report(self) -> List[Dict]:
        """获取阻塞事件报告"""
        return sorted(self.blocking_events, key=lambda x: x["latency_ms"], reverse=True)


class E2EDiagnosisTester:
    """端到端诊断测试器"""

    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.detector = BlockingDetector(threshold_ms=500.0)
        self.results: List[DiagnosisResult] = []

    async def test_normal_mode_flow(self) -> DiagnosisResult:
        """测试普通模式完整流程"""
        test_name = "普通模式完整流程诊断"
        print(f"\n开始测试: {test_name}")

        timings: List[MessageTiming] = []
        errors: List[str] = []
        start_time = time.time()
        last_message_time = start_time

        try:
            async with websockets.connect(
                f"{self.base_url}/ws/chat",
                timeout=10
            ) as ws:
                print("  ✓ WebSocket连接建立")

                # 等待连接确认
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(response)

                    if data.get("type") != "connection_established":
                        errors.append(f"连接确认失败: {data}")
                        return DiagnosisResult(
                            test_name=test_name,
                            success=False,
                            total_duration_ms=(time.time() - start_time) * 1000,
                            errors=errors
                        )

                    current_time = time.time()
                    latency = (current_time - last_message_time) * 1000
                    timings.append(MessageTiming(
                        message_type="connection_established",
                        timestamp=current_time,
                        latency_from_previous=latency,
                        data_size=len(response)
                    ))
                    last_message_time = current_time
                    print(f"  ✓ 连接确认接收 ({latency:.2f}ms)")

                except asyncio.TimeoutError:
                    errors.append("连接确认超时")
                    return DiagnosisResult(
                        test_name=test_name,
                        success=False,
                        total_duration_ms=(time.time() - start_time) * 1000,
                        errors=errors
                    )

                # 发送用户消息
                await ws.send(json.dumps({
                    "type": "chat_message",
                    "content": "分析长江流域洪水风险",
                    "mode": "normal"
                }))
                print("  ✓ 用户消息已发送")

                # 接收所有消息直到完成
                message_count = 0
                max_messages = 50
                stage_received = set()

                while message_count < max_messages:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                        message_count += 1
                        current_time = time.time()

                        data = json.loads(response)
                        msg_type = data.get("type", "unknown")
                        stage_received.add(msg_type)

                        latency = (current_time - last_message_time) * 1000
                        timings.append(MessageTiming(
                            message_type=msg_type,
                            timestamp=current_time,
                            latency_from_previous=latency,
                            data_size=len(response)
                        ))

                        # 检测阻塞
                        self.detector.check_latency(msg_type, latency, f"Message {message_count}")

                        last_message_time = current_time

                        print(f"  ✓ 收到 [{msg_type}] ({latency:.2f}ms)")

                        # 检查是否完成
                        if msg_type == "execution_complete":
                            print("  ✓ 执行完成")
                            break
                        elif msg_type == "error":
                            errors.append(f"收到错误消息: {data.get('message', 'Unknown')}")
                            break

                    except asyncio.TimeoutError:
                        errors.append(f"消息接收超时 (已接收 {message_count} 条消息)")
                        break

            total_duration = (time.time() - start_time) * 1000

            return DiagnosisResult(
                test_name=test_name,
                success=len(errors) == 0 and "execution_complete" in stage_received,
                total_duration_ms=total_duration,
                message_timings=timings,
                blocking_detected=self.detector.get_report(),
                errors=errors
            )

        except Exception as e:
            return DiagnosisResult(
                test_name=test_name,
                success=False,
                total_duration_ms=(time.time() - start_time) * 1000,
                errors=[str(e)]
            )

    async def test_plan_mode_flow(self) -> DiagnosisResult:
        """测试Plan模式完整流程"""
        test_name = "Plan模式完整流程诊断"
        print(f"\n开始测试: {test_name}")

        timings: List[MessageTiming] = []
        errors: List[str] = []
        start_time = time.time()
        last_message_time = start_time

        try:
            async with websockets.connect(
                f"{self.base_url}/ws/chat",
                timeout=10
            ) as ws:
                # 等待连接确认
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)

                if data.get("type") != "connection_established":
                    errors.append("连接确认失败")
                    return DiagnosisResult(
                        test_name=test_name,
                        success=False,
                        total_duration_ms=(time.time() - start_time) * 1000,
                        errors=errors
                    )

                last_message_time = time.time()

                # 发送Plan模式消息
                await ws.send(json.dumps({
                    "type": "chat_message",
                    "content": "制定长江流域洪水应急响应计划",
                    "mode": "plan"
                }))
                print("  ✓ Plan模式消息已发送")

                # 接收Plan生成消息
                plan_received = False
                message_count = 0

                while not plan_received and message_count < 20:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                        message_count += 1
                        current_time = time.time()

                        data = json.loads(response)
                        msg_type = data.get("type", "unknown")

                        latency = (current_time - last_message_time) * 1000
                        timings.append(MessageTiming(
                            message_type=msg_type,
                            timestamp=current_time,
                            latency_from_previous=latency,
                            data_size=len(response)
                        ))
                        self.detector.check_latency(msg_type, latency)
                        last_message_time = current_time

                        print(f"  ✓ 收到 [{msg_type}] ({latency:.2f}ms)")

                        if msg_type == "user_message_confirm":
                            plan_received = True
                            break
                        elif msg_type == "error":
                            errors.append(f"错误: {data.get('message', 'Unknown')}")
                            break

                    except asyncio.TimeoutError:
                        errors.append("等待Plan确认超时")
                        break

                if not plan_received:
                    errors.append("未收到Plan确认消息")
                    return DiagnosisResult(
                        test_name=test_name,
                        success=False,
                        total_duration_ms=(time.time() - start_time) * 1000,
                        message_timings=timings,
                        errors=errors
                    )

                # 发送Plan确认
                await ws.send(json.dumps({
                    "type": "confirm_plan",
                    "confirmed": True
                }))
                print("  ✓ Plan确认已发送")

                # 接收后续消息
                stage_received = set()
                while message_count < 50:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                        message_count += 1
                        current_time = time.time()

                        data = json.loads(response)
                        msg_type = data.get("type", "unknown")
                        stage_received.add(msg_type)

                        latency = (current_time - last_message_time) * 1000
                        timings.append(MessageTiming(
                            message_type=msg_type,
                            timestamp=current_time,
                            latency_from_previous=latency,
                            data_size=len(response)
                        ))
                        self.detector.check_latency(msg_type, latency)
                        last_message_time = current_time

                        print(f"  ✓ 收到 [{msg_type}] ({latency:.2f}ms)")

                        if msg_type == "execution_complete":
                            print("  ✓ 执行完成")
                            break
                        elif msg_type == "error":
                            errors.append(f"错误: {data.get('message', 'Unknown')}")
                            break

                    except asyncio.TimeoutError:
                        errors.append(f"消息接收超时 (已接收 {message_count} 条)")
                        break

            total_duration = (time.time() - start_time) * 1000

            return DiagnosisResult(
                test_name=test_name,
                success=len(errors) == 0 and "execution_complete" in stage_received,
                total_duration_ms=total_duration,
                message_timings=timings,
                blocking_detected=self.detector.get_report(),
                errors=errors
            )

        except Exception as e:
            return DiagnosisResult(
                test_name=test_name,
                success=False,
                total_duration_ms=(time.time() - start_time) * 1000,
                errors=[str(e)]
            )

    async def test_error_handling(self) -> DiagnosisResult:
        """测试错误处理流程"""
        test_name = "错误处理流程诊断"
        print(f"\n开始测试: {test_name}")

        timings: List[MessageTiming] = []
        errors: List[str] = []
        start_time = time.time()

        try:
            async with websockets.connect(
                f"{self.base_url}/ws/chat",
                timeout=10
            ) as ws:
                # 等待连接确认
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)

                # 发送空消息（应该触发错误）
                await ws.send(json.dumps({
                    "type": "chat_message",
                    "content": "",
                    "mode": "normal"
                }))

                # 接收响应
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    data = json.loads(response)
                    msg_type = data.get("type", "unknown")

                    print(f"  ✓ 收到 [{msg_type}]")

                    if msg_type == "error":
                        print("  ✓ 错误处理正常")
                        return DiagnosisResult(
                            test_name=test_name,
                            success=True,
                            total_duration_ms=(time.time() - start_time) * 1000,
                            message_timings=timings,
                            errors=[]
                        )
                    else:
                        errors.append(f"预期错误消息，但收到 {msg_type}")

                except asyncio.TimeoutError:
                    errors.append("错误响应超时")

            return DiagnosisResult(
                test_name=test_name,
                success=len(errors) == 0,
                total_duration_ms=(time.time() - start_time) * 1000,
                message_timings=timings,
                errors=errors
            )

        except Exception as e:
            return DiagnosisResult(
                test_name=test_name,
                success=False,
                total_duration_ms=(time.time() - start_time) * 1000,
                errors=[str(e)]
            )

    async def run_all_tests(self) -> List[DiagnosisResult]:
        """运行所有诊断测试"""
        print("=" * 80)
        print("开始端到端诊断测试")
        print("=" * 80)

        # 测试1: 普通模式
        result = await self.test_normal_mode_flow()
        self.results.append(result)

        # 等待一下再开始下一个测试
        await asyncio.sleep(2)

        # 测试2: Plan模式
        result = await self.test_plan_mode_flow()
        self.results.append(result)

        # 等待一下
        await asyncio.sleep(2)

        # 测试3: 错误处理
        result = await self.test_error_handling()
        self.results.append(result)

        print("\n" + "=" * 80)
        print("诊断测试完成")
        print("=" * 80)

        return self.results

    def generate_report(self) -> str:
        """生成诊断报告"""
        report = []
        report.append("=" * 80)
        report.append("端到端诊断报告")
        report.append("=" * 80)
        report.append("")

        # 汇总
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        report.append("## 测试汇总")
        report.append(f"- 总测试数: {total_tests}")
        report.append(f"- 通过: {passed_tests}")
        report.append(f"- 失败: {total_tests - passed_tests}")
        report.append("")

        # 阻塞检测汇总
        all_blocking = []
        for result in self.results:
            all_blocking.extend(result.blocking_detected)

        if all_blocking:
            report.append("## 阻塞检测结果")
            report.append(f"检测到 {len(all_blocking)} 个潜在阻塞事件")
            report.append("")

            # 按严重程度分组
            by_severity = defaultdict(list)
            for event in all_blocking:
                by_severity[event["severity"]].append(event)

            for severity in ["HIGH", "MEDIUM", "LOW"]:
                if severity in by_severity:
                    report.append(f"### {severity} 级别 ({len(by_severity[severity])} 个)")
                    for event in by_severity[severity]:
                        report.append(f"- {event['message_type']}: {event['latency_ms']:.2f}ms")
                        if event['context']:
                            report.append(f"  上下文: {event['context']}")
                    report.append("")
        else:
            report.append("## 阻塞检测结果")
            report.append("✓ 未检测到超过500ms的阻塞事件")
            report.append("")

        # 详细结果
        report.append("## 详细测试结果")
        report.append("")

        for result in self.results:
            status = "✓ 通过" if result.success else "✗ 失败"
            report.append(f"### {result.test_name}")
            report.append(f"状态: {status}")
            report.append(f"总耗时: {result.total_duration_ms:.2f}ms")
            report.append(f"消息数: {len(result.message_timings)}")

            if result.message_timings:
                # 计算各阶段统计
                stage_stats = defaultdict(lambda: {"count": 0, "total_ms": 0, "max_ms": 0})
                for timing in result.message_timings:
                    stage = timing.message_type
                    stage_stats[stage]["count"] += 1
                    stage_stats[stage]["total_ms"] += timing.latency_from_previous
                    stage_stats[stage]["max_ms"] = max(stage_stats[stage]["max_ms"], timing.latency_from_previous)

                report.append("各阶段统计:")
                for stage, stats in sorted(stage_stats.items()):
                    avg = stats["total_ms"] / stats["count"] if stats["count"] > 0 else 0
                    report.append(f"  - {stage}: 平均 {avg:.2f}ms, 最大 {stats['max_ms']:.2f}ms, 次数 {stats['count']}")

            if result.blocking_detected:
                report.append("阻塞事件:")
                for event in result.blocking_detected[:5]:  # 只显示前5个
                    report.append(f"  - {event['message_type']}: {event['latency_ms']:.2f}ms ({event['severity']})")

            if result.errors:
                report.append("错误:")
                for error in result.errors:
                    report.append(f"  - {error}")

            report.append("")

        report.append("=" * 80)

        return "\n".join(report)


async def main():
    """主函数"""
    # 检查后端是否运行
    try:
        async with websockets.connect("ws://localhost:8000/ws/chat", timeout=5):
            pass
    except Exception as e:
        print(f"错误: 无法连接到后端服务")
        print(f"请确保后端服务已启动")
        return 1

    # 运行诊断测试
    tester = E2EDiagnosisTester()
    await tester.run_all_tests()

    # 生成报告
    report = tester.generate_report()
    print("\n" + report)

    # 保存报告
    report_path = os.path.join(
        os.path.dirname(__file__),
        "e2e_diagnosis_report.md"
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
