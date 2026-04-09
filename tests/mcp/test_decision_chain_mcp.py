"""测试DecisionChainGeneratorAgent的MCP工具自动选择功能

验证决策链生成器是否能自动为节点分配MCP工具。
"""

import asyncio
import os
import sys
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flood_decision_agent.agents.decision_chain.generator import DecisionChainGeneratorAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.infra.logging import setup_logging

# 配置日志
setup_logging()


def test_decision_chain_with_mcp():
    """测试DecisionChainGeneratorAgent的MCP工具自动选择"""
    print("\n" + "=" * 70)
    print("测试DecisionChainGeneratorAgent的MCP工具自动选择")
    print("=" * 70)

    # 创建Agent（启用MCP）
    print("\n[1/4] 创建DecisionChainGeneratorAgent（启用MCP）...")
    agent = DecisionChainGeneratorAgent(enable_mcp=True)
    print("  ✓ Agent创建成功")

    # 测试用例
    test_cases = [
        {
            "name": "数据收集任务",
            "input": "查询北京未来3天的降雨数据",
            "expected_tools": ["data", "query"],
        },
        {
            "name": "报告生成任务",
            "input": "生成洪水调度分析报告",
            "expected_tools": ["report", "doc"],
        },
        {
            "name": "调度决策任务",
            "input": "制定水库泄洪调度方案",
            "expected_tools": ["plan", "dispatch"],
        },
    ]

    for case in test_cases:
        print(f"\n[2/4] 测试: {case['name']}")
        print(f"  输入: {case['input']}")

        # 构建消息
        message = BaseMessage(
            type=MessageType.TASK_REQUEST,
            sender="TestClient",
            receiver="DecisionChainGenerator",
            payload={
                "input": case['input'],
                "input_type": "natural_language",
            },
        )

        # 执行决策链生成
        start_time = time.time()
        response = agent.execute(message)
        elapsed = (time.time() - start_time) * 1000

        # 检查结果
        task_graph = response.payload.get("task_graph")
        metadata = response.payload.get("metadata", {})

        print(f"\n  执行结果:")
        print(f"    耗时: {elapsed:.2f} ms")
        print(f"    模式: {metadata.get('mode', 'unknown')}")

        if task_graph:
            nodes_dict = task_graph.get_all_nodes()
            print(f"    节点数: {len(nodes_dict)}")

            # 检查MCP工具分配
            mcp_enabled_nodes = 0
            for node_id, node in nodes_dict.items():
                node_metadata = node.metadata or {}
                mcp_tools = node_metadata.get("mcp_tools", [])
                if mcp_tools:
                    mcp_enabled_nodes += 1
                    print(f"    节点 {node_id}: {len(mcp_tools)} 个MCP工具")
                    for tool in mcp_tools:
                        print(f"      - {tool['tool_name']} ({tool['server_name']})")

            print(f"    MCP工具分配: {mcp_enabled_nodes}/{len(nodes_dict)} 个节点")
        else:
            print("    ✗ 未生成TaskGraph")


def test_mcp_initialization():
    """测试MCP初始化"""
    print("\n" + "=" * 70)
    print("测试MCP初始化")
    print("=" * 70)

    agent = DecisionChainGeneratorAgent(enable_mcp=True)

    print("\n[3/4] 初始化MCP客户端管理器...")
    try:
        # 检查是否已有事件循环
        try:
            loop = asyncio.get_running_loop()
            # 如果在异步环境中，创建新任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, agent.initialize_mcp())
                success = future.result()
        except RuntimeError:
            # 没有事件循环，使用 asyncio.run
            success = asyncio.run(agent.initialize_mcp())

        if success:
            print(f"  ✓ MCP初始化成功")
            print(f"    缓存的MCP工具数: {len(agent._mcp_tools_cache)}")

            # 显示可用工具
            if agent._mcp_tools_cache:
                print(f"\n  可用MCP工具:")
                for tool_name, tool_info in list(agent._mcp_tools_cache.items())[:5]:
                    server = tool_info.get('server_name', 'unknown')
                    print(f"    - {tool_name} ({server})")
        else:
            print("  ✗ MCP初始化失败")

    except Exception as e:
        print(f"  ✗ MCP初始化异常: {e}")


def test_mcp_tool_selection():
    """测试MCP工具选择逻辑"""
    print("\n" + "=" * 70)
    print("测试MCP工具选择逻辑")
    print("=" * 70)

    from flood_decision_agent.core.task_types import ExecutionTaskType

    agent = DecisionChainGeneratorAgent(enable_mcp=True)

    # 先初始化MCP
    print("\n[4/4] 初始化MCP...")
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, agent.initialize_mcp())
                future.result()
        except RuntimeError:
            asyncio.run(agent.initialize_mcp())
    except Exception as e:
        print(f"  警告: MCP初始化失败: {e}")
        print("  将使用空缓存测试工具选择逻辑")

    # 测试不同任务类型的工具选择
    test_cases = [
        (ExecutionTaskType.DATA_COLLECTION, "收集降雨数据", ["data", "query"]),
        (ExecutionTaskType.REPORTING, "生成报告", ["report", "doc"]),
        (ExecutionTaskType.DECISION, "决策支持", ["decision", "plan"]),
        (ExecutionTaskType.SIMULATION, "水文模型", ["hydro", "model"]),
    ]

    print("\n  工具选择测试结果:")
    for task_type, description, expected_keywords in test_cases:
        context = {"description": description, "user_input": description}
        matched_tools = agent._find_mcp_tools_for_task(task_type, context)

        if matched_tools:
            print(f"    {task_type.value}: ✓ 找到 {len(matched_tools)} 个工具")
            for tool in matched_tools[:2]:
                print(f"      - {tool['tool_name']} (匹配: {tool['matched_keyword']})")
        else:
            print(f"    {task_type.value}: - 未找到匹配工具")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("DecisionChainGeneratorAgent MCP工具自动选择功能测试")
    print("=" * 70)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 检查API Key
    if not os.environ.get("KIMI_API_KEY"):
        print("\n✗ 错误: 需要设置 KIMI_API_KEY 环境变量")
        print("  请运行: $env:KIMI_API_KEY='your-api-key'")
        sys.exit(1)

    try:
        # 1. 测试MCP初始化
        test_mcp_initialization()

        # 2. 测试MCP工具选择
        test_mcp_tool_selection()

        # 3. 测试完整决策链生成
        test_decision_chain_with_mcp()

        print("\n" + "=" * 70)
        print("所有测试完成！")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
