"""HiPIMS MCP Server

HiPIMS (High-Performance Integrated Hydrodynamic Modelling System) MCP 服务
提供 GPU 加速的 2D 水动力模拟能力：
- 2D 洪水演进模拟
- GPU 可用性检测
- 模拟数据准备
- 模拟状态监控
- 历史结果管理

注意：当前实现包含 HiPIMS 的模拟/包装层，用于测试框架。
实际生产环境可替换为真实的 HiPIMS Python 接口调用。
"""

import asyncio
import os
import platform
import sys
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from mcp.server import Server
from mcp.types import Tool, TextContent

from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps


# ============== 启动检查 ==============
def _check_api_key():
    """检查 KIMI_API_KEY 环境变量"""
    if not os.environ.get("KIMI_API_KEY"):
        print("需要kimi_api_key", file=sys.stderr)
        sys.exit(1)


# ============== 数据模型定义 ==============

class SimulationStatus(Enum):
    """模拟任务状态"""
    PENDING = "pending"
    PREPARING = "preparing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SimulationConfig:
    """模拟配置"""
    simulation_id: str
    terrain_path: str
    boundary_conditions: Dict[str, Any]
    rainfall_data: Optional[Dict[str, Any]] = None
    simulation_duration: float = 3600.0  # 秒
    time_step: float = 1.0  # 秒
    output_interval: float = 300.0  # 秒
    use_gpu: bool = True
    gpu_device: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SimulationResult:
    """模拟结果"""
    simulation_id: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    progress: float = 0.0
    
    # 结果数据
    inundation_extent: Optional[Dict[str, Any]] = None  # 淹没范围
    water_depth: Optional[Dict[str, Any]] = None  # 水深分布
    velocity_field: Optional[Dict[str, Any]] = None  # 流速场
    
    # 统计信息
    max_water_depth: float = 0.0
    max_velocity: float = 0.0
    inundation_area: float = 0.0  # m²
    
    # 错误信息
    error_message: Optional[str] = None


@dataclass
class GPUInfo:
    """GPU 信息"""
    available: bool
    device_count: int = 0
    devices: List[Dict[str, Any]] = field(default_factory=list)
    cuda_version: Optional[str] = None


# ============== HiPIMS 模拟引擎 ==============

class HipimsSimulator:
    """
    HiPIMS 模拟引擎（模拟实现）
    
    使用 NumPy 实现简化的 2D 浅水方程求解，用于测试框架。
    实际部署时可替换为真实的 HiPIMS Python 接口。
    """
    
    def __init__(self):
        self.simulations: Dict[str, SimulationResult] = {}
        self.configs: Dict[str, SimulationConfig] = {}
        self.results_dir = Path("resources/data/hipims_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def check_gpu(self) -> GPUInfo:
        """检查 GPU 可用性"""
        gpu_info = GPUInfo(available=False)
        
        try:
            # 尝试导入 PyTorch 检查 CUDA
            import torch
            if torch.cuda.is_available():
                gpu_info.available = True
                gpu_info.device_count = torch.cuda.device_count()
                for i in range(gpu_info.device_count):
                    gpu_info.devices.append({
                        "id": i,
                        "name": torch.cuda.get_device_name(i),
                        "memory_total": torch.cuda.get_device_properties(i).total_memory
                    })
                gpu_info.cuda_version = torch.version.cuda
        except ImportError:
            pass
        
        # 尝试检查 CuPy（HiPIMS 可能使用的 GPU 库）
        if not gpu_info.available:
            try:
                import cupy as cp
                gpu_info.available = True
                gpu_info.device_count = cp.cuda.runtime.getDeviceCount()
                for i in range(gpu_info.device_count):
                    props = cp.cuda.runtime.getDeviceProperties(i)
                    gpu_info.devices.append({
                        "id": i,
                        "name": props["name"].decode() if isinstance(props["name"], bytes) else props["name"],
                        "memory_total": props["totalGlobalMem"]
                    })
            except ImportError:
                pass
        
        return gpu_info
    
    def prepare_simulation_data(
        self,
        terrain_path: str,
        boundary_conditions: Dict[str, Any],
        rainfall_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备模拟所需数据"""
        simulation_id = f"HIPIMS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # 验证地形数据
        terrain_valid = self._validate_terrain(terrain_path)
        
        # 处理边界条件
        processed_boundary = self._process_boundary_conditions(boundary_conditions)
        
        # 处理降雨数据
        processed_rainfall = None
        if rainfall_data:
            processed_rainfall = self._process_rainfall_data(rainfall_data)
        
        return {
            "simulation_id": simulation_id,
            "status": "ready",
            "terrain_valid": terrain_valid,
            "boundary_conditions": processed_boundary,
            "rainfall_data": processed_rainfall,
            "prepared_at": datetime.now().isoformat()
        }
    
    def _validate_terrain(self, terrain_path: str) -> bool:
        """验证地形数据"""
        path = Path(terrain_path)
        if not path.exists():
            # 如果是相对路径，尝试从项目根目录查找
            path = Path("resources/data/terrain") / terrain_path
        return path.exists()
    
    def _process_boundary_conditions(self, bc: Dict[str, Any]) -> Dict[str, Any]:
        """处理边界条件"""
        processed = {
            "inflow_points": bc.get("inflow_points", []),
            "outflow_points": bc.get("outflow_points", []),
            "wall_boundaries": bc.get("wall_boundaries", []),
            "initial_water_level": bc.get("initial_water_level", 0.0)
        }
        return processed
    
    def _process_rainfall_data(self, rainfall: Dict[str, Any]) -> Dict[str, Any]:
        """处理降雨数据"""
        return {
            "type": rainfall.get("type", "uniform"),  # uniform 或 spatial
            "intensity": rainfall.get("intensity", 0.0),  # mm/h
            "duration": rainfall.get("duration", 3600),  # 秒
            "pattern": rainfall.get("pattern", "constant")  # constant 或 varying
        }
    
    def run_2d_simulation(
        self,
        config: SimulationConfig
    ) -> SimulationResult:
        """运行 2D 水动力模拟"""
        simulation_id = config.simulation_id
        
        # 创建结果对象
        result = SimulationResult(
            simulation_id=simulation_id,
            status=SimulationStatus.RUNNING.value,
            start_time=datetime.now().isoformat(),
            progress=0.0
        )
        
        self.simulations[simulation_id] = result
        self.configs[simulation_id] = config
        
        try:
            # 执行模拟（简化版 2D 浅水方程）
            grid_size = 100  # 100x100 网格
            dx = 10.0  # 网格间距 10m
            
            # 初始化地形（简化的高程模型）
            elevation = self._generate_terrain(grid_size, dx)
            
            # 初始化水深和流速
            water_depth = np.zeros((grid_size, grid_size))
            velocity_x = np.zeros((grid_size, grid_size))
            velocity_y = np.zeros((grid_size, grid_size))
            
            # 设置初始条件
            initial_level = config.boundary_conditions.get("initial_water_level", 0.0)
            if initial_level > 0:
                water_depth += initial_level
            
            # 应用边界条件
            inflow_points = config.boundary_conditions.get("inflow_points", [])
            for point in inflow_points:
                i, j = point.get("i", 0), point.get("j", grid_size // 2)
                discharge = point.get("discharge", 10.0)  # m³/s
                # 简化的入流处理
                if 0 <= i < grid_size and 0 <= j < grid_size:
                    water_depth[i, j] += discharge * config.time_step / (dx * dx)
            
            # 简化的模拟循环（实际 HiPIMS 使用更复杂的数值方法）
            num_steps = int(config.simulation_duration / config.time_step)
            output_steps = max(1, int(config.output_interval / config.time_step))
            
            # 存储时序结果
            depth_history = []
            velocity_history = []
            
            for step in range(num_steps):
                # 简化的洪水演进计算（扩散方程近似）
                water_depth, velocity_x, velocity_y = self._update_flow(
                    water_depth, velocity_x, velocity_y, elevation,
                    dx, config.time_step
                )
                
                # 应用降雨
                if config.rainfall_data and step * config.time_step < config.rainfall_data.get("duration", 0):
                    rainfall_intensity = config.rainfall_data.get("intensity", 0)  # mm/h
                    # 转换为 m/s 并添加到水深
                    rainfall_rate = rainfall_intensity / 1000 / 3600  # mm/h -> m/s
                    water_depth += rainfall_rate * config.time_step
                
                # 更新进度
                result.progress = (step + 1) / num_steps * 100
                
                # 保存输出
                if step % output_steps == 0:
                    depth_history.append(water_depth.copy())
                    velocity_magnitude = np.sqrt(velocity_x**2 + velocity_y**2)
                    velocity_history.append(velocity_magnitude.copy())
            
            # 计算结果统计
            result.max_water_depth = float(np.max(water_depth))
            result.max_velocity = float(np.max(np.sqrt(velocity_x**2 + velocity_y**2)))
            
            # 计算淹没面积（水深 > 0.1m 的区域）
            cell_area = dx * dx
            inundated_cells = np.sum(water_depth > 0.1)
            result.inundation_area = float(inundated_cells * cell_area)
            
            # 生成结果数据
            result.water_depth = {
                "grid_size": [grid_size, grid_size],
                "dx": dx,
                "final_depth": water_depth.tolist(),
                "max_depth": result.max_water_depth,
                "mean_depth": float(np.mean(water_depth[water_depth > 0])) if np.any(water_depth > 0) else 0.0
            }
            
            result.velocity_field = {
                "grid_size": [grid_size, grid_size],
                "dx": dx,
                "velocity_x": velocity_x.tolist(),
                "velocity_y": velocity_y.tolist(),
                "max_velocity": result.max_velocity,
                "mean_velocity": float(np.mean(np.sqrt(velocity_x**2 + velocity_y**2)))
            }
            
            # 计算淹没范围
            result.inundation_extent = self._calculate_inundation_extent(
                water_depth, dx
            )
            
            # 保存结果到文件
            self._save_simulation_result(simulation_id, result, depth_history, velocity_history)
            
            result.status = SimulationStatus.COMPLETED.value
            result.end_time = datetime.now().isoformat()
            result.progress = 100.0
            
        except Exception as e:
            result.status = SimulationStatus.FAILED.value
            result.error_message = str(e)
            result.end_time = datetime.now().isoformat()
        
        return result
    
    def _generate_terrain(self, grid_size: int, dx: float) -> np.ndarray:
        """生成简化地形"""
        x = np.linspace(0, (grid_size - 1) * dx, grid_size)
        y = np.linspace(0, (grid_size - 1) * dx, grid_size)
        X, Y = np.meshgrid(x, y)
        
        # 创建一个简单的倾斜平面 + 一些起伏
        elevation = 100.0 - 0.05 * X + 5 * np.sin(X / 100) * np.cos(Y / 100)
        return elevation
    
    def _update_flow(
        self,
        depth: np.ndarray,
        vel_x: np.ndarray,
        vel_y: np.ndarray,
        elevation: np.ndarray,
        dx: float,
        dt: float
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        简化的水流更新（基于扩散近似）
        实际 HiPIMS 使用完整的 2D 浅水方程求解器
        """
        # 计算水面高程
        water_surface = elevation + depth
        
        # 简化的流量计算（基于水面坡度）
        grad_x = np.zeros_like(depth)
        grad_y = np.zeros_like(depth)
        
        grad_x[1:-1, :] = (water_surface[2:, :] - water_surface[:-2, :]) / (2 * dx)
        grad_y[:, 1:-1] = (water_surface[:, 2:] - water_surface[:, :-2]) / (2 * dx)
        
        # 曼宁公式简化
        n = 0.03  # 曼宁系数
        
        # 更新流速（仅在水深 > 0 的区域）
        mask = depth > 0.01
        vel_x_new = vel_x.copy()
        vel_y_new = vel_y.copy()
        
        # 简化的动量方程
        vel_x_new[mask] = -np.sign(grad_x[mask]) * np.sqrt(np.abs(grad_x[mask])) * depth[mask]**(2/3) / n
        vel_y_new[mask] = -np.sign(grad_y[mask]) * np.sqrt(np.abs(grad_y[mask])) * depth[mask]**(2/3) / n
        
        # 限制流速
        max_vel = 5.0  # m/s
        vel_x_new = np.clip(vel_x_new, -max_vel, max_vel)
        vel_y_new = np.clip(vel_y_new, -max_vel, max_vel)
        
        # 简化的连续性方程（扩散）
        depth_new = depth.copy()
        depth_new[1:-1, 1:-1] += dt * (
            (depth[2:, 1:-1] - 2 * depth[1:-1, 1:-1] + depth[:-2, 1:-1]) / (dx * dx) * 0.1 +
            (depth[1:-1, 2:] - 2 * depth[1:-1, 1:-1] + depth[1:-1, :-2]) / (dx * dx) * 0.1
        )
        
        # 确保水深非负
        depth_new = np.maximum(depth_new, 0)
        
        return depth_new, vel_x_new, vel_y_new
    
    def _calculate_inundation_extent(
        self,
        depth: np.ndarray,
        dx: float
    ) -> Dict[str, Any]:
        """计算淹没范围"""
        # 定义不同水深等级
        levels = [
            ("minor", 0.1, 0.3),      # 轻度淹没
            ("moderate", 0.3, 0.8),   # 中度淹没
            ("major", 0.8, 1.5),      # 重度淹没
            ("extreme", 1.5, float('inf'))  # 极端淹没
        ]
        
        extent = {
            "total_area": float(np.sum(depth > 0.1) * dx * dx),
            "levels": {}
        }
        
        for name, min_depth, max_depth in levels:
            mask = (depth >= min_depth) & (depth < max_depth)
            area = float(np.sum(mask) * dx * dx)
            extent["levels"][name] = {
                "depth_range": [min_depth, max_depth if max_depth != float('inf') else "inf"],
                "area": area,
                "percentage": float(np.sum(mask) / depth.size * 100)
            }
        
        return extent
    
    def _save_simulation_result(
        self,
        simulation_id: str,
        result: SimulationResult,
        depth_history: List[np.ndarray],
        velocity_history: List[np.ndarray]
    ):
        """保存模拟结果到文件"""
        result_dir = self.results_dir / simulation_id
        result_dir.mkdir(exist_ok=True)
        
        # 保存主要结果（JSON 格式）
        result_file = result_dir / "result_summary.json"
        result_data = {
            "simulation_id": result.simulation_id,
            "status": result.status,
            "start_time": result.start_time,
            "end_time": result.end_time,
            "max_water_depth": result.max_water_depth,
            "max_velocity": result.max_velocity,
            "inundation_area": result.inundation_area,
            "inundation_extent": result.inundation_extent
        }
        
        import json
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # 保存网格数据（NumPy 格式）
        if result.water_depth:
            np.save(result_dir / "water_depth.npy", np.array(result.water_depth["final_depth"]))
        if result.velocity_field:
            np.save(result_dir / "velocity_x.npy", np.array(result.velocity_field["velocity_x"]))
            np.save(result_dir / "velocity_y.npy", np.array(result.velocity_field["velocity_y"]))
    
    def get_simulation_status(self, simulation_id: str) -> Optional[SimulationResult]:
        """获取模拟状态"""
        return self.simulations.get(simulation_id)
    
    def list_simulation_results(self) -> List[Dict[str, Any]]:
        """列出所有历史模拟结果"""
        results = []
        for sim_id, result in self.simulations.items():
            results.append({
                "simulation_id": sim_id,
                "status": result.status,
                "start_time": result.start_time,
                "end_time": result.end_time,
                "progress": result.progress,
                "max_water_depth": result.max_water_depth,
                "inundation_area": result.inundation_area
            })
        
        # 按开始时间排序
        results.sort(key=lambda x: x["start_time"], reverse=True)
        return results


# ============== MCP Server 实现 ==============

# 创建全局模拟器实例
simulator = HipimsSimulator()

# 创建 MCP Server
server = Server("flood-agent-hipims")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """定义可用工具"""
    return [
        Tool(
            name="prepare_simulation_data",
            description="准备 HiPIMS 模拟所需的数据（地形、边界条件、降雨数据）",
            inputSchema={
                "type": "object",
                "properties": {
                    "terrain_path": {
                        "type": "string",
                        "description": "地形数据文件路径（支持 GeoTIFF、ASCII Grid 格式）"
                    },
                    "boundary_conditions": {
                        "type": "object",
                        "description": "边界条件配置",
                        "properties": {
                            "inflow_points": {
                                "type": "array",
                                "description": "入流点列表",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "i": {"type": "integer", "description": "网格行索引"},
                                        "j": {"type": "integer", "description": "网格列索引"},
                                        "discharge": {"type": "number", "description": "流量 (m³/s)"}
                                    }
                                }
                            },
                            "outflow_points": {
                                "type": "array",
                                "description": "出流点列表"
                            },
                            "wall_boundaries": {
                                "type": "array",
                                "description": "固壁边界列表"
                            },
                            "initial_water_level": {
                                "type": "number",
                                "description": "初始水位 (m)",
                                "default": 0.0
                            }
                        }
                    },
                    "rainfall_data": {
                        "type": "object",
                        "description": "降雨数据（可选）",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["uniform", "spatial"],
                                "default": "uniform"
                            },
                            "intensity": {
                                "type": "number",
                                "description": "降雨强度 (mm/h)"
                            },
                            "duration": {
                                "type": "number",
                                "description": "降雨持续时间 (秒)"
                            },
                            "pattern": {
                                "type": "string",
                                "enum": ["constant", "varying"],
                                "default": "constant"
                            }
                        }
                    }
                },
                "required": ["terrain_path", "boundary_conditions"]
            }
        ),
        Tool(
            name="run_2d_simulation",
            description="运行 2D 水动力模拟（基于 HiPIMS 引擎）",
            inputSchema={
                "type": "object",
                "properties": {
                    "terrain_path": {
                        "type": "string",
                        "description": "地形数据文件路径"
                    },
                    "boundary_conditions": {
                        "type": "object",
                        "description": "边界条件配置"
                    },
                    "rainfall_data": {
                        "type": "object",
                        "description": "降雨数据（可选）"
                    },
                    "simulation_duration": {
                        "type": "number",
                        "description": "模拟时长 (秒)",
                        "default": 3600
                    },
                    "time_step": {
                        "type": "number",
                        "description": "计算时间步长 (秒)",
                        "default": 1.0
                    },
                    "output_interval": {
                        "type": "number",
                        "description": "结果输出间隔 (秒)",
                        "default": 300
                    },
                    "use_gpu": {
                        "type": "boolean",
                        "description": "是否使用 GPU 加速",
                        "default": True
                    },
                    "gpu_device": {
                        "type": "integer",
                        "description": "GPU 设备 ID",
                        "default": 0
                    }
                },
                "required": ["terrain_path", "boundary_conditions"]
            }
        ),
        Tool(
            name="check_gpu_availability",
            description="检查 GPU 加速是否可用（CUDA 支持）",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_simulation_status",
            description="获取指定模拟任务的状态和进度",
            inputSchema={
                "type": "object",
                "properties": {
                    "simulation_id": {
                        "type": "string",
                        "description": "模拟任务 ID"
                    }
                },
                "required": ["simulation_id"]
            }
        ),
        Tool(
            name="list_simulation_results",
            description="列出所有历史模拟结果",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制",
                        "default": 10
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "prepare_simulation_data":
            return await _handle_prepare_simulation_data(arguments)
        elif name == "run_2d_simulation":
            return await _handle_run_2d_simulation(arguments)
        elif name == "check_gpu_availability":
            return await _handle_check_gpu_availability(arguments)
        elif name == "get_simulation_status":
            return await _handle_get_simulation_status(arguments)
        elif name == "list_simulation_results":
            return await _handle_list_simulation_results(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
    except Exception as e:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)
        )]


async def _handle_prepare_simulation_data(args: Dict[str, Any]) -> List[TextContent]:
    """处理数据准备请求"""
    terrain_path = args["terrain_path"]
    boundary_conditions = args["boundary_conditions"]
    rainfall_data = args.get("rainfall_data")
    
    result = simulator.prepare_simulation_data(
        terrain_path=terrain_path,
        boundary_conditions=boundary_conditions,
        rainfall_data=rainfall_data
    )
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "message": "模拟数据准备完成",
            "data": result
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_run_2d_simulation(args: Dict[str, Any]) -> List[TextContent]:
    """处理模拟运行请求"""
    # 首先准备数据
    prep_result = simulator.prepare_simulation_data(
        terrain_path=args["terrain_path"],
        boundary_conditions=args["boundary_conditions"],
        rainfall_data=args.get("rainfall_data")
    )
    
    # 创建模拟配置
    config = SimulationConfig(
        simulation_id=prep_result["simulation_id"],
        terrain_path=args["terrain_path"],
        boundary_conditions=args["boundary_conditions"],
        rainfall_data=args.get("rainfall_data"),
        simulation_duration=args.get("simulation_duration", 3600.0),
        time_step=args.get("time_step", 1.0),
        output_interval=args.get("output_interval", 300.0),
        use_gpu=args.get("use_gpu", True),
        gpu_device=args.get("gpu_device", 0)
    )
    
    # 运行模拟
    result = simulator.run_2d_simulation(config)
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": result.status == SimulationStatus.COMPLETED.value,
            "simulation_id": result.simulation_id,
            "status": result.status,
            "message": "模拟运行完成" if result.status == SimulationStatus.COMPLETED.value else f"模拟失败: {result.error_message}",
            "results": {
                "max_water_depth": result.max_water_depth,
                "max_velocity": result.max_velocity,
                "inundation_area": result.inundation_area,
                "inundation_extent": result.inundation_extent
            },
            "timing": {
                "start_time": result.start_time,
                "end_time": result.end_time
            }
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_check_gpu_availability(args: Dict[str, Any]) -> List[TextContent]:
    """处理 GPU 检查请求"""
    gpu_info = simulator.check_gpu()
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "gpu_available": gpu_info.available,
            "device_count": gpu_info.device_count,
            "devices": gpu_info.devices,
            "cuda_version": gpu_info.cuda_version,
            "note": "GPU 加速可用" if gpu_info.available else "未检测到 GPU，将使用 CPU 模式运行"
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_get_simulation_status(args: Dict[str, Any]) -> List[TextContent]:
    """处理状态查询请求"""
    simulation_id = args["simulation_id"]
    result = simulator.get_simulation_status(simulation_id)
    
    if result is None:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": f"未找到模拟任务: {simulation_id}"
            }, ensure_ascii=False)
        )]
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "simulation_id": result.simulation_id,
            "status": result.status,
            "progress": result.progress,
            "start_time": result.start_time,
            "end_time": result.end_time,
            "summary": {
                "max_water_depth": result.max_water_depth,
                "max_velocity": result.max_velocity,
                "inundation_area": result.inundation_area
            },
            "error": result.error_message
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_list_simulation_results(args: Dict[str, Any]) -> List[TextContent]:
    """处理结果列表请求"""
    limit = args.get("limit", 10)
    results = simulator.list_simulation_results()
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "total": len(results),
            "limit": limit,
            "results": results[:limit]
        }, ensure_ascii=False, indent=2)
    )]


# ============== 主程序入口 ==============

async def main():
    """启动 MCP Server（Windows 兼容版）"""
    # 检查 API Key
    _check_api_key()
    
    # Windows 事件循环策略
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 局部导入 stdio_server
    from mcp.server.stdio import stdio_server as mcp_stdio_server
    
    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
