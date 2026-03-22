"""
UnitTaskExecutionAgent 交互式测试脚本

使用真实 API_KEY 进行测试，展示完整执行过程

运行前请确保已设置环境变量:
    setx KIMI_API_KEY=your_api_key
"""

import os
import sys

# 自动添加项目 src 到 Python 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 检查 KIMI_API_KEY
def check_api_key():
    """检查 API Key 是否存在"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("=" * 70)
        print("错误: 未找到 KIMI_API_KEY 环境变量")
        print("=" * 70)
        print("\n请按以下步骤设置:")
        print("  1. 打开 PowerShell (管理员)")
        print("  2. 执行: setx KIMI_API_KEY \"your_api_key\"")
        print("  3. 重启终端或重新加载环境变量")
        print("\n或者临时设置 (仅当前终端):")
        print("  $env:KIMI_API_KEY=\"your_api_key\"")
        print("=" * 70)
        return False
    
    # 隐藏部分 key 用于显示
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"✓ KIMI_API_KEY 已配置: {masked_key}")
    return True


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title):
    """打印子章节标题"""
    print(f"\n>>> {title}")
    print("-" * 50)


def demo_1_upstream_tools_sufficient():
    """
    场景1: 上游指定工具充足
    
    说明: 上游Agent指定了所有需要的工具，UnitTaskExecutionAgent
          直接使用，不进行自主选用
    """
    print_section("场景1: 上游指定工具充足（无需自主选用）")
    
    from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
    from flood_decision_agent.core.shared_data_pool import SharedDataPool
    from flood_decision_agent.tools.registry import ToolMetadata, register_tool
    
    # 注册业务工具（模拟上游Agent可用的工具）
    @register_tool(ToolMetadata(
        name="rainfall_forecast_api",
        description="调用气象API获取降雨预报",
        task_types={"hydrological_model"},
        priority=10,
        output_keys={"rainfall_forecast"}
    ))
    def rainfall_forecast_api(data_pool, config):
        location = config.get("location", "北江")
        print(f"    [工具执行] 获取 {location} 降雨预报...")
        return {
            "rainfall_forecast": {
                "location": location,
                "24h": 45.5,
                "48h": 30.2,
                "unit": "mm"
            }
        }
    
    @register_tool(ToolMetadata(
        name="inflow_calculation",
        description="根据降雨计算入库流量",
        task_types={"hydrological_model"},
        priority=20,
        output_keys={"inflow_forecast"}
    ))
    def inflow_calculation(data_pool, config):
        print("    [工具执行] 计算入库流量...")
        rainfall = data_pool.get("rainfall_forecast", {})
        rain_24h = rainfall.get("24h", 0)
        # 简化计算
        peak_flow = rain_24h * 15
        return {
            "inflow_forecast": {
                "peak_flow": peak_flow,
                "unit": "m3/s",
                "calculation_method": "rainfall_runoff"
            }
        }
    
    # 创建Agent和数据池
    agent = UnitTaskExecutionAgent(agent_id="TestAgent1")
    data_pool = SharedDataPool()
    
    print_subsection("上游指定工具列表")
    upstream_tools = [
        {"tool_name": "rainfall_forecast_api", "tool_config": {"location": "飞来峡"}, "priority": 1},
        {"tool_name": "inflow_calculation", "tool_config": {}, "priority": 2}
    ]
    for tool in upstream_tools:
        print(f"  - {tool['tool_name']}: {tool['tool_config']}")
    
    print_subsection("执行过程")
    print("  策略: 上游指定工具充足 → 直接使用，不触发自主选用\n")
    
    result = agent.execute_task(
        node_id="N1_Hydrological",
        task_type="hydrological_model",
        data_pool=data_pool,
        tools=upstream_tools,
        execution_strategy="single",
    )
    
    print_subsection("执行结果")
    print(f"  状态: {result['status']}")
    print(f"  使用工具: {result['metrics']['tools_used']}")
    print(f"  执行策略: {result['metrics']['execution_strategy']}")
    print(f"  耗时: {result['metrics']['elapsed_time_ms']:.2f}ms")
    print(f"\n  输出数据:")
    for key, value in result['output'].items():
        print(f"    - {key}: {value}")


def demo_2_upstream_insufficient_tools():
    """
    场景2: 上游指定工具不足，触发自主选用补充
    
    说明: 上游Agent指定了部分工具，但数量不足以完成任务
          （如 hydrological_model 任务需要至少2个工具），
          UnitTaskExecutionAgent 检测到后自主选用补充
    """
    print_section("场景2: 上游指定工具不足（触发自主选用补充）")
    
    from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
    from flood_decision_agent.core.shared_data_pool import SharedDataPool
    from flood_decision_agent.tools.registry import ToolMetadata, register_tool
    
    # 注册一个水文模型工具（模拟上游只提供了一个）
    @register_tool(ToolMetadata(
        name="rainfall_data_collector",
        description="收集降雨数据",
        task_types={"hydrological_model"},
        priority=10,
        output_keys={"rainfall_data"}
    ))
    def rainfall_data_collector(data_pool, config):
        print("    [工具执行] 收集降雨数据...")
        return {
            "rainfall_data": {"24h": 50.5, "48h": 30.2, "unit": "mm"}
        }
    
    agent = UnitTaskExecutionAgent(agent_id="TestAgent2")
    data_pool = SharedDataPool()
    
    print_subsection("任务需求")
    print("  任务类型: hydrological_model (水文模型)")
    print("  最少需要: 2个工具（数据收集 + 流量计算）")
    
    print_subsection("上游指定工具列表（不足）")
    upstream_tools = [
        {"tool_name": "rainfall_data_collector", "tool_config": {}, "priority": 1}
        # 只提供了1个工具，缺少流量计算工具
    ]
    print(f"  - rainfall_data_collector: 收集降雨数据")
    print(f"  [注意] 缺少流量计算工具！需要补充")
    
    print_subsection("执行过程")
    print("  策略: 检测到工具数量不足 → 触发自主选用补充\n")
    
    result = agent.execute_task(
        node_id="N2_Hydrological",
        task_type="hydrological_model",
        data_pool=data_pool,
        tools=upstream_tools,
        execution_strategy="auto",
    )
    
    print_subsection("执行结果")
    print(f"  状态: {result['status']}")
    print(f"  工具来源:")
    for tool in result['metrics']['tools_used']:
        marker = "[上游]" if tool == "rainfall_data_collector" else "[补充]"
        print(f"    - {tool} {marker}")
    print(f"  执行策略: {result['metrics']['execution_strategy']}")
    print(f"  耗时: {result['metrics']['elapsed_time_ms']:.2f}ms")


def demo_3_upstream_tool_unavailable():
    """
    场景3: 上游指定工具不可用，自主选用替代
    
    说明: 上游Agent指定的工具当前不可用（如服务故障），
          UnitTaskExecutionAgent自主选用替代工具
    """
    print_section("场景3: 上游指定工具不可用（自主选用替代）")
    
    from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
    from flood_decision_agent.core.shared_data_pool import SharedDataPool
    
    agent = UnitTaskExecutionAgent(agent_id="TestAgent3")
    data_pool = SharedDataPool()
    
    print_subsection("上游指定工具列表（包含不可用工具）")
    upstream_tools = [
        {"tool_name": "external_weather_api", "tool_config": {"city": "广州"}, "priority": 1}
        # 这个工具未注册，不可用
    ]
    print(f"  - external_weather_api: [未注册，不可用]")
    
    print_subsection("执行过程")
    print("  策略: 检测到工具不可用 → 自主选用替代工具\n")
    
    result = agent.execute_task(
        node_id="N3_WeatherQuery",
        task_type="data_query",
        data_pool=data_pool,
        tools=upstream_tools,
        execution_strategy="auto",
    )
    
    print_subsection("执行结果")
    print(f"  状态: {result['status']}")
    print(f"  上游指定工具: external_weather_api [不可用]")
    print(f"  自主选用替代: {result['metrics']['tools_used']}")
    print(f"  执行策略: {result['metrics']['execution_strategy']}")


def demo_4_mixed_strategy():
    """
    场景4: 混合策略 - 上游工具 + 自主补充 + 并行执行
    
    说明: 复杂场景，上游指定部分工具，Agent自主补充其他工具，
          使用并行策略同时执行
    """
    print_section("场景4: 混合策略（上游+自主+并行）")
    
    from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
    from flood_decision_agent.core.shared_data_pool import SharedDataPool
    from flood_decision_agent.tools.registry import ToolMetadata, register_tool
    
    # 注册一个业务工具
    @register_tool(ToolMetadata(
        name="dispatch_plan_generator",
        description="生成水库调度方案",
        task_types={"reservoir_dispatch"},
        priority=10,
        output_keys={"dispatch_plan"}
    ))
    def dispatch_plan_generator(data_pool, config):
        print("    [工具执行] 生成调度方案...")
        inflow = data_pool.get("inflow_forecast", {})
        peak = inflow.get("peak_flow", 1000)
        return {
            "dispatch_plan": {
                "strategy": "flood_control",
                "target_peak": peak * 0.8,
                "gates_open": 3
            }
        }
    
    agent = UnitTaskExecutionAgent(agent_id="TestAgent4")
    data_pool = SharedDataPool()
    
    # 准备数据
    data_pool.set("inflow_forecast", {"peak_flow": 15000, "unit": "m3/s"})
    
    print_subsection("任务需求分析")
    print("  任务: 水库调度方案生成 + 执行报告创建")
    print("  需要工具:")
    print("    1. 调度方案生成（上游指定）")
    print("    2. 执行报告创建（缺失，需自主选用）")
    print("    3. 时间戳记录（缺失，需自主选用）")
    
    print_subsection("上游指定工具列表")
    upstream_tools = [
        {"tool_name": "dispatch_plan_generator", "tool_config": {}, "priority": 1}
    ]
    print(f"  - dispatch_plan_generator")
    
    print_subsection("执行过程")
    print("  策略: 上游工具 + 自主补充 → 并行执行\n")
    
    result = agent.execute_task(
        node_id="N4_Dispatch",
        task_type="reservoir_dispatch",
        data_pool=data_pool,
        tools=upstream_tools,
        execution_strategy="parallel",  # 并行执行所有工具
    )
    
    print_subsection("执行结果")
    print(f"  状态: {result['status']}")
    print(f"  工具组合:")
    for tool in result['metrics']['tools_used']:
        marker = "[上游]" if tool == "dispatch_plan_generator" else "[自主]"
        print(f"    - {tool} {marker}")
    print(f"  执行策略: {result['metrics']['execution_strategy']}")
    print(f"  工具数量: {result['metrics']['tool_count']}")
    print(f"  耗时: {result['metrics']['elapsed_time_ms']:.2f}ms")


def demo_5_show_all_tools():
    """展示所有可用工具"""
    print_section("附录: 常用工具库清单")
    
    from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
    
    agent = UnitTaskExecutionAgent(agent_id="ToolViewer")
    
    print_subsection("已注册工具列表")
    tools = agent.list_available_tools()
    
    # 分类显示
    categories = {
        "数据查询": [],
        "计算": [],
        "格式转换": [],
        "日志报告": [],
        "其他": []
    }
    
    for tool_name in sorted(tools):
        info = agent.get_tool_info(tool_name)
        if not info:
            continue
            
        task_types = info.get("task_types", [])
        if "data_query" in task_types:
            categories["数据查询"].append((tool_name, info))
        elif "compute" in task_types or "math" in task_types:
            categories["计算"].append((tool_name, info))
        elif "format" in task_types:
            categories["格式转换"].append((tool_name, info))
        elif "log" in task_types or "report" in task_types:
            categories["日志报告"].append((tool_name, info))
        else:
            categories["其他"].append((tool_name, info))
    
    for category, items in categories.items():
        if items:
            print(f"\n  [{category}]")
            for name, info in items:
                print(f"    - {name}: {info['description']}")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  UnitTaskExecutionAgent 交互式测试")
    print("  策略: 上游指定为主，自主选用为补")
    print("=" * 70)
    
    # 检查 API Key
    if not check_api_key():
        sys.exit(1)
    
    try:
        # 运行所有演示
        demo_1_upstream_tools_sufficient()
        demo_2_upstream_insufficient_tools()
        demo_3_upstream_tool_unavailable()
        demo_4_mixed_strategy()
        demo_5_show_all_tools()
        
        print("\n" + "=" * 70)
        print("  所有测试完成!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
