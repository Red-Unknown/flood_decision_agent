"""高级Pipeline测试脚本

测试Plan模式和Spec模式的复杂Pipeline任务。
"""

import asyncio
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flood_decision_agent.app.real_pipeline import RealPipeline
from flood_decision_agent.agents.decision_chain.mode_detector import ModeDetector, ModeType
from flood_decision_agent.infrastructure.logging import setup_logging

# 配置日志
setup_logging()


async def start_mcp_servers():
    """启动MCP服务器"""
    print("=" * 70)
    print("启动MCP服务器")
    print("=" * 70)
    
    from flood_decision_agent.mcp.clients.base import MCPClientManager
    
    manager = MCPClientManager()
    
    # 从配置加载服务器
    print("\n[1/2] 从配置加载MCP服务器...")
    manager.load_from_config("configs/mcp/servers.yaml")
    
    # 连接所有服务器
    print("\n[2/2] 连接MCP服务器...")
    connected = await manager.connect_all()
    print(f"✓ 已连接 {connected} 个MCP服务器")
    
    # 显示连接状态
    for name, client in manager.clients.items():
        status = "✓ 已连接" if client._connected else "✗ 未连接"
        tool_count = len(client.tools) if hasattr(client, 'tools') else 0
        print(f"  {status}: {name} ({tool_count} 个工具)")
    
    return manager


def test_mode_detection():
    """测试模式检测"""
    print("\n" + "=" * 70)
    print("测试模式检测")
    print("=" * 70)
    
    detector = ModeDetector()
    
    test_cases = [
        ("北京今天天气怎么样？", "简单查询"),
        ("分析未来3天的降雨情况并给出调度建议", "中等复杂度"),
        ("""请帮我完成以下复杂的水利调度分析任务：
1. 收集过去30天的降雨数据
2. 分析流域土壤饱和度
3. 预测未来7天的来水情况
4. 考虑下游生态流量需求
5. 制定多目标优化调度方案
6. 评估不同方案的风险和收益
7. 生成详细的调度报告""", "复杂任务"),
    ]
    
    for user_input, description in test_cases:
        print(f"\n测试: {description}")
        print(f"输入: {user_input[:50]}...")
        
        mode = detector.detect(user_input)
        print(f"检测模式: {mode}")
        
        # 显示详细分析
        metrics = detector._calculate_metrics(user_input)
        print(f"  字符数: {metrics.char_count}")
        print(f"  句子数: {metrics.sentence_count}")
        print(f"  技术术语数: {metrics.technical_term_count}")


def test_simple_mode():
    """测试Simple模式"""
    print("\n" + "=" * 70)
    print("测试Simple模式")
    print("=" * 70)
    
    pipeline = RealPipeline()
    
    user_input = "查询当前时间"
    print(f"\n用户输入: {user_input}")
    
    result = pipeline.run(user_input)
    
    print(f"\n执行结果:")
    print(f"  成功: {result.success}")
    print(f"  执行时间: {result.execution_time_ms:.2f} ms")
    print(f"  决策链节点数: {len(result.decision_chain)}")
    print(f"  执行结果数: {len(result.execution_results)}")
    
    if result.execution_results:
        for res in result.execution_results:
            print(f"    - {res['node_id']}: {res['status']}")
    
    return result


def test_plan_mode():
    """测试Plan模式"""
    print("\n" + "=" * 70)
    print("测试Plan模式")
    print("=" * 70)
    
    pipeline = RealPipeline()
    
    user_input = """请帮我制定一个水库调度计划：
1. 获取未来3天的降雨预报
2. 计算入库流量
3. 考虑下游防洪安全
4. 制定泄洪方案"""
    
    print(f"\n用户输入: {user_input}")
    
    result = pipeline.run(user_input)
    
    print(f"\n执行结果:")
    print(f"  成功: {result.success}")
    print(f"  执行时间: {result.execution_time_ms:.2f} ms")
    print(f"  决策链节点数: {len(result.decision_chain)}")
    print(f"  执行结果数: {len(result.execution_results)}")
    
    if result.decision_chain:
        print(f"\n决策链节点:")
        for i, node in enumerate(result.decision_chain):
            print(f"  {i+1}. {node.get('node_id')} ({node.get('task_type')})")
    
    if result.execution_results:
        print(f"\n执行详情:")
        for res in result.execution_results:
            status_icon = "✓" if res['status'] == 'success' else "✗"
            print(f"  {status_icon} {res['node_id']}: {res['status']}")
            if 'result' in res and isinstance(res['result'], dict):
                output = res['result'].get('output', {})
                if output:
                    print(f"      输出: {str(output)[:100]}...")
    
    return result


def test_spec_mode():
    """测试Spec模式"""
    print("\n" + "=" * 70)
    print("测试Spec模式")
    print("=" * 70)
    
    pipeline = RealPipeline()
    
    user_input = """请完成以下专业水利调度分析任务：

【任务背景】
某流域近期连续降雨，土壤饱和度较高，需要制定科学的洪水调度方案。

【具体要求】
1. 数据收集阶段：
   - 收集过去7天的逐小时降雨数据
   - 获取当前土壤饱和度数据
   - 查询水库当前水位和库容

2. 水文分析阶段：
   - 使用单位线法计算径流
   - 预测未来72小时的入库流量过程
   - 分析不同降雨情景下的洪水规模

3. 调度决策阶段：
   - 考虑下游防洪标准（50年一遇）
   - 评估水库大坝安全
   - 兼顾下游生态流量需求（不小于10m³/s）
   - 优化发电效益

4. 方案输出阶段：
   - 生成3套调度方案（保守/适中/激进）
   - 每套方案包含详细的泄洪过程
   - 风险评估和应急预案
   - 完整的决策报告

【约束条件】
- 最大泄流量不超过5000m³/s
- 水位控制不超过汛限水位2m
- 调度周期为72小时"""
    
    print(f"\n用户输入: {user_input[:200]}...")
    
    result = pipeline.run(user_input)
    
    print(f"\n执行结果:")
    print(f"  成功: {result.success}")
    print(f"  执行时间: {result.execution_time_ms:.2f} ms")
    print(f"  决策链节点数: {len(result.decision_chain)}")
    print(f"  执行结果数: {len(result.execution_results)}")
    
    if result.decision_chain:
        print(f"\n决策链节点:")
        for i, node in enumerate(result.decision_chain):
            print(f"  {i+1}. {node.get('node_id')} ({node.get('task_type')})")
    
    return result


def test_with_mcp_tools():
    """测试使用MCP工具的Pipeline"""
    print("\n" + "=" * 70)
    print("测试使用MCP工具的Pipeline")
    print("=" * 70)
    
    from flood_decision_agent.agents.task_executor.mcp_integration import setup_mcp_for_executor
    from flood_decision_agent.agents.task_executor.executor import UnitTaskExecutionAgent
    from flood_decision_agent.core.shared_data_pool import SharedDataPool
    
    # 创建执行器
    print("\n[1/3] 创建任务执行器...")
    executor = UnitTaskExecutionAgent()
    print(f"✓ 基础工具: {len(executor.tool_registry.list_tools())} 个")
    
    # 设置MCP
    print("\n[2/3] 设置MCP集成...")
    
    async def setup():
        mcp_integration = await setup_mcp_for_executor(executor)
        mcp_tools = mcp_integration.get_registered_mcp_tools()
        print(f"✓ MCP工具: {len(mcp_tools)} 个")
        
        # 查找hydrology相关工具
        hydro_tools = [t for t in mcp_tools if "hydro" in t.lower() or "rain" in t.lower()]
        print(f"✓ 水文/降雨工具: {len(hydro_tools)} 个")
        for tool in hydro_tools[:5]:
            print(f"    - {tool}")
        
        return mcp_integration
    
    mcp_integration = asyncio.run(setup())
    
    # 执行测试任务
    print("\n[3/3] 执行测试任务...")
    data_pool = SharedDataPool()
    data_pool.set("city", "北京")
    
    async def execute():
        # 尝试执行降雨相关工具
        rainfall_tools = [t for t in mcp_integration.get_registered_mcp_tools() 
                         if "rain" in t.lower()]
        
        if rainfall_tools:
            tool_name = rainfall_tools[0]
            print(f"  执行工具: {tool_name}")
            
            result = await mcp_integration.execute_mcp_tool(
                tool_name=tool_name,
                data_pool=data_pool,
                config={"city": "北京"}
            )
            
            if result.get("success"):
                print(f"  ✓ 执行成功")
                print(f"    结果: {str(result.get('result', {}))[:150]}...")
            else:
                print(f"  ✗ 执行失败: {result.get('error')}")
        else:
            print("  未找到降雨工具，跳过执行测试")
        
        await mcp_integration.close()
    
    asyncio.run(execute())
    
    print("\n✓ 测试完成")


async def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("高级Pipeline测试")
    print("测试Plan模式和Spec模式的复杂任务")
    print("=" * 70)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 检查API Key
    if not os.environ.get("KIMI_API_KEY"):
        print("\n✗ 错误: 需要设置 KIMI_API_KEY 环境变量")
        sys.exit(1)
    
    try:
        # 1. 启动MCP服务器
        # mcp_manager = await start_mcp_servers()
        
        # 2. 测试模式检测
        test_mode_detection()
        
        # 3. 测试Simple模式
        test_simple_mode()
        
        # 4. 测试Plan模式
        test_plan_mode()
        
        # 5. 测试Spec模式
        test_spec_mode()
        
        # 6. 测试MCP工具
        # test_with_mcp_tools()
        
        # 关闭MCP服务器
        # await mcp_manager.close_all()
        
        print("\n" + "=" * 70)
        print("所有测试完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
