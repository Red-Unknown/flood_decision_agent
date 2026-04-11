"""完整的端到端测试 - 验证参数提取流程"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.flood_decision_agent.core.shared_data_pool import SharedDataPool
from src.flood_decision_agent.agents.intent_parser.parser import IntentParser
from src.flood_decision_agent.agents.decision_chain.task_decomposer import TaskDecomposer
from src.flood_decision_agent.agents.parameter_planner import ParameterPlanner


async def test_full_pipeline():
    """测试完整的参数提取和处理流程"""
    print("=" * 70)
    print("  完整端到端测试 - 参数提取流程")
    print("=" * 70)
    
    # 1. 用户输入
    user_input = "查询金坛天气"
    print(f"\n📥 Step 1: 用户输入")
    print(f"   输入: {user_input}")
    
    # 2. 创建数据池并存储用户输入
    pool = SharedDataPool()
    pool.set("raw_user_input", user_input, source="user_input")
    print(f"\n📦 Step 2: 数据池存储")
    print(f"   raw_user_input: {pool.get('raw_user_input')}")
    print(f"   来源: {pool.get_source('raw_user_input')}")
    
    # 3. 意图解析
    print(f"\n🔍 Step 3: 意图解析")
    parser = IntentParser()
    intent = parser.parse(user_input)
    print(f"   task_type: {intent.task_type.value if hasattr(intent.task_type, 'value') else intent.task_type}")
    print(f"   goal: {intent.goal}")
    print(f"   raw_input: {intent.raw_input}")
    
    # 4. 任务分解
    print(f"\n📋 Step 4: 任务分解")
    decomposer = TaskDecomposer()
    task_nodes = await decomposer.decompose(
        goal=user_input,
        task_type=intent.task_type,
        intent=intent
    )
    print(f"   分解结果: {len(task_nodes)} 个任务节点")
    for node in task_nodes:
        print(f"   - 节点ID: {node.task_id}")
        print(f"     任务类型: {node.task_type}")
        print(f"     描述: {node.description}")
        print(f"     输入: {node.inputs}")
        print(f"     输出: {node.outputs}")
        if node.tool_candidates:
            print(f"     工具候选:")
            for tc in node.tool_candidates:
                print(f"       * {tc.tool_name} (优先级: {tc.priority})")
    
    # 5. 参数提取渠道分析
    print(f"\n🔧 Step 5: 参数提取渠道分析")
    print("   参数可以通过以下渠道获取:")
    print("   ┌─────────────────────────────────────────────────────────────┐")
    print("   │ 渠道1: USER_INPUT (用户直接输入)                            │")
    print("   │   - 从用户查询中提取: '金坛' -> city='金坛'                 │")
    print("   │   - 实现方式: LLM 解析用户输入                               │")
    print("   ├─────────────────────────────────────────────────────────────┤")
    print("   │ 渠道2: DATA_POOL (前置任务输出/上下文)                      │")
    print("   │   - 从 data_pool 获取上下文数据                             │")
    print("   │   - 实现方式: 从 context: 命名空间读取                       │")
    print("   ├─────────────────────────────────────────────────────────────┤")
    print("   │ 渠道3: EXPERIENCE (水利领域经验参数)                        │")
    print("   │   - 从 water_domain_prompts 获取默认值                      │")
    print("   │   - 实现方式: THRESHOLDS 中的预设值                         │")
    print("   ├─────────────────────────────────────────────────────────────┤")
    print("   │ 渠道4: USER_PROVIDED (用户澄清回答)                         │")
    print("   │   - ParameterPlanner 触发澄清请求                           │")
    print("   │   - 实现方式: ClarificationRequest/Response 机制            │")
    print("   └─────────────────────────────────────────────────────────────┘")
    
    # 6. ParameterPlanner 测试（模拟）
    print(f"\n⚙️ Step 6: ParameterPlanner 测试")
    planner = ParameterPlanner()
    print(f"   ParameterPlanner 已创建")
    print(f"   - llm_client: {planner.llm_client}")
    print(f"   - state: {planner.state.value if hasattr(planner.state, 'value') else planner.state}")
    print(f"   - on_clarification_needed: {planner.on_clarification_needed}")
    
    print(f"\n📊 总结:")
    print(f"   ✅ IntentParser 解析结果: task_type={intent.task_type.value}, goal={intent.goal}")
    print(f"   ✅ TaskDecomposer 分解结果: {len(task_nodes)} 个节点")
    print(f"   ✅ 工具推荐: {sum(len(n.tool_candidates) for n in task_nodes)} 个工具候选")
    print(f"   ⚠️  ParameterPlanner 需要 LLM client 才能完整工作")
    
    print("\n" + "=" * 70)
    print("  测试完成")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
