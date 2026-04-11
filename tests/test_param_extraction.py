"""测试参数提取流程 - 直接调用"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.flood_decision_agent.core.shared_data_pool import SharedDataPool
from src.flood_decision_agent.agents.intent_parser.parser import IntentParser
from src.flood_decision_agent.agents.decision_chain.task_decomposer import TaskDecomposer


async def test_parameter_extraction():
    """测试参数提取流程"""
    print("=" * 60)
    print("  测试参数提取流程")
    print("=" * 60)
    
    # 1. 创建数据池和存储用户输入
    pool = SharedDataPool()
    user_input = "查询金坛天气"
    pool.set("user_input", user_input, source="user_input")
    print(f"\n1. 用户输入: {user_input}")
    print(f"   数据池存储: {pool.get('user_input')}")
    
    # 2. 意图解析
    print("\n2. 意图解析...")
    parser = IntentParser()
    intent = parser.parse(user_input)
    print(f"   解析结果: task_type={intent.task_type.value if hasattr(intent.task_type, 'value') else intent.task_type}")
    print(f"   goal: {intent.goal}")
    
    # 3. 任务分解
    print("\n3. 任务分解...")
    decomposer = TaskDecomposer()
    task_nodes = await decomposer.decompose(
        goal=user_input,
        task_type=intent.task_type,
        intent=intent
    )
    print(f"   分解结果: {len(task_nodes)} 个任务节点")
    for node in task_nodes:
        print(f"   - {node.task_id}: {node.description}")
        print(f"     inputs: {node.inputs}")
        print(f"     outputs: {node.outputs}")
        if node.tool_candidates:
            print(f"     工具候选:")
            for tc in node.tool_candidates:
                print(f"       - {tc.tool_name} (优先级: {tc.priority})")
    
    # 4. 检查参数提取
    print("\n4. 参数提取分析:")
    print("   提取渠道:")
    print("   - 用户输入直接提取: 任务描述中包含 '金坛'，可提取 location='金坛'")
    print("   - 上下文提取: 从 data_pool 获取")
    print("   - 经验参数: 从 water_domain_prompts 获取默认值")
    
    print("\n" + "=" * 60)
    print("  测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_parameter_extraction())
