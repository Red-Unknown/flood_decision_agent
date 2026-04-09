"""测试脚本：输出完整返回数据 - 参照 e2e 测试报告格式"""

import asyncio
import json
import time
import uuid
import websockets
from datetime import datetime


def create_test_report(test_id: str, test_input: str, start_time: datetime, messages: list, errors: list):
    """创建 e2e 格式的测试报告"""
    end_time = datetime.now()
    total_duration_ms = (end_time - start_time).total_seconds() * 1000

    message_types = {}
    stage_timings = {}
    total_data_received_bytes = 0
    stages = []
    sent_messages = 0
    received_messages = 0

    for msg in messages:
        direction = msg.get("direction")
        msg_type = msg.get("message_type", msg.get("type"))
        size = msg.get("size_bytes", 0)

        if direction == "sent":
            sent_messages += 1
        elif direction == "received":
            received_messages += 1

        total_data_received_bytes += size

        if msg_type not in message_types:
            message_types[msg_type] = 0
        message_types[msg_type] += 1

        stage_name = get_stage_name(msg_type)
        if stage_name not in stage_timings:
            stage_timings[stage_name] = {
                "first_seen_at_ms": msg.get("elapsed_ms", 0),
                "message_count": 0
            }
        stage_timings[stage_name]["message_count"] += 1

    stage_order = ["连接建立", "消息处理"]
    for stage_name in stage_timings:
        if stage_name not in stage_order:
            stage_order.append(stage_name)

    for stage_name in stage_order:
        if stage_name in stage_timings:
            stages.append({
                "stage_name": stage_name,
                "duration_ms": stage_timings[stage_name]["message_count"] * 10,
                "message_count": stage_timings[stage_name]["message_count"]
            })

    report = {
        "test_id": test_id,
        "test_input": test_input,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_duration_ms": total_duration_ms,
        "messages": messages,
        "stages": stages,
        "errors": errors,
        "summary": {
            "total_messages": len(messages),
            "sent_messages": sent_messages,
            "received_messages": received_messages,
            "message_type_distribution": message_types,
            "stage_timings": stage_timings,
            "total_data_received_bytes": total_data_received_bytes,
            "has_errors": len(errors) > 0
        }
    }

    return report


def get_stage_name(message_type: str) -> str:
    """根据消息类型获取阶段名称"""
    stage_map = {
        "connected": "连接建立",
        "user_message_confirm": "用户消息确认",
        "chain_generation_stage": "决策链生成",
        "intent_parsed": "意图解析",
        "task_graph_generated": "任务图生成",
        "chain_generated": "决策链生成完成",
        "execution_started": "执行开始",
        "task_update": "任务更新",
        "execution_progress": "执行进度",
        "execution_complete": "执行完成",
        "assistant_message": "AI回复",
        "document_chunk": "文档生成",
        "document_complete": "文档完成"
    }
    return stage_map.get(message_type, "消息处理")


async def test():
    test_id = f"test_{uuid.uuid4().hex[:8]}"
    test_input = "分析金坛降雨情况"
    uri = "ws://localhost:8001/ws/chat/test_001"

    print("=" * 60)
    print(f"测试ID: {test_id}")
    print(f"测试问题: {test_input}")
    print("=" * 60)

    start_time = datetime.now()
    messages = []
    errors = []

    async with websockets.connect(uri, max_size=10_000_000) as ws:
        message = {
            "type": "chat_message",
            "content": test_input,
            "session_id": test_id
        }

        print("\n[发送消息]")
        send_msg = json.dumps(message, ensure_ascii=False)
        print(send_msg)

        start_time_connect = datetime.now()
        connect_elapsed = (start_time_connect - start_time).total_seconds() * 1000

        messages.append({
            "direction": "sent",
            "message_type": "chat_message",
            "timestamp": start_time_connect.isoformat(),
            "elapsed_ms": connect_elapsed,
            "size_bytes": len(send_msg),
            "data_preview": {
                "type": "chat_message",
                "content": test_input,
                "conversation_id": test_id,
                "timestamp": time.time()
            }
        })

        await ws.send(send_msg)

        print("\n[接收数据]")

        while True:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=120)
                data = json.loads(response)
                receive_time = datetime.now()
                elapsed_ms = (receive_time - start_time).total_seconds() * 1000

                msg_type = data.get("type", "unknown")

                if msg_type == "connected":
                    direction = "received"
                    message_type = "connected"
                elif msg_type == "user_message_confirm":
                    direction = "received"
                    message_type = "user_message_confirm"
                elif msg_type in ["chain_generation_stage", "intent_parsed", "task_graph_generated", "chain_generated"]:
                    direction = "received"
                    message_type = msg_type
                elif msg_type in ["execution_started", "task_update", "execution_progress", "execution_complete"]:
                    direction = "received"
                    message_type = msg_type
                elif msg_type == "assistant_message":
                    direction = "received"
                    message_type = "assistant_message"
                elif msg_type in ["document_chunk", "document_complete"]:
                    direction = "received"
                    message_type = msg_type
                else:
                    direction = "received"
                    message_type = msg_type

                msg_entry = {
                    "direction": direction,
                    "message_type": message_type,
                    "timestamp": receive_time.isoformat(),
                    "elapsed_ms": elapsed_ms,
                    "size_bytes": len(response),
                    "data_preview": data
                }
                messages.append(msg_entry)

                print(f"收到: type={msg_type}, elapsed_ms={elapsed_ms:.2f}ms, size={len(response)}bytes")
                if msg_type == "error":
                    print(f"  错误详情: {data}")

                if msg_type in ["assistant_message", "error"]:
                    break

            except asyncio.TimeoutError:
                print("\n[超时]")
                errors.append({"error": "Timeout", "timestamp": datetime.now().isoformat()})
                break

    report = create_test_report(test_id, test_input, start_time, messages, errors)

    output_file = f"test_reports/e2e_test_report_{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("测试报告汇总")
    print("=" * 60)
    print(f"测试ID: {test_id}")
    print(f"测试输入: {test_input}")
    print(f"开始时间: {report['start_time']}")
    print(f"结束时间: {report['end_time']}")
    print(f"总耗时: {report['total_duration_ms']:.2f}ms")
    print(f"总消息数: {report['summary']['total_messages']}")
    print(f"发送消息: {report['summary']['sent_messages']}")
    print(f"接收消息: {report['summary']['received_messages']}")
    print(f"数据接收: {report['summary']['total_data_received_bytes']}bytes")
    print(f"错误数: {len(errors)}")
    print("\n消息类型分布:")
    for msg_type, count in report['summary']['message_type_distribution'].items():
        print(f"  - {msg_type}: {count}")
    print(f"\n报告已保存到: {output_file}")


if __name__ == "__main__":
    asyncio.run(test())
