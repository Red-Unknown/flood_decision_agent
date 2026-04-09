"""统一优化器测试（使用真实API）

测试 UnifiedOptimizer 的三种策略：
- simple: 轻量级优化
- plan: Plan模式优化
- spec: Spec模式优化
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from flood_decision_agent.agents.decision_chain.unified_optimizer import UnifiedOptimizer
from flood_decision_agent.agents.decision_chain.task_decomposer import TaskNodeInfo, TaskType


def create_sample_tasks():
    """创建示例任务节点"""
    return [
        TaskNodeInfo(
            task_id="task_001",
            task_type=TaskType.DATA_COLLECTION,
            description="采集降雨数据",
            inputs=[],
            outputs=["rainfall_data"],
            dependencies=[],
            metadata={"tool": "rainfall_sensor"},
        ),
        TaskNodeInfo(
            task_id="task_002",
            task_type=TaskType.DATA_COLLECTION,
            description="采集上游流量数据",
            inputs=[],
            outputs=["upstream_flow"],
            dependencies=[],
            metadata={"tool": "flow_meter"},
        ),
        TaskNodeInfo(
            task_id="task_003",
            task_type=TaskType.PREDICTION,
            description="预测未来来水",
            inputs=["rainfall_data", "upstream_flow"],
            outputs=["inflow_forecast"],
            dependencies=["task_001", "task_002"],
            metadata={"tool": "flood_forecast_model"},
        ),
        TaskNodeInfo(
            task_id="task_004",
            task_type=TaskType.DATA_COLLECTION,
            description="获取当前水库状态",
            inputs=[],
            outputs=["current_state"],
            dependencies=[],
            metadata={"tool": "reservoir_monitor"},
        ),
        TaskNodeInfo(
            task_id="task_005",
            task_type=TaskType.CALCULATION,
            description="计算调度方案",
            inputs=["inflow_forecast", "current_state"],
            outputs=["dispatch_plan"],
            dependencies=["task_003", "task_004"],
            metadata={"tool": "dispatch_optimizer"},
        ),
        TaskNodeInfo(
            task_id="task_006",
            task_type=TaskType.DECISION,
            description="审核调度方案",
            inputs=["dispatch_plan"],
            outputs=["approved_plan"],
            dependencies=["task_005"],
            metadata={"requires_human": True},
        ),
        TaskNodeInfo(
            task_id="task_007",
            task_type=TaskType.EXECUTION,
            description="执行调度操作",
            inputs=["approved_plan"],
            outputs=["execution_result"],
            dependencies=["task_006"],
            metadata={"tool": "gate_controller"},
        ),
    ]


def test_simple_strategy():
    """测试Simple策略"""
    print("\n" + "=" * 70)
    print(" " * 25 + "Simple策略测试")
    print("=" * 70)
    
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("\n❌ KIMI_API_KEY 环境变量未设置")
        return False
    
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    try:
        # 创建优化器
        optimizer = UnifiedOptimizer(strategy="simple", api_key=api_key)
        print(f"✓ 优化器初始化成功")
        print(f"  策略信息: {optimizer.get_strategy_info()}")
        
        # 创建示例任务
        tasks = create_sample_tasks()
        print(f"\n✓ 创建{len(tasks)}个示例任务")
        
        # 执行优化
        print("\n执行优化...")
        result = optimizer.optimize(
            task_nodes=tasks,
            user_input="洪水调度决策",
            business_type="flood_dispatch",
            execution_type="chain",
            entities={"reservoir": "三峡"},
            mcp_tools=[
                {"name": "flood_forecast_model", "description": "洪水预报模型"},
                {"name": "dispatch_optimizer", "description": "调度优化器"},
                {"name": "gate_controller", "description": "闸门控制器"},
            ],
        )
        
        # 验证结果
        print(f"\n优化结果:")
        print(f"  - 策略: {result['strategy']}")
        print(f"  - 来源: {result['source']}")
        print(f"  - 可靠性评分: {result['reliability_score']:.2f}")
        print(f"  - 通过阈值: {result['passed']}")
        print(f"  - 备选链数量: {len(result['alternatives'])}")
        print(f"  - 迭代次数: {result['iterations']}")
        
        if result['issues']:
            print(f"  - 问题: {len(result['issues'])}个")
            for issue in result['issues'][:3]:
                print(f"    * {issue}")
        
        print("\n✓ Simple策略测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ Simple策略测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plan_strategy():
    """测试Plan策略"""
    print("\n" + "=" * 70)
    print(" " * 25 + "Plan策略测试")
    print("=" * 70)
    
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("\n❌ KIMI_API_KEY 环境变量未设置")
        return False
    
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    try:
        # 创建优化器
        optimizer = UnifiedOptimizer(strategy="plan", api_key=api_key)
        print(f"✓ 优化器初始化成功")
        print(f"  策略信息: {optimizer.get_strategy_info()}")
        
        # 创建示例任务
        tasks = create_sample_tasks()
        print(f"\n✓ 创建{len(tasks)}个示例任务")
        
        # 执行优化
        print("\n执行优化（使用LLM）...")
        result = optimizer.optimize(
            task_nodes=tasks,
            user_input="洪水调度决策",
            business_type="flood_dispatch",
            execution_type="chain",
            entities={"reservoir": "三峡", "basin": "长江流域"},
            mcp_tools=[
                {"name": "flood_forecast_model", "description": "洪水预报模型"},
                {"name": "dispatch_optimizer", "description": "调度优化器"},
                {"name": "gate_controller", "description": "闸门控制器"},
                {"name": "rainfall_sensor", "description": "雨量传感器"},
                {"name": "flow_meter", "description": "流量计"},
            ],
        )
        
        # 验证结果
        print(f"\n优化结果:")
        print(f"  - 策略: {result['strategy']}")
        print(f"  - 来源: {result['source']}")
        print(f"  - 可靠性评分: {result['reliability_score']:.2f}")
        print(f"  - 通过阈值: {result['passed']}")
        print(f"  - 备选链数量: {len(result['alternatives'])}")
        print(f"  - 迭代次数: {result['iterations']}")
        
        if result['alternatives']:
            print(f"\n  备选链详情:")
            for i, alt in enumerate(result['alternatives'], 1):
                print(f"    链{i}: {alt.chain_id}")
                print(f"      - 策略: {alt.strategy}")
                print(f"      - 可靠性: {alt.reliability_score:.2f}")
                print(f"      - 节点数: {len(alt.nodes)}")
        
        if result['issues']:
            print(f"\n  问题列表:")
            for issue in result['issues'][:5]:
                print(f"    * {issue}")
        
        print("\n✓ Plan策略测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ Plan策略测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_spec_strategy():
    """测试Spec策略"""
    print("\n" + "=" * 70)
    print(" " * 25 + "Spec策略测试")
    print("=" * 70)
    
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("\n❌ KIMI_API_KEY 环境变量未设置")
        return False
    
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    try:
        # 创建优化器
        optimizer = UnifiedOptimizer(strategy="spec", api_key=api_key)
        print(f"✓ 优化器初始化成功")
        print(f"  策略信息: {optimizer.get_strategy_info()}")
        
        # 创建示例任务
        tasks = create_sample_tasks()
        print(f"\n✓ 创建{len(tasks)}个示例任务")
        
        # 执行优化
        print("\n执行优化（使用LLM，3次迭代）...")
        print("这可能需要一些时间...")
        result = optimizer.optimize(
            task_nodes=tasks,
            user_input="洪水调度决策，要求24小时预见期，调度方案需通过安全审核",
            business_type="flood_dispatch",
            execution_type="chain",
            entities={
                "reservoir": "三峡",
                "basin": "长江流域",
                "forecast_hours": 24,
                "safety_check": True,
            },
            mcp_tools=[
                {"name": "flood_forecast_model", "description": "洪水预报模型，支持24小时预见期"},
                {"name": "dispatch_optimizer", "description": "多目标调度优化器"},
                {"name": "gate_controller", "description": "闸门控制器，支持远程控制"},
                {"name": "rainfall_sensor", "description": "雨量传感器网络"},
                {"name": "flow_meter", "description": "流量计，实时监测"},
                {"name": "reservoir_monitor", "description": "水库状态监测"},
            ],
        )
        
        # 验证结果
        print(f"\n优化结果:")
        print(f"  - 策略: {result['strategy']}")
        print(f"  - 来源: {result['source']}")
        print(f"  - 可靠性评分: {result['reliability_score']:.2f}")
        print(f"  - 通过阈值: {result['passed']}")
        print(f"  - 备选链数量: {len(result['alternatives'])}")
        print(f"  - 迭代次数: {result['iterations']}")
        
        if result['alternatives']:
            print(f"\n  备选链详情:")
            for i, alt in enumerate(result['alternatives'], 1):
                print(f"    链{i}: {alt.chain_id}")
                print(f"      - 策略: {alt.strategy}")
                print(f"      - 可靠性: {alt.reliability_score:.2f}")
                print(f"      - 节点数: {len(alt.nodes)}")
                if alt.optimization_info:
                    print(f"      - 优化信息: {alt.optimization_info}")
        
        if result['issues']:
            print(f"\n  问题列表:")
            for issue in result['issues'][:5]:
                print(f"    * {issue}")
        
        print("\n✓ Spec策略测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ Spec策略测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 70)
    print(" " * 20 + "向后兼容性测试")
    print("=" * 70)
    
    try:
        # 测试旧的导入方式
        from flood_decision_agent.agents.decision_chain.unified_optimizer import (
            SimpleOptimizer,
            PlanOptimizer,
            UnifiedOptimizer,
        )
        
        print("\n✓ 导入成功")
        print("  - SimpleOptimizer")
        print("  - PlanOptimizer")
        print("  - UnifiedOptimizer")
        
        # 测试SimpleOptimizer
        simple_opt = SimpleOptimizer(strategy="simple")
        print(f"\n✓ SimpleOptimizer创建成功")
        print(f"  策略: {simple_opt.strategy_name}")
        
        # 测试PlanOptimizer
        plan_opt = PlanOptimizer(strategy="plan")
        print(f"\n✓ PlanOptimizer创建成功")
        print(f"  策略: {plan_opt.strategy_name}")
        
        print("\n✓ 向后兼容性测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 向后兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "统一优化器测试套件" + " " * 33 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # 检查API Key
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("\n" + "=" * 70)
        print(" " * 20 + "API Key 未配置")
        print("=" * 70)
        print("\n请设置环境变量 KIMI_API_KEY 后重新运行测试")
        print("\n设置方法:")
        print("  Windows PowerShell:")
        print("    $env:KIMI_API_KEY=\"your-api-key\"")
        return False
    
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    # 运行测试
    results = {}
    
    # 1. 向后兼容性测试
    results["backward_compatibility"] = test_backward_compatibility()
    
    # 2. Simple策略测试
    results["simple_strategy"] = test_simple_strategy()
    
    # 3. Plan策略测试
    results["plan_strategy"] = test_plan_strategy()
    
    # 4. Spec策略测试
    results["spec_strategy"] = test_spec_strategy()
    
    # 打印总结
    print("\n" + "=" * 70)
    print(" " * 25 + "测试总结")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status}: {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n  ✓ 所有测试通过！")
    else:
        print("\n  ✗ 部分测试未通过")
    
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
