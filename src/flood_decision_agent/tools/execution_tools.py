"""执行工具模块 - 为每种执行类型提供工具实现.

提供以下工具：
- data_collection: 数据采集
- data_processing: 数据处理
- prediction: 预测预报
- calculation: 计算分析
- simulation: 模拟仿真
- optimization: 优化计算
- decision: 决策生成
- execution: 执行操作
- verification: 验证检查
- reporting: 报告生成
- universal_query: 通用查询（使用LLM直接回答）
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from openai import OpenAI

from flood_decision_agent.infra.kimi_guard import require_kimi_api_key
from flood_decision_agent.tools.registry import ToolMetadata, ToolRegistry


def register_execution_tools(registry: ToolRegistry) -> None:
    """注册所有执行工具到注册表.

    Args:
        registry: 工具注册表
    """
    # 数据采集工具
    registry.register(
        name="data_collection",
        handler=_data_collection_handler,
        metadata=ToolMetadata(
            name="data_collection",
            description="采集实时水情、雨情、气象等数据",
            task_types={"data_collection"},
        ),
    )
    
    # 数据处理工具
    registry.register(
        name="data_processing",
        handler=_data_processing_handler,
        metadata=ToolMetadata(
            name="data_processing",
            description="处理和分析原始数据",
            task_types={"data_processing"},
        ),
    )
    
    # 预测预报工具
    registry.register(
        name="prediction",
        handler=_prediction_handler,
        metadata=ToolMetadata(
            name="prediction",
            description="进行洪水、降雨、流量等预测预报",
            task_types={"prediction"},
        ),
    )
    
    # 计算分析工具
    registry.register(
        name="calculation",
        handler=_calculation_handler,
        metadata=ToolMetadata(
            name="calculation",
            description="进行水文水力计算分析",
            task_types={"calculation"},
        ),
    )
    
    # 模拟仿真工具
    registry.register(
        name="simulation",
        handler=_simulation_handler,
        metadata=ToolMetadata(
            name="simulation",
            description="进行洪水演进、调度方案等模拟仿真",
            task_types={"simulation"},
        ),
    )
    
    # 优化计算工具
    registry.register(
        name="optimization",
        handler=_optimization_handler,
        metadata=ToolMetadata(
            name="optimization",
            description="进行水库调度优化计算",
            task_types={"optimization"},
        ),
    )
    
    # 决策生成工具
    registry.register(
        name="decision",
        handler=_decision_handler,
        metadata=ToolMetadata(
            name="decision",
            description="生成调度决策方案",
            task_types={"decision"},
        ),
    )
    
    # 执行操作工具
    registry.register(
        name="execution",
        handler=_execution_handler,
        metadata=ToolMetadata(
            name="execution",
            description="执行具体的调度操作",
            task_types={"execution"},
        ),
    )
    
    # 验证检查工具
    registry.register(
        name="verification",
        handler=_verification_handler,
        metadata=ToolMetadata(
            name="verification",
            description="验证方案的可行性和安全性",
            task_types={"verification"},
        ),
    )
    
    # 报告生成工具
    registry.register(
        name="reporting",
        handler=_reporting_handler,
        metadata=ToolMetadata(
            name="reporting",
            description="生成分析报告和决策建议",
            task_types={"reporting"},
        ),
    )

    # 通用查询工具
    registry.register(
        name="universal_query",
        handler=_universal_query_handler,
        metadata=ToolMetadata(
            name="universal_query",
            description="使用LLM直接回答通用问题，支持流式输出",
            task_types={"universal_query"},
        ),
    )


# ========== 工具处理器实现 ==========

def _data_collection_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """数据采集工具处理器."""
    # 模拟数据采集
    station = config.get("station", "未知站点")
    data_type = config.get("data_type", "水位")

    # 生成模拟数据
    if data_type == "水位":
        value = round(random.uniform(140.0, 160.0), 2)
        unit = "米"
    elif data_type == "流量":
        value = round(random.uniform(1000.0, 50000.0), 0)
        unit = "立方米每秒"
    elif data_type == "降雨":
        value = round(random.uniform(0.0, 100.0), 1)
        unit = "毫米"
    else:
        value = random.randint(1, 100)
        unit = ""

    return {
        "station": station,
        "data_type": data_type,
        "value": value,
        "unit": unit,
        "timestamp": "2024-07-15 08:00:00",
        "status": "正常",
    }


def _data_processing_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """数据处理工具处理器."""
    # 模拟数据处理
    process_type = config.get("process_type", "统计分析")

    # 生成处理结果
    if process_type == "统计分析":
        result = {
            "mean": round(random.uniform(145.0, 155.0), 2),
            "max": round(random.uniform(155.0, 165.0), 2),
            "min": round(random.uniform(135.0, 145.0), 2),
            "count": random.randint(10, 100),
        }
    elif process_type == "趋势分析":
        trends = ["上升", "下降", "平稳"]
        result = {"trend": random.choice(trends), "confidence": round(random.uniform(0.7, 0.95), 2)}
    else:
        result = {"processed": True, "records": random.randint(10, 100)}

    return {
        "process_type": process_type,
        "result": result,
        "status": "完成",
    }


def _prediction_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """预测预报工具处理器."""
    # 模拟预测
    forecast_type = config.get("forecast_type", "水位预报")
    horizon = config.get("horizon", "24小时")

    # 生成预测结果
    predictions = []
    for i in range(6):  # 6个时间点
        if forecast_type == "水位预报":
            value = round(145.0 + random.uniform(-2.0, 5.0), 2)
            unit = "米"
        elif forecast_type == "流量预报":
            value = round(10000.0 + random.uniform(-2000.0, 10000.0), 0)
            unit = "立方米每秒"
        else:
            value = random.randint(1, 100)
            unit = ""

        predictions.append({
            "time": f"+{(i+1)*4}小时",
            "value": value,
            "unit": unit,
        })

    return {
        "forecast_type": forecast_type,
        "horizon": horizon,
        "predictions": predictions,
        "confidence": round(random.uniform(0.75, 0.95), 2),
        "status": "完成",
    }


def _calculation_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """计算分析工具处理器."""
    # 模拟计算
    calc_type = config.get("calc_type", "洪水频率分析")

    # 生成计算结果
    if calc_type == "洪水频率分析":
        result = {
            "p_50": round(random.uniform(140.0, 145.0), 2),
            "p_20": round(random.uniform(145.0, 150.0), 2),
            "p_10": round(random.uniform(150.0, 155.0), 2),
            "p_5": round(random.uniform(155.0, 160.0), 2),
            "p_1": round(random.uniform(160.0, 170.0), 2),
        }
    elif calc_type == "调洪演算":
        result = {
            "max_inflow": round(random.uniform(20000.0, 50000.0), 0),
            "max_outflow": round(random.uniform(15000.0, 40000.0), 0),
            "max_level": round(random.uniform(165.0, 175.0), 2),
            "flood_volume": round(random.uniform(1.0, 10.0), 2),
        }
    else:
        result = {"calculated": True, "value": random.randint(1, 1000)}

    return {
        "calc_type": calc_type,
        "result": result,
        "status": "完成",
    }


def _simulation_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """模拟仿真工具处理器."""
    # 模拟仿真
    sim_type = config.get("sim_type", "洪水演进")

    # 生成仿真结果
    if sim_type == "洪水演进":
        result = {
            "peak_time": f"+{random.randint(12, 48)}小时",
            "peak_flow": round(random.uniform(30000.0, 60000.0), 0),
            "affected_area": random.randint(100, 1000),
            "evacuation_needed": random.choice([True, False]),
        }
    elif sim_type == "调度方案仿真":
        result = {
            "scenarios_analyzed": random.randint(3, 10),
            "optimal_scenario": f"方案{random.randint(1, 5)}",
            "benefit_score": round(random.uniform(0.7, 0.95), 2),
        }
    else:
        result = {"simulated": True, "iterations": random.randint(100, 1000)}

    return {
        "sim_type": sim_type,
        "result": result,
        "status": "完成",
    }


def _optimization_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """优化计算工具处理器."""
    # 模拟优化
    opt_type = config.get("opt_type", "水库群联合优化")

    # 生成优化结果
    result = {
        "optimal_outflows": {
            "三峡": round(random.uniform(15000.0, 25000.0), 0),
            "葛洲坝": round(random.uniform(10000.0, 20000.0), 0),
            "丹江口": round(random.uniform(8000.0, 15000.0), 0),
        },
        "target_levels": {
            "三峡": round(random.uniform(145.0, 175.0), 2),
            "葛洲坝": round(random.uniform(62.0, 66.0), 2),
            "丹江口": round(random.uniform(155.0, 170.0), 2),
        },
        "benefit": {
            "flood_control": round(random.uniform(0.8, 0.95), 2),
            "power_generation": round(random.uniform(0.7, 0.9), 2),
            "navigation": round(random.uniform(0.8, 0.95), 2),
        },
    }

    return {
        "opt_type": opt_type,
        "result": result,
        "convergence": True,
        "iterations": random.randint(50, 200),
        "status": "完成",
    }


def _decision_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """决策生成工具处理器."""
    # 模拟决策生成
    decision_type = config.get("decision_type", "调度决策")

    # 生成决策建议
    if decision_type == "调度决策":
        result = {
            "decision": random.choice(["加大出库", "维持现状", "减小出库", "开闸泄洪"]),
            "target_outflow": round(random.uniform(10000.0, 30000.0), 0),
            "reason": "基于当前水情和预报结果，为平衡防洪安全和发电效益",
            "urgency": random.choice(["高", "中", "低"]),
        }
    elif decision_type == "预警决策":
        levels = ["蓝色", "黄色", "橙色", "红色"]
        result = {
            "warning_level": random.choice(levels),
            "trigger_condition": "水位达到警戒水位",
            "response_measures": ["加强监测", "通知下游", "准备应急"],
        }
    else:
        result = {"decision": "继续监测", "confidence": round(random.uniform(0.7, 0.9), 2)}

    return {
        "decision_type": decision_type,
        "result": result,
        "status": "完成",
    }


def _execution_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """执行操作工具处理器."""
    # 模拟执行
    action = config.get("action", "调整出库流量")

    # 生成执行结果
    result = {
        "action": action,
        "target": config.get("target", "三峡大坝"),
        "value": config.get("value", round(random.uniform(15000.0, 25000.0), 0)),
        "unit": "立方米每秒",
        "executed": True,
        "execution_time": "2024-07-15 08:30:00",
        "operator": "系统自动",
    }

    return {
        "action": action,
        "result": result,
        "status": "执行成功",
    }


def _verification_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """验证检查工具处理器."""
    # 模拟验证
    check_type = config.get("check_type", "方案可行性检查")

    # 生成验证结果
    checks = [
        {"item": "防洪安全", "passed": random.choice([True, True, True, False]), "score": round(random.uniform(0.8, 1.0), 2)},
        {"item": "发电效益", "passed": random.choice([True, True, True]), "score": round(random.uniform(0.7, 0.95), 2)},
        {"item": "航运保障", "passed": random.choice([True, True, True, True, False]), "score": round(random.uniform(0.8, 0.95), 2)},
        {"item": "生态影响", "passed": random.choice([True, True, True]), "score": round(random.uniform(0.75, 0.9), 2)},
    ]

    all_passed = all(c["passed"] for c in checks)

    return {
        "check_type": check_type,
        "checks": checks,
        "all_passed": all_passed,
        "overall_score": round(sum(c["score"] for c in checks) / len(checks), 2),
        "status": "通过" if all_passed else "需调整",
    }


def _reporting_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """报告生成工具处理器."""
    # 模拟报告生成
    report_type = config.get("report_type", "调度分析报告")

    # 生成报告
    report = {
        "title": report_type,
        "summary": "本次调度方案综合考虑了防洪、发电、航运等多方面因素，总体效果良好。",
        "key_findings": [
            f"水位控制在安全范围内",
            f"出库流量满足下游防洪要求",
            f"发电效益达到预期的{round(random.uniform(85, 98), 0)}%",
        ],
        "recommendations": [
            "继续加强水情监测",
            "根据预报及时调整调度方案",
            "做好应急准备工作",
        ],
        "generated_at": "2024-07-15 09:00:00",
    }

    return {
        "report_type": report_type,
        "report": report,
        "status": "完成",
    }


def _universal_query_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """通用查询工具处理器 - 使用LLM直接回答用户问题.

    这是一个通用工具，可以处理任何类型的问题，不局限于水利调度领域。
    使用流式输出实时显示AI的回答。

    Args:
        data_pool: 数据池
        config: 配置参数，包含用户问题

    Returns:
        包含LLM回答的字典
    """
    # 获取用户问题
    question = config.get("question", "")
    if not question:
        # 尝试从数据池获取原始输入
        question = data_pool.get("raw_user_input", "请回答一个通用问题")

    # 获取任务上下文
    task_context = config.get("task_context", {})
    task_type = task_context.get("task_type", "general")

    # 初始化LLM客户端
    try:
        api_key = require_kimi_api_key()
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )
    except Exception as e:
        return {
            "answer": f"无法初始化LLM客户端: {str(e)}",
            "status": "失败",
            "source": "error",
        }

    # 构建系统提示词
    system_prompt = """你是"水利智脑"——一个专业的水利调度领域AI助手，同时也具备广泛的通用知识。

【你的能力】
1. 水利调度专业知识：洪水预警、水库调度、干旱调度、风险评估等
2. 通用知识：回答用户提出的各类问题

【回答原则】
- 如果问题与水利相关，提供专业、准确的回答
- 如果问题与水利无关，用通用知识礼貌回答
- 语言简洁清晰，结构分明
- 不确定的信息要说明"据我所知"或"建议进一步核实"

【输出格式】
直接给出回答，不需要额外的格式标记。"""

    # 流式输出标题
    print(f"\n{'='*70}")
    print(f"[AI 正在回答问题]")
    print(f"{'='*70}\n")
    print(f"问题: {question}\n")
    print("-" * 70)
    print("回答:\n")

    try:
        # 调用LLM，启用流式输出
        response_stream = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            temperature=0.3,
            max_tokens=1500,
            stream=True,
        )

        # 收集流式输出
        full_answer = []
        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                part = chunk.choices[0].delta.content
                full_answer.append(part)
                print(part, end="", flush=True)

        print("\n")  # 最后换行

        answer = "".join(full_answer)

        return {
            "answer": answer,
            "question": question,
            "source": "llm_direct",
            "status": "完成",
            "task_type": task_type,
        }

    except Exception as e:
        error_msg = f"LLM调用失败: {str(e)}"
        print(f"\n[错误] {error_msg}")
        return {
            "answer": error_msg,
            "status": "失败",
            "source": "error",
        }
