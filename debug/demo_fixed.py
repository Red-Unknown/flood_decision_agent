"""
修复后的演示脚本 - 自动处理环境变量和模块导入
"""

import os
import sys

# ========== 自动修复模块导入 ==========
# 添加项目 src 目录到 Python 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# ========== API Key 设置 ==========
# 方法1: 从环境变量读取（推荐）
api_key = os.environ.get("KIMI_API_KEY")

# 方法2: 如果环境变量未设置，可以在这里直接设置（仅测试用）
# 注意：生产环境请勿硬编码 API Key
if not api_key:
    # 取消下面一行的注释并填入你的 API Key
    # api_key = "your_api_key_here"
    pass

if not api_key:
    print("=" * 70)
    print("错误: 未找到 KIMI_API_KEY")
    print("=" * 70)
    print("\n请设置环境变量：")
    print("  PowerShell: $env:KIMI_API_KEY='your_key'")
    print("  CMD: set KIMI_API_KEY=your_key")
    print("\n或在脚本中取消注释并设置 api_key 变量")
    sys.exit(1)

# 设置到环境变量（供其他模块使用）
os.environ["KIMI_API_KEY"] = api_key
masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
print(f"✓ KIMI_API_KEY 已配置: {masked_key}")

# ========== 继续导入和运行 ==========
try:
    from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
    from flood_decision_agent.core.shared_data_pool import SharedDataPool
    from flood_decision_agent.tools.registry import ToolMetadata, register_tool
    print("✓ 模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    print("\n请确保已安装包: pip install -e .")
    sys.exit(1)


# ========== 演示代码 ==========
def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_1():
    """场景1: 上游指定工具充足"""
    print_section("场景1: 上游指定工具充足")
    
    @register_tool(ToolMetadata(
        name="demo_rainfall_api",
        description="降雨预报API",
        task_types={"hydrological_model"},
        priority=10,
        output_keys={"rainfall"}
    ))
    def demo_rainfall_api(data_pool, config):
        return {"rainfall": {"24h": 50.5, "unit": "mm"}}
    
    agent = UnitTaskExecutionAgent(agent_id="Demo1", enable_common_tools=False)
    data_pool = SharedDataPool()
    
    result = agent.execute_task(
        node_id="N1",
        task_type="hydrological_model",
        data_pool=data_pool,
        tools=[{"tool_name": "demo_rainfall_api", "tool_config": {}}],
        execution_strategy="single",
    )
    
    print(f"状态: {result['status']}")
    print(f"工具: {result['metrics']['tools_used']}")
    print(f"输出: {result['output']}")


def demo_2():
    """场景2: 上游工具不足，自主补充"""
    print_section("场景2: 上游工具不足，自主补充")
    
    agent = UnitTaskExecutionAgent(agent_id="Demo2")
    data_pool = SharedDataPool()
    
    result = agent.execute_task(
        node_id="N2",
        task_type="data_query",  # 会自主选用常用工具
        data_pool=data_pool,
        tools=[],  # 空列表触发自主选用
        execution_strategy="auto",
    )
    
    print(f"状态: {result['status']}")
    print(f"自主选用工具: {result['metrics']['tools_used']}")


def main():
    print("\n" + "=" * 70)
    print("  UnitTaskExecutionAgent 修复版演示")
    print("=" * 70)
    
    demo_1()
    demo_2()
    
    print("\n" + "=" * 70)
    print("  演示完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
