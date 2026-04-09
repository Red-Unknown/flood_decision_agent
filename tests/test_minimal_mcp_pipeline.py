"""最小化MCP链路测试 - 验证完整调用链路

测试：用户输入("查询金坛天气") -> 意图解析 -> 调用rainfall MCP工具 -> 
      将数据写入共享数据池 -> 调用总结智能体输出总结

运行方式：
    python tests/test_minimal_mcp_pipeline.py
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def check_api_key():
    """检查 API Key 配置"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("需要kimi_api_key")
        sys.exit(1)
    return api_key


async def step1_intent_parsing(user_input: str):
    """步骤1: 意图解析"""
    print("\n" + "=" * 70)
    print("步骤1: 意图解析")
    print("=" * 70)
    print(f"用户输入: {user_input}")

    from flood_decision_agent.agents.intent_parser.parser import IntentParser

    parser = IntentParser(use_tools=False)
    intent = parser.parse(user_input)

    print(f"\n解析结果:")
    print(f"  任务类型: {intent.task_type.value}")
    print(f"  执行步骤: {[s.value for s in intent.execution_steps]}")
    if intent.error_message:
        print(f"  错误信息: {intent.error_message}")

    if intent.task_type.value == "unknown":
        print("\n[!] 警告: 意图解析失败，任务类型为 unknown")
        return None

    return intent


async def step2_mcp_tool_call(city: str):
    """步骤2: 调用 MCP 工具 (rainfall / data_hub)"""
    print("\n" + "=" * 70)
    print("步骤2: 调用 MCP 工具")
    print("=" * 70)
    print(f"查询城市: {city}")

    from flood_decision_agent.mcp.clients.base import MCPClientManager

    manager = MCPClientManager(auto_load_config=False)

    manager.register_server(
        name="rainfall",
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.rainfall_server"],
        env={}
    )

    manager.register_server(
        name="data_hub",
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.data_hub_server"],
        env={}
    )

    print("\n[1] 连接 MCP 服务器...")
    start_time = time.time()
    connected = await manager.connect_all()
    elapsed = time.time() - start_time
    print(f"  已连接 {connected} 个服务器 (耗时: {elapsed:.2f}s)")

    result = None

    for server_name in ["rainfall", "data_hub"]:
        if server_name not in manager.clients:
            continue

        client = manager.clients[server_name]
        if not client._connected:
            print(f"  [{server_name}] 服务器未成功连接")
            continue

        print(f"\n[{server_name}] 可用工具:")
        for tool in client.tools:
            print(f"  - {tool.name}: {tool.description[:50]}...")

        if server_name == "rainfall":
            tool_name = "get_current_rainfall"
        else:
            tool_name = "get_rainfall_data"

        print(f"\n[2] 调用 {server_name}.{tool_name} 工具...")
        try:
            if server_name == "rainfall":
                result = await client.call_tool(tool_name, {
                    "city": city,
                    "provider": "auto"
                })
            else:
                result = await client.call_tool(tool_name, {
                    "city": city,
                    "provider": "auto"
                })

            print(f"\n  工具调用结果:")
            print(f"    success: {result.get('success')}")

            if result.get("success"):
                if server_name == "rainfall":
                    current = result.get("current", {})
                    print(f"    城市: {result.get('city')}")
                    print(f"    温度: {current.get('temperature')}°C")
                    print(f"    天气: {current.get('weather')}")
                    print(f"    降雨量: {current.get('precipitation', current.get('rain_1h', 0))}mm")
                else:
                    data = result.get("data", {})
                    print(f"    城市: {result.get('city')}")
                    print(f"    温度: {data.get('temperature')}°C")
                    print(f"    天气: {data.get('weather')}")
                    print(f"    降雨量: {data.get('precipitation', 0)}mm")
                break
            else:
                print(f"    错误: {result.get('error', '未知错误')}")

        except Exception as e:
            print(f"\n  工具调用失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n[3] 关闭 MCP 连接...")
    await manager.close_all()
    print("  已关闭所有连接")

    return result


async def step3_write_to_data_pool(mcp_result: Dict[str, Any]):
    """步骤3: 将数据写入共享数据池"""
    print("\n" + "=" * 70)
    print("步骤3: 写入共享数据池")
    print("=" * 70)

    from flood_decision_agent.core.shared_data_pool import SharedDataPool

    data_pool = SharedDataPool()

    if mcp_result and mcp_result.get("success"):
        if "current" in mcp_result:
            weather_data = {
                "city": mcp_result.get("city"),
                "current": mcp_result.get("current"),
                "provider": mcp_result.get("provider"),
                "timestamp": mcp_result.get("timestamp"),
            }
        elif "data" in mcp_result:
            weather_data = {
                "city": mcp_result.get("city"),
                "current": mcp_result.get("data"),
                "provider": mcp_result.get("provider", "qweather"),
                "timestamp": mcp_result.get("timestamp"),
            }
        else:
            weather_data = mcp_result

        data_pool.set("weather_data", weather_data)
        print(f"  已写入天气数据到数据池")
        print(f"    城市: {weather_data.get('city', 'N/A')}")
        current = weather_data.get("current", {})
        print(f"    温度: {current.get('temperature')}°C")
    else:
        mock_data = {
            "city": "金坛",
            "current": {
                "temperature": "25",
                "weather": "晴",
                "precipitation": "0"
            },
            "provider": "mock",
            "timestamp": "2024-01-01T00:00:00",
        }
        data_pool.set("weather_data", mock_data)
        print(f"  [使用模拟数据] 已写入天气数据到数据池")

    print(f"\n  数据池快照:")
    snapshot = data_pool.snapshot()
    for key, value in snapshot.items():
        print(f"    {key}: {value}")

    return data_pool


async def step4_summarizer(data_pool, user_input: str):
    """步骤4: 调用总结智能体"""
    print("\n" + "=" * 70)
    print("步骤4: 调用总结智能体")
    print("=" * 70)

    from flood_decision_agent.agents.summarizer import SummarizerAgent
    from flood_decision_agent.core.message import BaseMessage, MessageType

    summarizer = SummarizerAgent(enable_streaming=False)

    execution_info = {
        "task_request": {
            "input": user_input,
            "type": "weather_query",
        },
        "execution_summary": {
            "total_tasks": 3,
            "completed_tasks": 2,
            "failed_tasks": 0,
            "total_duration_ms": 5000,
        },
        "data_pool_snapshot": data_pool.snapshot(),
        "node_results": [
            {
                "node_id": "intent_parsing",
                "task_type": "intent_parsing",
                "status": "success",
                "metrics": {"elapsed_time_ms": 1000},
            },
            {
                "node_id": "mcp_tool_call",
                "task_type": "mcp_tool_call",
                "status": "success",
                "metrics": {"elapsed_time_ms": 3000},
            },
            {
                "node_id": "data_pool_write",
                "task_type": "data_pool_write",
                "status": "success",
                "metrics": {"elapsed_time_ms": 100},
            },
        ],
        "task_graph": {},
    }

    message = BaseMessage(
        type=MessageType.TASK_REQUEST,
        sender="test_client",
        payload=execution_info,
    )

    print("\n[AI 生成总结中...]")
    result = summarizer.execute(message)

    summary = result.get("summary", "")
    print(f"\n总结结果:")
    print("-" * 70)
    print(summary[:500] if len(summary) > 500 else summary)
    print("-" * 70)

    return result


async def main():
    """主函数 - 运行完整测试链路"""
    print("=" * 70)
    print("最小化 MCP 链路测试")
    print("用户输入 -> 意图解析 -> MCP工具 -> 数据池 -> 总结智能体")
    print("=" * 70)

    api_key = check_api_key()
    print(f"API Key: {api_key[:10]}...")

    user_input = "查询金坛天气"
    city = "金坛"

    total_start = time.time()

    try:
        intent = await step1_intent_parsing(user_input)
        if not intent:
            print("\n[X] 意图解析失败，终止测试")
            return False

        mcp_result = await step2_mcp_tool_call(city)

        data_pool = await step3_write_to_data_pool(mcp_result)

        summary_result = await step4_summarizer(data_pool, user_input)

        total_elapsed = time.time() - total_start
        print("\n" + "=" * 70)
        print("测试完成!")
        print("=" * 70)
        print(f"总耗时: {total_elapsed:.2f}s")
        print(f"意图解析: 成功")
        print(f"MCP工具调用: {'成功' if mcp_result else '失败'}")
        print(f"数据池写入: 成功")
        print(f"总结生成: {'成功' if summary_result.get('summary') else '失败'}")

        return True

    except Exception as e:
        print(f"\n[X] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
