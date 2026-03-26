"""水利模型 MCP Server

提供水文水利相关模型计算服务：
- 降雨径流模型
- 洪水演进模型
- 水库调度模型
- 水质模型（预留）

注意：此服务为预留框架，具体模型实现需根据业务需求开发。
"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
import numpy as np


# ============== 数据模型定义 ==============

@dataclass
class RainfallData:
    """降雨数据"""
    timestamps: List[str]
    values: List[float]  # mm
    station_id: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RunoffResult:
    """径流计算结果"""
    timestamps: List[str]
    discharge: List[float]  # m³/s
    total_runoff: float  # m³
    peak_discharge: float  # m³/s
    model_name: str


@dataclass
class ReservoirState:
    """水库状态"""
    water_level: float  # m
    storage: float  # m³
    inflow: float  # m³/s
    outflow: float  # m³/s
    timestamp: str


@dataclass
class DispatchPlan:
    """调度方案"""
    plan_id: str
    target_level: float
    gate_openings: List[float]
    expected_outflow: List[float]
    time_steps: List[str]
    safety_check: bool


# ============== 模型接口定义 ==============

class HydrologicalModel(ABC):
    """水文模型基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """模型名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """模型描述"""
        pass
    
    @abstractmethod
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """运行模型"""
        pass


class MockRainfallRunoffModel(HydrologicalModel):
    """模拟降雨径流模型（用于测试）"""
    
    @property
    def name(self) -> str:
        return "MockRainfallRunoff"
    
    @property
    def description(self) -> str:
        return "基于经验公式的降雨径流模拟模型"
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """运行模型"""
        rainfall = inputs.get("rainfall", [])
        area = inputs.get("catchment_area", 100)  # km²
        
        # 简单的径流系数法
        runoff_coefficient = 0.7
        discharge = [r * area * runoff_coefficient / 3.6 for r in rainfall]  # 简化的转换
        
        return {
            "discharge": discharge,
            "total_runoff": sum(discharge) * 3600,  # 假设小时尺度
            "peak_discharge": max(discharge) if discharge else 0,
            "model": self.name
        }


class MockFloodRoutingModel(HydrologicalModel):
    """模拟洪水演进模型（用于测试）"""
    
    @property
    def name(self) -> str:
        return "MockFloodRouting"
    
    @property
    def description(self) -> str:
        return "基于马斯京根法的洪水演进模型"
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """运行模型"""
        inflow = inputs.get("inflow", [])
        k = inputs.get("k", 3.0)  # 蓄量常数
        x = inputs.get("x", 0.3)  # 权重系数
        
        # 简化的马斯京根法
        outflow = []
        c0 = (0.5 * 1 - k * x) / (0.5 * 1 + k * (1 - x))
        c1 = (0.5 * 1 + k * x) / (0.5 * 1 + k * (1 - x))
        c2 = (k * (1 - x) - 0.5 * 1) / (0.5 * 1 + k * (1 - x))
        
        outflow.append(inflow[0] if inflow else 0)
        for i in range(1, len(inflow)):
            q_out = c0 * inflow[i] + c1 * inflow[i-1] + c2 * outflow[i-1]
            outflow.append(max(0, q_out))
        
        return {
            "outflow": outflow,
            "peak_attenuation": max(inflow) - max(outflow) if inflow else 0,
            "time_shift": 0,  # 简化处理
            "model": self.name
        }


class MockReservoirDispatchModel(HydrologicalModel):
    """模拟水库调度模型（用于测试）"""
    
    @property
    def name(self) -> str:
        return "MockReservoirDispatch"
    
    @property
    def description(self) -> str:
        return "基于规则的水库调度模型"
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """运行模型"""
        inflow = inputs.get("inflow", [])
        initial_level = inputs.get("initial_level", 100.0)
        target_level = inputs.get("target_level", 95.0)
        max_outflow = inputs.get("max_outflow", 1000.0)
        
        # 简化的调度规则
        outflow = []
        current_level = initial_level
        
        for q_in in inflow:
            if current_level > target_level:
                # 需要泄洪
                q_out = min(max_outflow, (current_level - target_level) * 10)
            else:
                # 保持最小下泄
                q_out = max(0, q_in * 0.1)
            
            outflow.append(q_out)
            # 简化的水位变化
            current_level += (q_in - q_out) * 0.001
        
        return {
            "outflow": outflow,
            "final_level": current_level,
            "total_release": sum(outflow) * 3600,
            "model": self.name
        }


# ============== MCP Server 实现 ==============

# 创建 MCP Server
server = Server("flood-agent-hydrology")

# 模型注册表
MODEL_REGISTRY: Dict[str, HydrologicalModel] = {
    "rainfall_runoff": MockRainfallRunoffModel(),
    "flood_routing": MockFloodRoutingModel(),
    "reservoir_dispatch": MockReservoirDispatchModel(),
}


@server.list_tools()
async def list_tools() -> List[Tool]:
    """定义可用工具"""
    return [
        Tool(
            name="list_hydrology_models",
            description="列出所有可用的水利模型",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_model_info",
            description="获取模型详细信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "模型名称",
                        "enum": ["rainfall_runoff", "flood_routing", "reservoir_dispatch"]
                    }
                },
                "required": ["model_name"]
            }
        ),
        Tool(
            name="run_rainfall_runoff",
            description="运行降雨径流模型计算",
            inputSchema={
                "type": "object",
                "properties": {
                    "rainfall": {
                        "type": "array",
                        "description": "降雨序列 (mm)",
                        "items": {"type": "number"}
                    },
                    "timestamps": {
                        "type": "array",
                        "description": "时间戳序列",
                        "items": {"type": "string"}
                    },
                    "catchment_area": {
                        "type": "number",
                        "description": "流域面积 (km²)",
                        "default": 100
                    },
                    "station_id": {
                        "type": "string",
                        "description": "测站ID"
                    }
                },
                "required": ["rainfall"]
            }
        ),
        Tool(
            name="run_flood_routing",
            description="运行洪水演进模型",
            inputSchema={
                "type": "object",
                "properties": {
                    "inflow": {
                        "type": "array",
                        "description": "入流序列 (m³/s)",
                        "items": {"type": "number"}
                    },
                    "k": {
                        "type": "number",
                        "description": "蓄量常数",
                        "default": 3.0
                    },
                    "x": {
                        "type": "number",
                        "description": "权重系数",
                        "default": 0.3
                    },
                    "reach_length": {
                        "type": "number",
                        "description": "河段长度 (km)"
                    }
                },
                "required": ["inflow"]
            }
        ),
        Tool(
            name="run_reservoir_dispatch",
            description="运行水库调度模型",
            inputSchema={
                "type": "object",
                "properties": {
                    "inflow": {
                        "type": "array",
                        "description": "入库流量序列 (m³/s)",
                        "items": {"type": "number"}
                    },
                    "initial_level": {
                        "type": "number",
                        "description": "初始水位 (m)",
                        "default": 100.0
                    },
                    "target_level": {
                        "type": "number",
                        "description": "目标水位 (m)",
                        "default": 95.0
                    },
                    "max_outflow": {
                        "type": "number",
                        "description": "最大下泄流量 (m³/s)",
                        "default": 1000.0
                    },
                    "min_outflow": {
                        "type": "number",
                        "description": "最小下泄流量 (m³/s)",
                        "default": 10.0
                    }
                },
                "required": ["inflow"]
            }
        ),
        Tool(
            name="calculate_dispatch_plan",
            description="生成水库调度方案",
            inputSchema={
                "type": "object",
                "properties": {
                    "forecast_inflow": {
                        "type": "array",
                        "description": "预报入流序列",
                        "items": {"type": "number"}
                    },
                    "current_state": {
                        "type": "object",
                        "description": "当前水库状态",
                        "properties": {
                            "water_level": {"type": "number"},
                            "storage": {"type": "number"}
                        }
                    },
                    "constraints": {
                        "type": "object",
                        "description": "调度约束条件",
                        "properties": {
                            "max_level": {"type": "number"},
                            "min_level": {"type": "number"},
                            "max_outflow": {"type": "number"}
                        }
                    }
                },
                "required": ["forecast_inflow", "current_state"]
            }
        ),
        Tool(
            name="validate_dispatch_safety",
            description="验证调度方案安全性",
            inputSchema={
                "type": "object",
                "properties": {
                    "dispatch_plan": {
                        "type": "object",
                        "description": "调度方案"
                    },
                    "safety_rules": {
                        "type": "array",
                        "description": "安全规则",
                        "items": {"type": "object"}
                    }
                },
                "required": ["dispatch_plan"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "list_hydrology_models":
            return await _handle_list_models()
        elif name == "get_model_info":
            return await _handle_get_model_info(arguments)
        elif name == "run_rainfall_runoff":
            return await _handle_run_rainfall_runoff(arguments)
        elif name == "run_flood_routing":
            return await _handle_run_flood_routing(arguments)
        elif name == "run_reservoir_dispatch":
            return await _handle_run_reservoir_dispatch(arguments)
        elif name == "calculate_dispatch_plan":
            return await _handle_calculate_dispatch_plan(arguments)
        elif name == "validate_dispatch_safety":
            return await _handle_validate_safety(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }, ensure_ascii=False)
        )]


async def _handle_list_models() -> List[TextContent]:
    """列出可用模型"""
    models = []
    for name, model in MODEL_REGISTRY.items():
        models.append({
            "name": name,
            "description": model.description,
            "status": "available"
        })
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "models": models,
            "total": len(models)
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_get_model_info(args: Dict[str, Any]) -> List[TextContent]:
    """获取模型信息"""
    model_name = args["model_name"]
    
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"未知模型: {model_name}")
    
    model = MODEL_REGISTRY[model_name]
    
    # 根据模型类型返回不同的参数说明
    params_info = {}
    if model_name == "rainfall_runoff":
        params_info = {
            "rainfall": "降雨序列 (mm)",
            "catchment_area": "流域面积 (km²)",
            "outputs": ["discharge", "total_runoff", "peak_discharge"]
        }
    elif model_name == "flood_routing":
        params_info = {
            "inflow": "入流序列 (m³/s)",
            "k": "蓄量常数",
            "x": "权重系数 (0-0.5)",
            "outputs": ["outflow", "peak_attenuation", "time_shift"]
        }
    elif model_name == "reservoir_dispatch":
        params_info = {
            "inflow": "入库流量 (m³/s)",
            "initial_level": "初始水位 (m)",
            "target_level": "目标水位 (m)",
            "outputs": ["outflow", "final_level", "total_release"]
        }
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "model": {
                "name": model.name,
                "description": model.description,
                "parameters": params_info
            }
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_run_rainfall_runoff(args: Dict[str, Any]) -> List[TextContent]:
    """运行降雨径流模型"""
    model = MODEL_REGISTRY["rainfall_runoff"]
    
    inputs = {
        "rainfall": args.get("rainfall", []),
        "catchment_area": args.get("catchment_area", 100),
        "timestamps": args.get("timestamps", []),
        "station_id": args.get("station_id", "unknown")
    }
    
    result = model.run(inputs)
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "model": result.pop("model"),
            "inputs": {
                "rainfall_count": len(inputs["rainfall"]),
                "catchment_area": inputs["catchment_area"]
            },
            "outputs": result,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_run_flood_routing(args: Dict[str, Any]) -> List[TextContent]:
    """运行洪水演进模型"""
    model = MODEL_REGISTRY["flood_routing"]
    
    inputs = {
        "inflow": args.get("inflow", []),
        "k": args.get("k", 3.0),
        "x": args.get("x", 0.3),
        "reach_length": args.get("reach_length", 10.0)
    }
    
    result = model.run(inputs)
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "model": result.pop("model"),
            "inputs": {
                "inflow_count": len(inputs["inflow"]),
                "k": inputs["k"],
                "x": inputs["x"]
            },
            "outputs": result,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_run_reservoir_dispatch(args: Dict[str, Any]) -> List[TextContent]:
    """运行水库调度模型"""
    model = MODEL_REGISTRY["reservoir_dispatch"]
    
    inputs = {
        "inflow": args.get("inflow", []),
        "initial_level": args.get("initial_level", 100.0),
        "target_level": args.get("target_level", 95.0),
        "max_outflow": args.get("max_outflow", 1000.0),
        "min_outflow": args.get("min_outflow", 10.0)
    }
    
    result = model.run(inputs)
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "model": result.pop("model"),
            "inputs": {
                "inflow_count": len(inputs["inflow"]),
                "initial_level": inputs["initial_level"],
                "target_level": inputs["target_level"]
            },
            "outputs": result,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_calculate_dispatch_plan(args: Dict[str, Any]) -> List[TextContent]:
    """生成调度方案"""
    forecast_inflow = args.get("forecast_inflow", [])
    current_state = args.get("current_state", {})
    constraints = args.get("constraints", {})
    
    # 简化的调度方案生成
    time_steps = len(forecast_inflow)
    plan_id = f"DSP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 运行调度模型
    model = MODEL_REGISTRY["reservoir_dispatch"]
    model_result = model.run({
        "inflow": forecast_inflow,
        "initial_level": current_state.get("water_level", 100.0),
        "target_level": constraints.get("target_level", 95.0),
        "max_outflow": constraints.get("max_outflow", 1000.0)
    })
    
    plan = {
        "plan_id": plan_id,
        "generated_at": datetime.now().isoformat(),
        "time_steps": time_steps,
        "outflow_schedule": model_result["outflow"],
        "expected_final_level": model_result["final_level"],
        "total_release": model_result["total_release"],
        "constraints_applied": list(constraints.keys())
    }
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "plan": plan,
            "model_used": "reservoir_dispatch"
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_validate_safety(args: Dict[str, Any]) -> List[TextContent]:
    """验证调度方案安全性"""
    dispatch_plan = args.get("dispatch_plan", {})
    safety_rules = args.get("safety_rules", [])
    
    # 简化的安全验证
    violations = []
    warnings = []
    
    outflow = dispatch_plan.get("outflow_schedule", [])
    
    # 检查最大下泄
    max_outflow = max(outflow) if outflow else 0
    if max_outflow > 5000:  # 假设安全阈值
        violations.append(f"最大下泄流量 {max_outflow:.2f} m³/s 超过安全阈值")
    elif max_outflow > 3000:
        warnings.append(f"最大下泄流量 {max_outflow:.2f} m³/s 接近安全阈值")
    
    # 检查水位变化率（简化）
    final_level = dispatch_plan.get("expected_final_level", 0)
    if final_level > 110:  # 假设最高水位限制
        violations.append(f"预测最高水位 {final_level:.2f}m 超过限制")
    
    is_safe = len(violations) == 0
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "is_safe": is_safe,
            "violations": violations,
            "warnings": warnings,
            "plan_id": dispatch_plan.get("plan_id", "unknown"),
            "validation_time": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


async def main():
    """启动 MCP Server"""
    from mcp.server.stdio import stdio_server as mcp_stdio_server
    
    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())