"""
端到端测试脚本 - 模拟用户使用简单模式输入"分析金坛降雨情况"

功能：
1. 建立 WebSocket 连接
2. 发送用户消息
3. 收集所有返回给前端的数据以及返回的时机
4. 生成详细的测试报告

使用方法：
    python test_e2e_chat_analysis.py

环境要求：
    - KIMI_API_KEY 环境变量已设置
    - 后端服务运行在 localhost:8000
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

import websockets
from websockets.exceptions import ConnectionClosed


# 检查环境变量
if not os.environ.get("KIMI_API_KEY"):
    print("需要kimi_api_key")
    sys.exit(1)


@dataclass
class MessageRecord:
    """消息记录"""
    direction: str  # "sent" 或 "received"
    message_type: str
    timestamp: float
    elapsed_ms: float  # 相对于测试开始的时间（毫秒）
    data: Dict[str, Any] = field(default_factory=dict)
    size_bytes: int = 0


@dataclass
class StageTiming:
    """阶段耗时"""
    stage_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    message_count: int = 0

    def complete(self, end_time: float):
        self.end_time = end_time
        self.duration_ms = (end_time - self.start_time) * 1000


@dataclass
class TestReport:
    """测试报告"""
    test_id: str
    test_input: str
    start_time: float
    end_time: Optional[float] = None
    total_duration_ms: Optional[float] = None
    messages: List[MessageRecord] = field(default_factory=list)
    stages: List[StageTiming] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_input": self.test_input,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "total_duration_ms": self.total_duration_ms,
            "messages": [
                {
                    "direction": m.direction,
                    "message_type": m.message_type,
                    "timestamp": datetime.fromtimestamp(m.timestamp).isoformat(),
                    "elapsed_ms": round(m.elapsed_ms, 2),
                    "size_bytes": m.size_bytes,
                    "data_preview": self._truncate_data(m.data),
                }
                for m in self.messages
            ],
            "stages": [
                {
                    "stage_name": s.stage_name,
                    "duration_ms": round(s.duration_ms, 2) if s.duration_ms else None,
                    "message_count": s.message_count,
                }
                for s in self.stages
            ],
            "errors": self.errors,
            "summary": self.summary,
        }

    def _truncate_data(self, data: Dict[str, Any], max_length: int = 200) -> Dict[str, Any]:
        """截断数据以便报告阅读"""
        preview = {}
        for key, value in data.items():
            if key in ["content", "accumulated", "message"] and isinstance(value, str):
                if len(value) > max_length:
                    preview[key] = value[:max_length] + "..."
                else:
                    preview[key] = value
            elif key in ["tasks", "nodes", "edges", "results"] and isinstance(value, list):
                preview[key] = f"[{len(value)} items]"
            elif key in ["task_graph", "intent", "summary", "metadata", "detail"] and isinstance(value, dict):
                preview[key] = f"{{{len(value)} fields}}"
            else:
                preview[key] = value
        return preview


class E2EChatTester:
    """端到端聊天测试器"""

    def __init__(self, ws_url: str = "ws://localhost:8002/ws/chat/"):
        self.ws_url = ws_url
        self.conversation_id = f"test_{uuid.uuid4().hex[:8]}"
        self.report = TestReport(
            test_id=self.conversation_id,
            test_input="分析金坛降雨情况",
            start_time=time.time(),
        )
        self.current_stage: Optional[StageTiming] = None
        self.message_count = 0
        self._stage_map = {
            "connected": "连接建立",
            "user_message_confirm": "用户消息确认",
            "intent_parsed": "意图解析",
            "chain_generation_stage": "决策链生成",
            "task_graph_generated": "任务图生成",
            "chain_generated": "决策链生成完成",
            "execution_started": "执行开始",
            "task_update": "任务更新",
            "execution_progress": "执行进度",
            "execution_complete": "执行完成",
            "assistant_message": "AI回复",
            "error": "错误",
            "complete": "完成",
        }

    def _record_message(self, direction: str, message: Dict[str, Any]):
        """记录消息"""
        current_time = time.time()
        elapsed_ms = (current_time - self.report.start_time) * 1000
        message_type = message.get("type", "unknown")

        # 序列化计算大小
        try:
            size_bytes = len(json.dumps(message, ensure_ascii=False).encode("utf-8"))
        except:
            size_bytes = 0

        record = MessageRecord(
            direction=direction,
            message_type=message_type,
            timestamp=current_time,
            elapsed_ms=elapsed_ms,
            data=message,
            size_bytes=size_bytes,
        )
        self.report.messages.append(record)
        self.message_count += 1

        # 更新当前阶段的消息计数
        if self.current_stage:
            self.current_stage.message_count += 1

        return record

    def _start_stage(self, stage_name: str):
        """开始新阶段"""
        # 完成上一个阶段
        if self.current_stage:
            self.current_stage.complete(time.time())

        # 开始新阶段
        self.current_stage = StageTiming(
            stage_name=stage_name,
            start_time=time.time(),
        )
        self.report.stages.append(self.current_stage)

    def _complete_current_stage(self):
        """完成当前阶段"""
        if self.current_stage:
            self.current_stage.complete(time.time())
            self.current_stage = None

    async def run_test(self) -> TestReport:
        """运行测试"""
        uri = f"{self.ws_url}{self.conversation_id}"
        print(f"\n{'='*60}")
        print(f"开始端到端测试")
        print(f"{'='*60}")
        print(f"WebSocket URL: {uri}")
        print(f"测试输入: {self.report.test_input}")
        print(f"开始时间: {datetime.fromtimestamp(self.report.start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print(f"{'='*60}\n")

        try:
            async with websockets.connect(uri) as websocket:
                # 1. 等待连接成功消息
                print("[1/4] 等待连接建立...")
                self._start_stage("连接建立")

                response = await websocket.recv()
                data = json.loads(response)
                self._record_message("received", data)

                if data.get("type") == "connected":
                    print(f"  ✓ 连接成功: conversation_id={data.get('conversation_id')}")
                    self._complete_current_stage()
                else:
                    raise Exception(f"连接失败: {data}")

                # 2. 发送用户消息
                print("\n[2/4] 发送用户消息...")
                self._start_stage("消息处理")

                user_message = {
                    "type": "chat_message",
                    "content": self.report.test_input,
                    "conversation_id": self.conversation_id,
                    "timestamp": time.time(),
                }
                await websocket.send(json.dumps(user_message, ensure_ascii=False))
                self._record_message("sent", user_message)
                print(f"  ✓ 已发送: {self.report.test_input}")

                # 3. 接收并记录所有响应
                print("\n[3/4] 接收后端响应...")
                print(f"  等待消息流...")

                message_type_stats = {}
                stage_timings = {}

                while True:
                    try:
                        # 设置超时，避免无限等待
                        response = await asyncio.wait_for(websocket.recv(), timeout=120.0)
                        data = json.loads(response)
                        message_type = data.get("type", "unknown")

                        # 记录消息
                        record = self._record_message("received", data)

                        # 统计消息类型
                        message_type_stats[message_type] = message_type_stats.get(message_type, 0) + 1

                        # 打印关键消息
                        self._print_message(message_type, data, record.elapsed_ms)

                        # 检测阶段变化
                        if message_type in self._stage_map:
                            stage_name = self._stage_map[message_type]
                            if stage_name not in stage_timings:
                                stage_timings[stage_name] = {
                                    "first_seen_at_ms": record.elapsed_ms,
                                    "message_count": 0,
                                }
                            stage_timings[stage_name]["message_count"] += 1

                        # 检测结束条件
                        if message_type == "assistant_message":
                            print(f"\n  ✓ 收到 AI 回复，处理完成")
                            self._complete_current_stage()
                            break

                        if message_type == "error":
                            error_info = {
                                "code": data.get("code", "UNKNOWN"),
                                "message": data.get("message", ""),
                                "timestamp": record.elapsed_ms,
                            }
                            self.report.errors.append(error_info)
                            print(f"\n  ✗ 收到错误: {error_info['code']} - {error_info['message']}")

                            # 某些错误可能表示流程结束
                            if data.get("code") in ["GENERATION_FAILED", "EXECUTION_FAILED", "PROCESSING_FAILED"]:
                                self._complete_current_stage()
                                break

                    except asyncio.TimeoutError:
                        print("\n  ✗ 等待响应超时（120秒）")
                        self.report.errors.append({
                            "code": "TIMEOUT",
                            "message": "等待响应超时",
                            "timestamp": (time.time() - self.report.start_time) * 1000,
                        })
                        self._complete_current_stage()
                        break

                # 4. 生成报告
                print("\n[4/4] 生成测试报告...")
                self.report.end_time = time.time()
                self.report.total_duration_ms = (self.report.end_time - self.report.start_time) * 1000

                # 生成摘要
                self.report.summary = {
                    "total_messages": self.message_count,
                    "sent_messages": len([m for m in self.report.messages if m.direction == "sent"]),
                    "received_messages": len([m for m in self.report.messages if m.direction == "received"]),
                    "message_type_distribution": message_type_stats,
                    "stage_timings": stage_timings,
                    "total_data_received_bytes": sum(m.size_bytes for m in self.report.messages if m.direction == "received"),
                    "has_errors": len(self.report.errors) > 0,
                }

                print(f"  ✓ 报告生成完成")

        except ConnectionRefusedError:
            error_msg = "无法连接到后端服务，请确保服务运行在 localhost:8000"
            print(f"\n  ✗ {error_msg}")
            self.report.errors.append({
                "code": "CONNECTION_REFUSED",
                "message": error_msg,
            })
        except Exception as e:
            error_msg = f"测试过程中发生错误: {str(e)}"
            print(f"\n  ✗ {error_msg}")
            self.report.errors.append({
                "code": "TEST_ERROR",
                "message": error_msg,
            })

        return self.report

    def _print_message(self, message_type: str, data: Dict[str, Any], elapsed_ms: float):
        """打印消息摘要"""
        timestamp = f"[{elapsed_ms:8.2f}ms]"

        if message_type == "user_message_confirm":
            print(f"  {timestamp} → 用户消息已确认")

        elif message_type == "intent_parsed":
            intent = data.get("intent", {})
            task_type = intent.get("task_type", "unknown")
            confidence = data.get("confidence", 0)
            print(f"  {timestamp} → 意图解析完成: type={task_type}, confidence={confidence}")

        elif message_type == "chain_generation_stage":
            stage = data.get("stage", "")
            progress = data.get("progress", 0)
            stage_name = data.get("stage_name", "")
            print(f"  {timestamp} → 决策链生成: {stage_name} ({stage}) progress={progress:.2f}")

        elif message_type == "task_graph_generated":
            task_count = data.get("total_count", 0)
            reliability = data.get("reliability_score", 0)
            print(f"  {timestamp} → 任务图生成完成: {task_count} 个任务, 可靠性={reliability:.2f}")

        elif message_type == "chain_generated":
            mode = data.get("mode", "unknown")
            print(f"  {timestamp} → 决策链生成完成: mode={mode}")

        elif message_type == "execution_started":
            total = data.get("total_tasks", 0)
            print(f"  {timestamp} → 执行开始: {total} 个任务")

        elif message_type == "task_update":
            task_id = data.get("task_id", "")[:20]
            status = data.get("status", "unknown")
            print(f"  {timestamp} → 任务更新: {task_id}... status={status}")

        elif message_type == "execution_progress":
            completed = data.get("completed_tasks", 0)
            total = data.get("total_tasks", 0)
            progress = data.get("progress", 0)
            print(f"  {timestamp} → 执行进度: {completed}/{total} ({progress*100:.1f}%)")

        elif message_type == "execution_complete":
            success = data.get("success", False)
            print(f"  {timestamp} → 执行完成: success={success}")

        elif message_type == "assistant_message":
            content = data.get("content", "")[:50]
            if len(data.get("content", "")) > 50:
                content += "..."
            print(f"  {timestamp} → AI回复: {content}")

        elif message_type == "error":
            code = data.get("code", "UNKNOWN")
            message = data.get("message", "")[:50]
            print(f"  {timestamp} ✗ 错误: {code} - {message}")

    def save_report(self, output_dir: str = "./test_reports") -> str:
        """保存测试报告"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"e2e_test_report_{self.conversation_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.report.to_dict(), f, ensure_ascii=False, indent=2)

        return filepath

    def print_summary(self):
        """打印测试摘要"""
        print(f"\n{'='*60}")
        print("测试摘要")
        print(f"{'='*60}")
        print(f"测试ID: {self.report.test_id}")
        print(f"测试输入: {self.report.test_input}")
        print(f"总耗时: {self.report.total_duration_ms:.2f}ms" if self.report.total_duration_ms else "总耗时: N/A")
        print(f"总消息数: {self.report.summary.get('total_messages', 0)}")
        print(f"  - 发送: {self.report.summary.get('sent_messages', 0)}")
        print(f"  - 接收: {self.report.summary.get('received_messages', 0)}")
        print(f"总数据量: {self.report.summary.get('total_data_received_bytes', 0)} bytes")
        print(f"错误数: {len(self.report.errors)}")

        if self.report.summary.get("message_type_distribution"):
            print(f"\n消息类型分布:")
            for msg_type, count in sorted(self.report.summary["message_type_distribution"].items()):
                print(f"  - {msg_type}: {count}")

        if self.report.summary.get("stage_timings"):
            print(f"\n阶段耗时:")
            for stage_name, timing in sorted(
                self.report.summary["stage_timings"].items(),
                key=lambda x: x[1]["first_seen_at_ms"]
            ):
                print(f"  - {stage_name}: {timing['first_seen_at_ms']:.2f}ms ({timing['message_count']} 条消息)")

        if self.report.errors:
            print(f"\n错误详情:")
            for error in self.report.errors:
                print(f"  - [{error.get('code', 'UNKNOWN')}] {error.get('message', '')}")

        print(f"{'='*60}\n")


async def main():
    """主函数"""
    # 创建测试器
    tester = E2EChatTester(ws_url="ws://localhost:8002/ws/chat/")

    # 运行测试
    report = await tester.run_test()

    # 打印摘要
    tester.print_summary()

    # 保存报告
    report_path = tester.save_report()
    print(f"详细报告已保存: {report_path}")

    # 返回退出码
    if report.errors:
        print("\n测试完成，但存在错误")
        return 1
    else:
        print("\n测试成功完成")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
