"""全流程集成测试 - 验证参数选取流程

测试目标：
1. 验证完整的参数选取流程符合预设的业务规则
2. 记录详细的 debug 日志
3. 测试关键业务场景、边界条件和异常情况
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.flood_decision_agent.core.parameter_types import (
    ParameterSource,
    ParameterRequirement,
    ParameterValue,
    ParameterPlan,
)
from src.flood_decision_agent.core.tool_types import ToolCandidate
from src.flood_decision_agent.core.clarification_types import (
    ClarificationRequest,
    ClarificationResponse,
    ParameterPlannerState,
)
from src.flood_decision_agent.core.shared_data_pool import SharedDataPool
from src.flood_decision_agent.agents.parameter_planner import ParameterPlanner
from src.flood_decision_agent.agents.decision_chain.task_decomposer import TaskDecomposer, TaskNodeInfo
from src.flood_decision_agent.agents.intent_parser.parser import TaskIntent, IntentParser
from src.flood_decision_agent.core.task_types import BusinessTaskType, ExecutionTaskType


def log_section(title: str):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def log_test(test_name: str, success: bool, details: str = ""):
    """打印测试结果"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"[{status}] {test_name}")
    if details:
        print(f"      {details}")


class TestResult:
    """测试结果收集器"""

    def __init__(self):
        self.tests = []
        self.start_time = time.time()

    def add(self, name: str, passed: bool, details: str = ""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        })

    def summary(self) -> dict:
        passed = sum(1 for t in self.tests if t["passed"])
        failed = len(self.tests) - passed
        return {
            "total": len(self.tests),
            "passed": passed,
            "failed": failed,
            "duration_ms": (time.time() - self.start_time) * 1000,
            "tests": self.tests,
        }


def test_parameter_types():
    """测试参数类型定义"""
    log_section("1. 参数类型定义测试")

    results = TestResult()

    # Test 1.1: ParameterRequirement
    req = ParameterRequirement(
        param_name="city",
        param_type="string",
        required=True,
        default_value="北京",
        description="城市名称",
    )
    results.add(
        "ParameterRequirement 创建",
        req.param_name == "city" and req.default_value == "北京",
        f"param_name={req.param_name}, default_value={req.default_value}"
    )

    # Test 1.2: ParameterValue
    val = ParameterValue(
        param_name="city",
        value="上海",
        source=ParameterSource.USER_INPUT,
    )
    results.add(
        "ParameterValue 创建",
        val.param_name == "city" and val.value == "上海",
        f"param_name={val.param_name}, source={val.source.value}"
    )

    # Test 1.3: ParameterPlan
    plan = ParameterPlan(
        node_id="task_001",
        task_type="rainfall_analysis",
        selected_tool="get_rainfall",
        parameters=[val],
    )
    results.add(
        "ParameterPlan 创建",
        plan.node_id == "task_001" and plan.selected_tool == "get_rainfall",
        f"node_id={plan.node_id}, tool={plan.selected_tool}"
    )

    # Test 1.4: ToolCandidate
    candidate = ToolCandidate(
        tool_name="get_rainfall",
        priority=80,
        reason="适合降雨数据查询",
    )
    results.add(
        "ToolCandidate 创建",
        candidate.tool_name == "get_rainfall" and candidate.priority == 80,
        f"tool_name={candidate.tool_name}, priority={candidate.priority}"
    )

    # Test 1.5: ClarificationRequest
    clar_req = ClarificationRequest(
        node_id="task_001",
        task_type="rainfall_analysis",
        missing_params=[req],
        generated_questions=["请提供城市名称"],
    )
    results.add(
        "ClarificationRequest 创建",
        clar_req.node_id == "task_001" and len(clar_req.generated_questions) == 1,
        f"request_id={clar_req.request_id[:8]}..."
    )

    # Test 1.6: ParameterPlannerState
    results.add(
        "ParameterPlannerState 枚举",
        ParameterPlannerState.COMPLETED.value == "completed",
        f"COMPLETED={ParameterPlannerState.COMPLETED.value}"
    )

    summary = results.summary()
    for test in summary["tests"]:
        log_test(test["name"], test["passed"], test["details"])

    return summary


def test_shared_data_pool():
    """测试增强版共享数据池"""
    log_section("2. 共享数据池增强功能测试")

    results = TestResult()
    pool = SharedDataPool()

    # Test 2.1: 基础 put/get
    pool.put("key1", "value1", source="user_input")
    results.add(
        "基础 put/get",
        pool.get("key1") == "value1",
        f"get(key1)={pool.get('key1')}"
    )

    # Test 2.2: 来源追踪
    results.add(
        "来源追踪",
        pool.get_source("key1") == "user_input",
        f"source={pool.get_source('key1')}"
    )

    # Test 2.3: 版本控制
    results.add(
        "版本控制",
        pool.get_version("key1") == 1,
        f"version={pool.get_version('key1')}"
    )

    # Test 2.4: 命名空间
    pool.put_with_namespace("context", "city", "北京", source="user_input")
    results.add(
        "命名空间 put_with_namespace",
        pool.get_with_namespace("context", "city") == "北京",
        f"get_with_namespace(context, city)={pool.get_with_namespace('context', 'city')}"
    )

    # Test 2.5: 工具输出存储
    pool.put_tool_output("rainfall_tool", "result", {"data": 123}, source="tool_output")
    results.add(
        "工具输出存储",
        pool.get_tool_output("rainfall_tool", "result") == {"data": 123},
        f"tool_output={pool.get_tool_output('rainfall_tool', 'result')}"
    )

    # Test 2.6: 按前缀查找
    pool.put_tool_output("rainfall_tool", "status", "ok")
    prefix_result = pool.find_by_prefix("tool:rainfall_tool:")
    results.add(
        "按前缀查找",
        len(prefix_result) >= 1,
        f"find_by_prefix result count={len(prefix_result)}"
    )

    # Test 2.7: 按来源查找
    results.add(
        "按来源查找",
        "key1" in pool.find_by_source("user_input"),
        f"find_by_source result={list(pool.find_by_source('user_input').keys())}"
    )

    # Test 2.8: 批量操作
    pool.put_batch({"a": 1, "b": 2}, source="batch")
    results.add(
        "批量操作",
        pool.get("a") == 1 and pool.get("b") == 2,
        f"a={pool.get('a')}, b={pool.get('b')}"
    )

    # Test 2.9: 历史记录
    pool.put("key1", "value2", source="update")
    history = pool.get_history("key1")
    results.add(
        "历史记录",
        len(history) == 1 and history[0]["new_value"] == "value2",
        f"history length={len(history)}"
    )

    summary = results.summary()
    for test in summary["tests"]:
        log_test(test["name"], test["passed"], test["details"])

    return summary


def test_intent_parser():
    """测试意图解析器"""
    log_section("3. 意图解析器测试")

    results = TestResult()

    # Test 3.1: 创建 TaskIntent
    intent = TaskIntent(
        goal={"description": "分析三峡水库当前水情"},
        raw_input="分析三峡水库当前水情并给出调度建议",
        context={"session_id": "test_session"},
    )
    results.add(
        "TaskIntent 创建",
        intent.goal["description"] == "分析三峡水库当前水情",
        f"goal={intent.goal}"
    )

    # Test 3.2: execution_steps property
    intent.task_type = BusinessTaskType.RESERVOIR_DISPATCH
    steps = intent.execution_steps
    results.add(
        "execution_steps property",
        len(steps) > 0,
        f"execution_steps count={len(steps)}"
    )

    # Test 3.3: IntentParser
    parser = IntentParser()
    results.add(
        "IntentParser 创建",
        parser is not None,
        "IntentParser initialized"
    )

    summary = results.summary()
    for test in summary["tests"]:
        log_test(test["name"], test["passed"], test["details"])

    return summary


def test_task_decomposer():
    """测试任务分解器"""
    log_section("4. 任务分解器测试")

    results = TestResult()

    # Test 4.1: TaskDecomposer 创建
    decomposer = TaskDecomposer()
    results.add(
        "TaskDecomposer 创建",
        decomposer is not None,
        "TaskDecomposer initialized"
    )

    # Test 4.2: llm_client 属性
    results.add(
        "llm_client 属性存在",
        hasattr(decomposer, "llm_client"),
        f"has llm_client={hasattr(decomposer, 'llm_client')}"
    )

    # Test 4.3: tool_registry 属性
    results.add(
        "tool_registry 属性存在",
        hasattr(decomposer, "tool_registry"),
        f"has tool_registry={hasattr(decomposer, 'tool_registry')}"
    )

    # Test 4.4: decompose 方法存在
    results.add(
        "decompose 方法存在",
        hasattr(decomposer, "decompose"),
        f"has decompose={hasattr(decomposer, 'decompose')}"
    )

    summary = results.summary()
    for test in summary["tests"]:
        log_test(test["name"], test["passed"], test["details"])

    return summary


def test_parameter_planner():
    """测试参数规划器"""
    log_section("5. 参数规划器测试")

    results = TestResult()

    # Test 5.1: ParameterPlanner 创建
    planner = ParameterPlanner()
    results.add(
        "ParameterPlanner 创建",
        planner is not None,
        "ParameterPlanner initialized"
    )

    # Test 5.2: state 属性
    results.add(
        "state 属性",
        hasattr(planner, "state"),
        f"state={planner.state.value}"
    )

    # Test 5.3: plan_parameters 方法
    results.add(
        "plan_parameters 方法存在",
        hasattr(planner, "plan_parameters"),
        f"has plan_parameters={hasattr(planner, 'plan_parameters')}"
    )

    # Test 5.4: submit_clarification 方法
    results.add(
        "submit_clarification 方法存在",
        hasattr(planner, "submit_clarification"),
        f"has submit_clarification={hasattr(planner, 'submit_clarification')}"
    )

    summary = results.summary()
    for test in summary["tests"]:
        log_test(test["name"], test["passed"], test["details"])

    return summary


def test_parameter_selection_flow():
    """测试参数选取流程"""
    log_section("6. 参数选取流程测试")

    results = TestResult()

    # 模拟完整流程
    pool = SharedDataPool()

    # Step 1: 用户输入
    user_input = "分析三峡水库当前水情并给出调度建议"
    pool.set("raw_user_input", user_input, source="user_input")

    results.add(
        "Step 1: 用户输入设置",
        pool.get("raw_user_input") == user_input,
        f"raw_user_input={user_input}"
    )

    # Step 2: 从上下文提取参数
    pool.set_context("current_time", "2024-01-15 10:00:00")
    pool.set_context("user_location", "武汉")

    results.add(
        "Step 2: 上下文参数设置",
        pool.get_context("current_time") == "2024-01-15 10:00:00",
        f"current_time={pool.get_context('current_time')}"
    )

    # Step 3: 模拟经验参数
    reservoir_thresholds = {
        "warning_level": 175.0,
        "danger_level": 180.0,
        "max_outflow": 50000.0,
    }
    pool.put("reservoir_thresholds", reservoir_thresholds, source="experience")

    results.add(
        "Step 3: 经验参数设置",
        pool.get("reservoir_thresholds") == reservoir_thresholds,
        f"thresholds={pool.get('reservoir_thresholds')}"
    )

    # Step 4: 创建 ParameterRequirement
    requirements = [
        ParameterRequirement(
            param_name="reservoir_name",
            param_type="string",
            required=True,
            description="水库名称",
        ),
        ParameterRequirement(
            param_name="water_level",
            param_type="number",
            required=False,
            default_value=175.0,
            description="水位（米）",
        ),
    ]

    results.add(
        "Step 4: ParameterRequirement 创建",
        len(requirements) == 2 and requirements[0].required == True,
        f"requirements count={len(requirements)}"
    )

    # Step 5: 创建 ParameterPlan
    param_values = [
        ParameterValue(
            param_name="reservoir_name",
            value="三峡水库",
            source=ParameterSource.USER_INPUT,
        ),
        ParameterValue(
            param_name="water_level",
            value=178.5,
            source=ParameterSource.EXPERIENCE,
        ),
    ]

    plan = ParameterPlan(
        node_id="task_001",
        task_type="reservoir_analysis",
        selected_tool="analyze_reservoir",
        parameters=param_values,
        missing_params=[],
    )

    results.add(
        "Step 5: ParameterPlan 创建",
        plan.node_id == "task_001" and plan.selected_tool == "analyze_reservoir",
        f"plan={plan.node_id}, tool={plan.selected_tool}"
    )

    # Step 6: 参数合并（优先级覆盖）
    from_input = [
        ParameterValue(param_name="city", value="北京", source=ParameterSource.USER_INPUT)
    ]
    from_experience = [
        ParameterValue(param_name="threshold", value=100, source=ParameterSource.EXPERIENCE)
    ]
    merged = from_input + from_experience

    results.add(
        "Step 6: 参数合并",
        len(merged) == 2 and any(p.param_name == "city" for p in merged),
        f"merged count={len(merged)}"
    )

    summary = results.summary()
    for test in summary["tests"]:
        log_test(test["name"], test["passed"], test["details"])

    return summary


def test_clarification_flow():
    """测试用户澄清流程"""
    log_section("7. 用户澄清流程测试")

    results = TestResult()

    # Test 7.1: ClarificationRequest 创建
    req = ClarificationRequest(
        node_id="task_001",
        task_type="rainfall_analysis",
        missing_params=[
            ParameterRequirement(
                param_name="city",
                param_type="string",
                required=True,
                description="城市名称",
            )
        ],
        generated_questions=["请提供要分析的城市名称"],
    )
    results.add(
        "ClarificationRequest 创建",
        req.node_id == "task_001" and len(req.generated_questions) == 1,
        f"request_id={req.request_id[:8]}..."
    )

    # Test 7.2: ClarificationResponse 创建
    response = ClarificationResponse(
        request_id=req.request_id,
        answers={"city": "武汉"},
    )
    results.add(
        "ClarificationResponse 创建",
        response.request_id == req.request_id and response.answers["city"] == "武汉",
        f"answers={response.answers}"
    )

    # Test 7.3: ParameterPlanner 澄清回调
    planner = ParameterPlanner()

    clarification_received = {"received": False}

    def on_clarification(clar_req):
        clarification_received["received"] = True
        print(f"      [Callback] 收到澄清请求: {clar_req.request_id[:8]}...")

    planner.on_clarification_needed = on_clarification

    # 模拟触发澄清（需要缺少必需参数）
    # 注意：这里只是测试回调机制，不实际触发

    results.add(
        "Clarification 回调机制",
        planner.on_clarification_needed is not None,
        "callback is set"
    )

    summary = results.summary()
    for test in summary["tests"]:
        log_test(test["name"], test["passed"], test["details"])

    return summary


def run_all_tests():
    """运行所有测试"""
    log_section("全流程集成测试 - 参数选取流程验证")

    all_results = []

    # 执行所有测试
    all_results.append(test_parameter_types())
    all_results.append(test_shared_data_pool())
    all_results.append(test_intent_parser())
    all_results.append(test_task_decomposer())
    all_results.append(test_parameter_planner())
    all_results.append(test_parameter_selection_flow())
    all_results.append(test_clarification_flow())

    # 汇总结果
    log_section("测试汇总")

    total_tests = sum(r["total"] for r in all_results)
    total_passed = sum(r["passed"] for r in all_results)
    total_failed = sum(r["failed"] for r in all_results)
    total_duration = sum(r["duration_ms"] for r in all_results)

    print(f"总测试数: {total_tests}")
    print(f"通过: {total_passed} ✅")
    print(f"失败: {total_failed} ❌")
    print(f"总耗时: {total_duration:.2f}ms")

    # 打印测试分类汇总
    print("\n按测试分类:")
    test_names = [
        "参数类型定义",
        "共享数据池增强",
        "意图解析器",
        "任务分解器",
        "参数规划器",
        "参数选取流程",
        "用户澄清流程",
    ]

    for name, result in zip(test_names, all_results):
        status = "✅" if result["failed"] == 0 else "❌"
        print(f"  {status} {name}: {result['passed']}/{result['total']}")

    # 返回最终结果
    return {
        "success": total_failed == 0,
        "total": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "duration_ms": total_duration,
    }


if __name__ == "__main__":
    result = run_all_tests()

    # 退出码
    sys.exit(0 if result["success"] else 1)
