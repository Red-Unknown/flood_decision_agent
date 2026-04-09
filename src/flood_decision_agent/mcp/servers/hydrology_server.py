"""水利模型 MCP Server（集成版）

提供水文水利相关模型计算服务：
- 降雨径流模型
- 洪水演进模型
- 水库调度模型
- YOLO 视觉洪水检测
- HiPIMS 2D 水动力模拟
- 视觉辅助模型校准
- 服务间依赖调用（data_hub, hipims）

注意：此服务集成了多种水利模型能力，包括视觉检测和水动力模拟。
"""

import asyncio
import json
import os
import platform
import sys
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from mcp.server import Server
from mcp.types import Tool, TextContent

from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps
from src.flood_decision_agent.mcp.log import get_mcp_logger, ToolCallContext
from src.flood_decision_agent.mcp.log.error_formatter import format_error as format_error_dict

SERVER_NAME = "hydrology"
logger = get_mcp_logger(SERVER_NAME)


# ============== 服务间依赖管理 ==============

class MCPServiceClient:
    """MCP 服务客户端 - 用于服务间调用"""
    
    def __init__(self):
        self.service_urls = {
            "data_hub": os.environ.get("DATA_HUB_URL", "stdio"),
            "hipims": os.environ.get("HIPIMS_URL", "stdio"),
        }
        self._clients: Dict[str, Any] = {}
    
    async def call_data_hub(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用 data_hub 服务"""
        try:
            # 尝试通过 subprocess 调用 data_hub_server 模块
            import subprocess
            import tempfile
            
            # 创建临时文件传递参数
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump({"tool": tool_name, "arguments": arguments}, f, ensure_ascii=False)
                temp_file = f.name
            
            try:
                # 运行 data_hub 服务并获取结果
                result = subprocess.run(
                    [sys.executable, "-m", "flood_decision_agent.mcp.servers.data_hub_server", "--tool-call", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(Path(__file__).parent.parent.parent.parent.parent)
                )
                
                if result.returncode == 0 and result.stdout:
                    try:
                        return json.loads(result.stdout.strip().split('\n')[-1])
                    except json.JSONDecodeError:
                        return {"success": True, "output": result.stdout}
                else:
                    return {"success": False, "error": result.stderr or "调用失败"}
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            return {"success": False, "error": f"调用 data_hub 失败: {str(e)}"}
    
    async def call_hipims(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用 hipims 服务"""
        try:
            # 使用内部集成的 HipimsSimulator
            if tool_name == "run_2d_simulation":
                return await self._run_internal_hipims(arguments)
            elif tool_name == "check_gpu_availability":
                gpu_info = hipims_simulator.check_gpu()
                return {
                    "success": True,
                    "gpu_available": gpu_info["available"],
                    "device_count": gpu_info["device_count"],
                    "devices": gpu_info["devices"]
                }
            elif tool_name == "get_simulation_status":
                result = hipims_simulator.get_simulation_status(arguments.get("simulation_id"))
                if result:
                    return {
                        "success": True,
                        "simulation_id": result.simulation_id,
                        "status": result.status,
                        "progress": result.progress
                    }
                return {"success": False, "error": "未找到模拟任务"}
            else:
                return {"success": False, "error": f"不支持的 hipims 工具: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": f"调用 hipims 失败: {str(e)}"}
    
    async def _run_internal_hipims(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """运行内部 HiPIMS 模拟"""
        prep_result = hipims_simulator.prepare_simulation_data(
            terrain_path=arguments["terrain_path"],
            boundary_conditions=arguments["boundary_conditions"],
            rainfall_data=arguments.get("rainfall_data")
        )
        
        config = SimulationConfig(
            simulation_id=prep_result["simulation_id"],
            terrain_path=arguments["terrain_path"],
            boundary_conditions=arguments["boundary_conditions"],
            rainfall_data=arguments.get("rainfall_data"),
            simulation_duration=arguments.get("simulation_duration", 3600.0),
            time_step=arguments.get("time_step", 1.0),
            output_interval=arguments.get("output_interval", 300.0),
            use_gpu=arguments.get("use_gpu", True),
            gpu_device=0
        )
        
        result = hipims_simulator.run_2d_simulation(config)
        
        return {
            "success": result.status == SimulationStatus.COMPLETED.value,
            "simulation_id": result.simulation_id,
            "status": result.status,
            "results": {
                "max_water_depth": result.max_water_depth,
                "max_velocity": result.max_velocity,
                "inundation_area": result.inundation_area,
                "inundation_extent": result.inundation_extent
            }
        }


# 全局服务客户端实例
service_client = MCPServiceClient()


# ============== 启动检查 ==============
def _check_api_key():
    """检查 KIMI_API_KEY 环境变量"""
    if not os.environ.get("KIMI_API_KEY"):
        print("需要kimi_api_key", file=sys.stderr)
        sys.exit(1)


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
    inundation_extent: Optional[Dict[str, Any]] = None
    water_depth: Optional[Dict[str, Any]] = None
    velocity_field: Optional[Dict[str, Any]] = None
    
    # 统计信息
    max_water_depth: float = 0.0
    max_velocity: float = 0.0
    inundation_area: float = 0.0  # m²
    
    # 错误信息
    error_message: Optional[str] = None


@dataclass
class VisionDetectionResult:
    """视觉检测结果"""
    image_path: str
    detection_count: int
    detections: List[Dict[str, Any]]
    flood_area_estimate: float  # m²
    risk_level: str
    result_image: Optional[str] = None


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
        discharge = [r * area * runoff_coefficient / 3.6 for r in rainfall]
        
        return {
            "discharge": discharge,
            "total_runoff": sum(discharge) * 3600,
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
        k = inputs.get("k", 3.0)
        x = inputs.get("x", 0.3)
        
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
            "time_shift": 0,
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
                q_out = min(max_outflow, (current_level - target_level) * 10)
            else:
                q_out = max(0, q_in * 0.1)
            
            outflow.append(q_out)
            current_level += (q_in - q_out) * 0.001
        
        return {
            "outflow": outflow,
            "final_level": current_level,
            "total_release": sum(outflow) * 3600,
            "model": self.name
        }


# ============== YOLO 视觉检测模块 ==============

class YOLOVisionModule:
    """YOLO 视觉检测模块"""
    
    def __init__(self):
        self.models_dir = "./models"
        self.results_dir = "./results/yolo"
        self._model_cache: Dict[str, Any] = {}
        self._device: str = "cpu"
        self._deps_available = False
        self._deps_error = None
        self._check_dependencies()
        self._ensure_dirs()
    
    def _check_dependencies(self):
        """检查依赖是否可用"""
        try:
            import ultralytics
            import cv2
            import numpy as np
            self._deps_available = True
        except ImportError as e:
            self._deps_error = str(e)
            self._deps_available = False
    
    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
    
    def _get_device(self) -> str:
        """获取可用设备"""
        if self._device == "cpu":
            try:
                import torch
                self._device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self._device = "cpu"
        return self._device
    
    def _load_model(self, model_name: str = "yolo11n") -> Any:
        """加载 YOLO 模型"""
        if model_name in self._model_cache:
            return self._model_cache[model_name]
        
        try:
            from ultralytics import YOLO
            
            model_path = f"{model_name}.pt"
            local_path = os.path.join(self.models_dir, model_path)
            
            if os.path.exists(local_path):
                model = YOLO(local_path)
            else:
                model = YOLO(model_path)
                model.save(local_path)
            
            device = self._get_device()
            model.to(device)
            
            self._model_cache[model_name] = model
            return model
        except Exception as e:
            raise RuntimeError(f"模型加载失败: {e}")
    
    def detect_flood_from_image(
        self,
        image_path: str,
        confidence: float = 0.25,
        save_result: bool = True,
        pixel_scale: Optional[float] = None
    ) -> VisionDetectionResult:
        """从图像检测洪水区域"""
        if not self._deps_available:
            raise RuntimeError(f"依赖未安装: {self._deps_error}")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像不存在: {image_path}")
        
        import cv2
        
        # 加载图像获取尺寸
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        img_height, img_width = img.shape[:2]
        
        # 加载模型并检测
        model = self._load_model("yolo11n")
        results = model(image_path, conf=confidence, verbose=False)
        
        # 解析结果
        detections = []
        total_flood_area_pixels = 0
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls_id = int(box.cls[0])
                    cls_name = result.names[cls_id]
                    conf = float(box.conf[0])
                    
                    # 洪水相关类别
                    flood_related = ["water", "flood", "river", "lake", "puddle"]
                    if any(keyword in cls_name.lower() for keyword in flood_related):
                        bbox = box.xyxy[0].tolist()
                        detections.append({
                            "class": cls_name,
                            "confidence": round(conf, 4),
                            "bbox": bbox
                        })
                        # 计算面积（像素）
                        width = bbox[2] - bbox[0]
                        height = bbox[3] - bbox[1]
                        total_flood_area_pixels += width * height
        
        # 估算实际面积
        if pixel_scale:
            flood_area_estimate = total_flood_area_pixels * (pixel_scale ** 2)
        else:
            # 默认假设：图像覆盖 1km x 1km 区域
            pixel_area = (1000 / img_width) * (1000 / img_height)
            flood_area_estimate = total_flood_area_pixels * pixel_area
        
        # 确定风险等级
        risk_level = self._calculate_risk_level(flood_area_estimate, len(detections))
        
        # 保存结果图像
        result_path = None
        if save_result and detections:
            result_path = os.path.join(
                self.results_dir,
                f"flood_detect_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            )
            results[0].save(result_path)
        
        return VisionDetectionResult(
            image_path=image_path,
            detection_count=len(detections),
            detections=detections,
            flood_area_estimate=flood_area_estimate,
            risk_level=risk_level,
            result_image=result_path
        )
    
    def _calculate_risk_level(self, area: float, detection_count: int) -> str:
        """计算风险等级"""
        if area > 50000 or detection_count > 10:
            return "extreme"
        elif area > 10000 or detection_count > 5:
            return "high"
        elif area > 1000 or detection_count > 2:
            return "moderate"
        elif area > 0 or detection_count > 0:
            return "low"
        return "none"
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if not self._deps_available:
            return {
                "success": False,
                "error": f"依赖未安装: {self._deps_error}",
                "install_command": "pip install ultralytics opencv-python numpy"
            }
        
        try:
            import torch
            import ultralytics
            
            return {
                "success": True,
                "pytorch_version": torch.__version__,
                "ultralytics_version": ultralytics.__version__,
                "cuda_available": torch.cuda.is_available(),
                "device": self._get_device(),
                "model_name": "yolo11n"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# ============== HiPIMS 模拟引擎 ==============

class HipimsSimulator:
    """HiPIMS 模拟引擎"""
    
    def __init__(self):
        self.simulations: Dict[str, SimulationResult] = {}
        self.configs: Dict[str, SimulationConfig] = {}
        self.results_dir = Path("resources/data/hipims_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def check_gpu(self) -> Dict[str, Any]:
        """检查 GPU 可用性"""
        gpu_info = {"available": False, "device_count": 0, "devices": []}
        
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info["available"] = True
                gpu_info["device_count"] = torch.cuda.device_count()
                for i in range(gpu_info["device_count"]):
                    gpu_info["devices"].append({
                        "id": i,
                        "name": torch.cuda.get_device_name(i),
                        "memory_total": torch.cuda.get_device_properties(i).total_memory
                    })
                gpu_info["cuda_version"] = torch.version.cuda
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
        
        terrain_valid = self._validate_terrain(terrain_path)
        processed_boundary = self._process_boundary_conditions(boundary_conditions)
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
            path = Path("resources/data/terrain") / terrain_path
        return path.exists()
    
    def _process_boundary_conditions(self, bc: Dict[str, Any]) -> Dict[str, Any]:
        """处理边界条件"""
        return {
            "inflow_points": bc.get("inflow_points", []),
            "outflow_points": bc.get("outflow_points", []),
            "wall_boundaries": bc.get("wall_boundaries", []),
            "initial_water_level": bc.get("initial_water_level", 0.0)
        }
    
    def _process_rainfall_data(self, rainfall: Dict[str, Any]) -> Dict[str, Any]:
        """处理降雨数据"""
        return {
            "type": rainfall.get("type", "uniform"),
            "intensity": rainfall.get("intensity", 0.0),
            "duration": rainfall.get("duration", 3600),
            "pattern": rainfall.get("pattern", "constant")
        }
    
    def run_2d_simulation(self, config: SimulationConfig) -> SimulationResult:
        """运行 2D 水动力模拟"""
        simulation_id = config.simulation_id
        
        result = SimulationResult(
            simulation_id=simulation_id,
            status=SimulationStatus.RUNNING.value,
            start_time=datetime.now().isoformat(),
            progress=0.0
        )
        
        self.simulations[simulation_id] = result
        self.configs[simulation_id] = config
        
        try:
            # 简化版 2D 浅水方程模拟
            grid_size = 100
            dx = 10.0
            
            elevation = self._generate_terrain(grid_size, dx)
            water_depth = np.zeros((grid_size, grid_size))
            velocity_x = np.zeros((grid_size, grid_size))
            velocity_y = np.zeros((grid_size, grid_size))
            
            initial_level = config.boundary_conditions.get("initial_water_level", 0.0)
            if initial_level > 0:
                water_depth += initial_level
            
            inflow_points = config.boundary_conditions.get("inflow_points", [])
            for point in inflow_points:
                i, j = point.get("i", 0), point.get("j", grid_size // 2)
                discharge = point.get("discharge", 10.0)
                if 0 <= i < grid_size and 0 <= j < grid_size:
                    water_depth[i, j] += discharge * config.time_step / (dx * dx)
            
            num_steps = int(config.simulation_duration / config.time_step)
            output_steps = max(1, int(config.output_interval / config.time_step))
            
            for step in range(num_steps):
                water_depth, velocity_x, velocity_y = self._update_flow(
                    water_depth, velocity_x, velocity_y, elevation,
                    dx, config.time_step
                )
                
                if config.rainfall_data and step * config.time_step < config.rainfall_data.get("duration", 0):
                    rainfall_intensity = config.rainfall_data.get("intensity", 0)
                    rainfall_rate = rainfall_intensity / 1000 / 3600
                    water_depth += rainfall_rate * config.time_step
                
                result.progress = (step + 1) / num_steps * 100
            
            result.max_water_depth = float(np.max(water_depth))
            result.max_velocity = float(np.max(np.sqrt(velocity_x**2 + velocity_y**2)))
            
            cell_area = dx * dx
            inundated_cells = np.sum(water_depth > 0.1)
            result.inundation_area = float(inundated_cells * cell_area)
            
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
                "max_velocity": result.max_velocity
            }
            
            result.inundation_extent = self._calculate_inundation_extent(water_depth, dx)
            
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
        """简化的水流更新"""
        water_surface = elevation + depth
        
        grad_x = np.zeros_like(depth)
        grad_y = np.zeros_like(depth)
        
        grad_x[1:-1, :] = (water_surface[2:, :] - water_surface[:-2, :]) / (2 * dx)
        grad_y[:, 1:-1] = (water_surface[:, 2:] - water_surface[:, :-2]) / (2 * dx)
        
        n = 0.03
        
        mask = depth > 0.01
        vel_x_new = vel_x.copy()
        vel_y_new = vel_y.copy()
        
        vel_x_new[mask] = -np.sign(grad_x[mask]) * np.sqrt(np.abs(grad_x[mask])) * depth[mask]**(2/3) / n
        vel_y_new[mask] = -np.sign(grad_y[mask]) * np.sqrt(np.abs(grad_y[mask])) * depth[mask]**(2/3) / n
        
        max_vel = 5.0
        vel_x_new = np.clip(vel_x_new, -max_vel, max_vel)
        vel_y_new = np.clip(vel_y_new, -max_vel, max_vel)
        
        depth_new = depth.copy()
        depth_new[1:-1, 1:-1] += dt * (
            (depth[2:, 1:-1] - 2 * depth[1:-1, 1:-1] + depth[:-2, 1:-1]) / (dx * dx) * 0.1 +
            (depth[1:-1, 2:] - 2 * depth[1:-1, 1:-1] + depth[1:-1, :-2]) / (dx * dx) * 0.1
        )
        
        depth_new = np.maximum(depth_new, 0)
        
        return depth_new, vel_x_new, vel_y_new
    
    def _calculate_inundation_extent(self, depth: np.ndarray, dx: float) -> Dict[str, Any]:
        """计算淹没范围"""
        levels = [
            ("minor", 0.1, 0.3),
            ("moderate", 0.3, 0.8),
            ("major", 0.8, 1.5),
            ("extreme", 1.5, float('inf'))
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
    
    def get_simulation_status(self, simulation_id: str) -> Optional[SimulationResult]:
        """获取模拟状态"""
        return self.simulations.get(simulation_id)
    
    def list_simulation_results(self, limit: int = 10) -> List[Dict[str, Any]]:
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
        
        results.sort(key=lambda x: x["start_time"], reverse=True)
        return results[:limit]


# ============== 视觉辅助校准模块 ==============

class VisionCalibrationModule:
    """视觉辅助模型校准模块"""
    
    def __init__(self, vision_module: YOLOVisionModule, simulator: HipimsSimulator):
        self.vision_module = vision_module
        self.simulator = simulator
    
    def calibrate_with_vision(
        self,
        image_path: str,
        simulation_result: Dict[str, Any],
        calibration_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """使用视觉检测结果校准水文模型参数"""
        # 1. 获取视觉检测结果
        vision_result = self.vision_module.detect_flood_from_image(image_path)
        
        # 2. 获取模拟结果
        sim_inundation_area = simulation_result.get("inundation_area", 0)
        sim_max_depth = simulation_result.get("max_water_depth", 0)
        
        # 3. 计算差异
        vision_area = vision_result.flood_area_estimate
        area_difference = vision_area - sim_inundation_area
        area_error_ratio = abs(area_difference) / vision_area if vision_area > 0 else 0
        
        # 4. 生成校准建议
        calibration_suggestions = []
        
        if area_error_ratio > 0.3:
            calibration_suggestions.append({
                "parameter": "runoff_coefficient",
                "current_value": 0.7,
                "suggested_value": 0.7 * (vision_area / sim_inundation_area) if sim_inundation_area > 0 else 0.7,
                "reason": f"模拟淹没面积 ({sim_inundation_area:.1f} m²) 与视觉检测结果 ({vision_area:.1f} m²) 差异较大"
            })
        
        if vision_result.risk_level in ["high", "extreme"] and sim_max_depth < 0.5:
            calibration_suggestions.append({
                "parameter": "roughness_coefficient",
                "current_value": 0.03,
                "suggested_value": 0.05,
                "reason": "视觉检测显示高风险，但模拟水深较低，建议增加糙率系数"
            })
        
        # 5. 计算校准评分
        calibration_score = max(0, 1 - area_error_ratio)
        
        return {
            "success": True,
            "vision_detection": {
                "flood_area": vision_area,
                "risk_level": vision_result.risk_level,
                "detection_count": vision_result.detection_count
            },
            "simulation_result": {
                "inundation_area": sim_inundation_area,
                "max_water_depth": sim_max_depth
            },
            "comparison": {
                "area_difference": area_difference,
                "area_error_ratio": area_error_ratio,
                "calibration_score": calibration_score
            },
            "calibration_suggestions": calibration_suggestions,
            "calibrated": len(calibration_suggestions) > 0
        }
    
    def get_model_comparison(
        self,
        vision_result: Dict[str, Any],
        simulation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """对比视觉检测结果与多个模拟结果"""
        comparisons = []
        
        vision_area = vision_result.get("flood_area_estimate", 0)
        
        for sim_result in simulation_results:
            sim_area = sim_result.get("inundation_area", 0)
            difference = abs(vision_area - sim_area)
            error_ratio = difference / vision_area if vision_area > 0 else 0
            
            comparisons.append({
                "simulation_id": sim_result.get("simulation_id", "unknown"),
                "vision_area": vision_area,
                "simulated_area": sim_area,
                "difference": difference,
                "error_ratio": error_ratio,
                "match_score": max(0, 1 - error_ratio)
            })
        
        # 按匹配度排序
        comparisons.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "success": True,
            "vision_result": vision_result,
            "comparisons": comparisons,
            "best_match": comparisons[0] if comparisons else None,
            "total_compared": len(comparisons)
        }


# ============== MCP Server 实现 ==============

# 创建全局实例
vision_module = YOLOVisionModule()
hipims_simulator = HipimsSimulator()
calibration_module = VisionCalibrationModule(vision_module, hipims_simulator)

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
        # ===== 原有工具 =====
        Tool(
            name="list_hydrology_models",
            description="列出所有可用的水利模型",
            inputSchema={"type": "object", "properties": {}}
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
        ),
        # ===== YOLO 视觉检测工具 =====
        Tool(
            name="detect_flood_from_image",
            description="从图像检测洪水区域，返回检测结果、面积估算和风险等级",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "输入图像路径"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "置信度阈值 (0-1)",
                        "default": 0.25
                    },
                    "save_result": {
                        "type": "boolean",
                        "description": "是否保存结果图像",
                        "default": True
                    },
                    "pixel_scale": {
                        "type": "number",
                        "description": "像素到实际距离的比例 (m/pixel)，可选"
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="get_yolo_model_info",
            description="获取 YOLO 视觉检测模型信息",
            inputSchema={"type": "object", "properties": {}}
        ),
        # ===== HiPIMS 工具 =====
        Tool(
            name="run_hipims_workflow",
            description="运行完整的 HiPIMS 工作流：整合降雨数据→边界条件→HiPIMS 2D 模拟",
            inputSchema={
                "type": "object",
                "properties": {
                    "terrain_path": {
                        "type": "string",
                        "description": "地形数据文件路径"
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
                                        "i": {"type": "integer"},
                                        "j": {"type": "integer"},
                                        "discharge": {"type": "number"}
                                    }
                                }
                            },
                            "outflow_points": {"type": "array"},
                            "wall_boundaries": {"type": "array"},
                            "initial_water_level": {
                                "type": "number",
                                "default": 0.0
                            }
                        }
                    },
                    "rainfall_data": {
                        "type": "object",
                        "description": "降雨数据",
                        "properties": {
                            "type": {"type": "string", "enum": ["uniform", "spatial"]},
                            "intensity": {"type": "number", "description": "降雨强度 (mm/h)"},
                            "duration": {"type": "number", "description": "持续时间 (秒)"},
                            "pattern": {"type": "string", "enum": ["constant", "varying"]}
                        }
                    },
                    "simulation_duration": {
                        "type": "number",
                        "description": "模拟时长 (秒)",
                        "default": 3600
                    },
                    "time_step": {
                        "type": "number",
                        "description": "时间步长 (秒)",
                        "default": 1.0
                    },
                    "output_interval": {
                        "type": "number",
                        "description": "输出间隔 (秒)",
                        "default": 300
                    },
                    "use_gpu": {
                        "type": "boolean",
                        "description": "是否使用 GPU",
                        "default": True
                    }
                },
                "required": ["terrain_path", "boundary_conditions"]
            }
        ),
        Tool(
            name="check_gpu_availability",
            description="检查 GPU 加速是否可用",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_hipims_simulation_status",
            description="获取 HiPIMS 模拟任务状态",
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
            name="list_hipims_results",
            description="列出 HiPIMS 历史模拟结果",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回数量限制",
                        "default": 10
                    }
                }
            }
        ),
        # ===== 视觉辅助校准工具 =====
        Tool(
            name="calibrate_with_vision",
            description="使用 YOLO 视觉检测结果校准水文模型参数",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "洪水图像路径"
                    },
                    "simulation_id": {
                        "type": "string",
                        "description": "HiPIMS 模拟任务 ID"
                    },
                    "calibration_params": {
                        "type": "object",
                        "description": "校准参数配置"
                    }
                },
                "required": ["image_path", "simulation_id"]
            }
        ),
        Tool(
            name="get_model_comparison",
            description="对比视觉检测结果与多个模拟结果",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "洪水图像路径"
                    },
                    "simulation_ids": {
                        "type": "array",
                        "description": "要对比的模拟任务 ID 列表",
                        "items": {"type": "string"}
                    }
                },
                "required": ["image_path", "simulation_ids"]
            }
        ),
        # ===== 服务间依赖调用工具 =====
        Tool(
            name="run_integrated_workflow",
            description="运行完整集成工作流：获取降雨数据→径流计算→HiPIMS模拟→视觉检测→校准",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称（用于获取降雨数据）"
                    },
                    "catchment_area": {
                        "type": "number",
                        "description": "流域面积 (km²)",
                        "default": 100
                    },
                    "terrain_path": {
                        "type": "string",
                        "description": "地形数据路径"
                    },
                    "image_path": {
                        "type": "string",
                        "description": "洪水图像路径（用于视觉检测和校准）"
                    },
                    "simulation_duration": {
                        "type": "number",
                        "description": "模拟时长 (秒)",
                        "default": 3600
                    }
                },
                "required": ["city", "terrain_path"]
            }
        ),
        Tool(
            name="fetch_rainfall_and_runoff",
            description="从 data_hub 获取降雨数据并运行径流模型",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    },
                    "catchment_area": {
                        "type": "number",
                        "description": "流域面积 (km²)",
                        "default": 100
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="run_hipims_with_rainfall",
            description="使用径流结果运行 HiPIMS 2D 模拟",
            inputSchema={
                "type": "object",
                "properties": {
                    "runoff_result": {
                        "type": "object",
                        "description": "径流计算结果"
                    },
                    "terrain_path": {
                        "type": "string",
                        "description": "地形数据路径"
                    },
                    "simulation_duration": {
                        "type": "number",
                        "description": "模拟时长 (秒)",
                        "default": 3600
                    }
                },
                "required": ["runoff_result", "terrain_path"]
            }
        ),
        Tool(
            name="detect_and_calibrate",
            description="使用 YOLO 检测洪水并校准模拟结果",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "洪水图像路径"
                    },
                    "simulation_id": {
                        "type": "string",
                        "description": "HiPIMS 模拟任务 ID"
                    }
                },
                "required": ["image_path", "simulation_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    with ToolCallContext(SERVER_NAME, name, arguments, logger):
        try:
            # ===== 原有工具处理 =====
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
            # ===== YOLO 视觉检测工具处理 =====
            elif name == "detect_flood_from_image":
                return await _handle_detect_flood_from_image(arguments)
            elif name == "get_yolo_model_info":
                return await _handle_get_yolo_model_info(arguments)
            # ===== HiPIMS 工具处理 =====
            elif name == "run_hipims_workflow":
                return await _handle_run_hipims_workflow(arguments)
            elif name == "check_gpu_availability":
                return await _handle_check_gpu_availability(arguments)
            elif name == "get_hipims_simulation_status":
                return await _handle_get_hipims_simulation_status(arguments)
            elif name == "list_hipims_results":
                return await _handle_list_hipims_results(arguments)
            # ===== 视觉辅助校准工具处理 =====
            elif name == "calibrate_with_vision":
                return await _handle_calibrate_with_vision(arguments)
            elif name == "get_model_comparison":
                return await _handle_get_model_comparison(arguments)
            # ===== 服务间依赖调用工具处理 =====
            elif name == "run_integrated_workflow":
                return await _handle_run_integrated_workflow(arguments)
            elif name == "fetch_rainfall_and_runoff":
                return await _handle_fetch_rainfall_and_runoff(arguments)
            elif name == "run_hipims_with_rainfall":
                return await _handle_run_hipims_with_rainfall(arguments)
            elif name == "detect_and_calibrate":
                return await _handle_detect_and_calibrate(arguments)
            else:
                raise ValueError(f"未知工具: {name}")
        except Exception as e:
            logger.error(f"工具 {name} 执行失败: {e}")
            error_dict = format_error_dict(e, SERVER_NAME, name, arguments)
            return [TextContent(
                type="text",
                text=fast_json_dumps(error_dict, ensure_ascii=False)
            )]


# ===== 原有工具处理函数 =====

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
        text=fast_json_dumps({
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
        text=fast_json_dumps({
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
        text=fast_json_dumps({
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
        text=fast_json_dumps({
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
        text=fast_json_dumps({
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
    
    time_steps = len(forecast_inflow)
    plan_id = f"DSP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
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
        text=fast_json_dumps({
            "success": True,
            "plan": plan,
            "model_used": "reservoir_dispatch"
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_validate_safety(args: Dict[str, Any]) -> List[TextContent]:
    """验证调度方案安全性"""
    dispatch_plan = args.get("dispatch_plan", {})
    
    violations = []
    warnings = []
    
    outflow = dispatch_plan.get("outflow_schedule", [])
    
    max_outflow = max(outflow) if outflow else 0
    if max_outflow > 5000:
        violations.append(f"最大下泄流量 {max_outflow:.2f} m³/s 超过安全阈值")
    elif max_outflow > 3000:
        warnings.append(f"最大下泄流量 {max_outflow:.2f} m³/s 接近安全阈值")
    
    final_level = dispatch_plan.get("expected_final_level", 0)
    if final_level > 110:
        violations.append(f"预测最高水位 {final_level:.2f}m 超过限制")
    
    is_safe = len(violations) == 0
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "is_safe": is_safe,
            "violations": violations,
            "warnings": warnings,
            "plan_id": dispatch_plan.get("plan_id", "unknown"),
            "validation_time": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


# ===== YOLO 视觉检测工具处理函数 =====

async def _handle_detect_flood_from_image(args: Dict[str, Any]) -> List[TextContent]:
    """处理图像洪水检测请求"""
    image_path = args["image_path"]
    confidence = args.get("confidence", 0.25)
    save_result = args.get("save_result", True)
    pixel_scale = args.get("pixel_scale")
    
    result = vision_module.detect_flood_from_image(
        image_path=image_path,
        confidence=confidence,
        save_result=save_result,
        pixel_scale=pixel_scale
    )
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "task": "flood_detection",
            "image_path": result.image_path,
            "detection_count": result.detection_count,
            "detections": result.detections,
            "flood_area_estimate": result.flood_area_estimate,
            "risk_level": result.risk_level,
            "result_image": result.result_image,
            "device": vision_module._get_device(),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_get_yolo_model_info(args: Dict[str, Any]) -> List[TextContent]:
    """获取 YOLO 模型信息"""
    info = vision_module.get_model_info()
    
    return [TextContent(
        type="text",
        text=fast_json_dumps(info, ensure_ascii=False, indent=2)
    )]


# ===== HiPIMS 工具处理函数 =====

async def _handle_run_hipims_workflow(args: Dict[str, Any]) -> List[TextContent]:
    """运行 HiPIMS 工作流"""
    # 准备数据
    prep_result = hipims_simulator.prepare_simulation_data(
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
        gpu_device=0
    )
    
    # 运行模拟
    result = hipims_simulator.run_2d_simulation(config)
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": result.status == SimulationStatus.COMPLETED.value,
            "simulation_id": result.simulation_id,
            "status": result.status,
            "message": "HiPIMS 模拟运行完成" if result.status == SimulationStatus.COMPLETED.value else f"模拟失败: {result.error_message}",
            "workflow_steps": [
                "prepared_simulation_data",
                "configured_boundary_conditions",
                "applied_rainfall_data",
                "executed_2d_simulation"
            ],
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
    """检查 GPU 可用性"""
    gpu_info = hipims_simulator.check_gpu()
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "gpu_available": gpu_info["available"],
            "device_count": gpu_info["device_count"],
            "devices": gpu_info["devices"],
            "cuda_version": gpu_info.get("cuda_version"),
            "note": "GPU 加速可用" if gpu_info["available"] else "未检测到 GPU，将使用 CPU 模式运行"
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_get_hipims_simulation_status(args: Dict[str, Any]) -> List[TextContent]:
    """获取 HiPIMS 模拟状态"""
    simulation_id = args["simulation_id"]
    result = hipims_simulator.get_simulation_status(simulation_id)
    
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


async def _handle_list_hipims_results(args: Dict[str, Any]) -> List[TextContent]:
    """列出 HiPIMS 历史结果"""
    limit = args.get("limit", 10)
    results = hipims_simulator.list_simulation_results(limit)
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "total": len(results),
            "limit": limit,
            "results": results
        }, ensure_ascii=False, indent=2)
    )]


# ===== 视觉辅助校准工具处理函数 =====

async def _handle_calibrate_with_vision(args: Dict[str, Any]) -> List[TextContent]:
    """使用视觉检测校准模型"""
    image_path = args["image_path"]
    simulation_id = args["simulation_id"]
    calibration_params = args.get("calibration_params", {})
    
    # 获取模拟结果
    sim_result = hipims_simulator.get_simulation_status(simulation_id)
    if sim_result is None:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": f"未找到模拟任务: {simulation_id}"
            }, ensure_ascii=False)
        )]
    
    # 转换为字典
    sim_result_dict = {
        "inundation_area": sim_result.inundation_area,
        "max_water_depth": sim_result.max_water_depth,
        "inundation_extent": sim_result.inundation_extent
    }
    
    # 执行校准
    calibration_result = calibration_module.calibrate_with_vision(
        image_path=image_path,
        simulation_result=sim_result_dict,
        calibration_params=calibration_params
    )
    
    return [TextContent(
        type="text",
        text=fast_json_dumps(calibration_result, ensure_ascii=False, indent=2)
    )]


async def _handle_get_model_comparison(args: Dict[str, Any]) -> List[TextContent]:
    """获取模型结果对比"""
    image_path = args["image_path"]
    simulation_ids = args.get("simulation_ids", [])
    
    # 获取视觉检测结果
    vision_result = vision_module.detect_flood_from_image(image_path)
    vision_dict = {
        "flood_area_estimate": vision_result.flood_area_estimate,
        "risk_level": vision_result.risk_level,
        "detection_count": vision_result.detection_count
    }
    
    # 获取模拟结果
    sim_results = []
    for sim_id in simulation_ids:
        sim = hipims_simulator.get_simulation_status(sim_id)
        if sim:
            sim_results.append({
                "simulation_id": sim.simulation_id,
                "inundation_area": sim.inundation_area,
                "max_water_depth": sim.max_water_depth,
                "status": sim.status
            })
    
    # 执行对比
    comparison_result = calibration_module.get_model_comparison(vision_dict, sim_results)
    
    return [TextContent(
        type="text",
        text=fast_json_dumps(comparison_result, ensure_ascii=False, indent=2)
    )]


# ===== 服务间依赖调用工具处理函数 =====

async def _handle_run_integrated_workflow(args: Dict[str, Any]) -> List[TextContent]:
    """运行完整集成工作流"""
    city = args["city"]
    terrain_path = args["terrain_path"]
    image_path = args.get("image_path")
    catchment_area = args.get("catchment_area", 100)
    simulation_duration = args.get("simulation_duration", 3600)
    
    workflow_result = {
        "success": True,
        "workflow": "integrated_data_to_calibration",
        "steps": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Step 1: 获取降雨数据并运行径流模型
        rainfall_runoff_result = await _fetch_rainfall_and_runoff_internal(city, catchment_area)
        workflow_result["steps"].append({
            "step": 1,
            "name": "rainfall_runoff",
            "status": "success" if rainfall_runoff_result.get("success") else "failed",
            "data": rainfall_runoff_result
        })
        
        if not rainfall_runoff_result.get("success"):
            workflow_result["success"] = False
            workflow_result["error"] = rainfall_runoff_result.get("error", "降雨径流计算失败")
            return [TextContent(type="text", text=fast_json_dumps(workflow_result, ensure_ascii=False, indent=2))]
        
        # Step 2: 运行 HiPIMS 2D 模拟
        hipims_result = await _run_hipims_with_runoff_internal(
            rainfall_runoff_result, terrain_path, simulation_duration
        )
        workflow_result["steps"].append({
            "step": 2,
            "name": "hipims_simulation",
            "status": "success" if hipims_result.get("success") else "failed",
            "data": hipims_result
        })
        
        if not hipims_result.get("success"):
            workflow_result["success"] = False
            workflow_result["error"] = hipims_result.get("error", "HiPIMS 模拟失败")
            return [TextContent(type="text", text=fast_json_dumps(workflow_result, ensure_ascii=False, indent=2))]
        
        # Step 3: 视觉检测和校准（如果提供了图像路径）
        if image_path:
            calibration_result = await _detect_and_calibrate_internal(
                image_path, hipims_result.get("simulation_id")
            )
            workflow_result["steps"].append({
                "step": 3,
                "name": "vision_calibration",
                "status": "success" if calibration_result.get("success") else "failed",
                "data": calibration_result
            })
        
        workflow_result["summary"] = {
            "city": city,
            "simulation_id": hipims_result.get("simulation_id"),
            "max_water_depth": hipims_result.get("results", {}).get("max_water_depth"),
            "inundation_area": hipims_result.get("results", {}).get("inundation_area"),
            "steps_completed": len(workflow_result["steps"])
        }
        
    except Exception as e:
        workflow_result["success"] = False
        workflow_result["error"] = str(e)
    
    return [TextContent(
        type="text",
        text=fast_json_dumps(workflow_result, ensure_ascii=False, indent=2)
    )]


async def _handle_fetch_rainfall_and_runoff(args: Dict[str, Any]) -> List[TextContent]:
    """处理获取降雨数据并运行径流模型请求"""
    city = args["city"]
    catchment_area = args.get("catchment_area", 100)
    
    result = await _fetch_rainfall_and_runoff_internal(city, catchment_area)
    
    return [TextContent(
        type="text",
        text=fast_json_dumps(result, ensure_ascii=False, indent=2)
    )]


async def _fetch_rainfall_and_runoff_internal(city: str, catchment_area: float) -> Dict[str, Any]:
    """内部函数：获取降雨数据并运行径流模型"""
    try:
        # 调用 data_hub 获取降雨数据
        rainfall_data = await service_client.call_data_hub(
            "get_rainfall_data",
            {"city": city, "provider": "auto", "use_cache": True}
        )
        
        if not rainfall_data.get("success"):
            # 使用模拟降雨数据
            rainfall_values = [5.0, 10.0, 15.0, 20.0, 15.0, 10.0, 5.0]  # mm
        else:
            # 从返回数据中提取降雨信息
            current = rainfall_data.get("data", {}).get("current", {})
            rain_1h = current.get("rain_1h", 0) or current.get("precipitation", 0)
            # 生成降雨序列
            rainfall_values = [rain_1h * (0.5 + i * 0.2) for i in range(6)]
        
        # 运行径流模型
        model = MODEL_REGISTRY["rainfall_runoff"]
        inputs = {
            "rainfall": rainfall_values,
            "catchment_area": catchment_area
        }
        runoff_result = model.run(inputs)
        
        return {
            "success": True,
            "city": city,
            "rainfall_data": rainfall_data if rainfall_data.get("success") else None,
            "rainfall_values": rainfall_values,
            "runoff_result": runoff_result,
            "peak_discharge": runoff_result.get("peak_discharge"),
            "total_runoff": runoff_result.get("total_runoff")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _handle_run_hipims_with_rainfall(args: Dict[str, Any]) -> List[TextContent]:
    """处理使用径流结果运行 HiPIMS 模拟请求"""
    runoff_result = args["runoff_result"]
    terrain_path = args["terrain_path"]
    simulation_duration = args.get("simulation_duration", 3600)
    
    result = await _run_hipims_with_runoff_internal(runoff_result, terrain_path, simulation_duration)
    
    return [TextContent(
        type="text",
        text=fast_json_dumps(result, ensure_ascii=False, indent=2)
    )]


async def _run_hipims_with_runoff_internal(
    runoff_result: Dict[str, Any],
    terrain_path: str,
    simulation_duration: float
) -> Dict[str, Any]:
    """内部函数：使用径流结果运行 HiPIMS 模拟"""
    try:
        peak_discharge = runoff_result.get("peak_discharge", 100)
        
        # 准备边界条件
        boundary_conditions = {
            "inflow_points": [{"i": 0, "j": 50, "discharge": peak_discharge}],
            "outflow_points": [{"i": 99, "j": 50}],
            "wall_boundaries": [],
            "initial_water_level": 0.0
        }
        
        # 调用 hipims 服务
        hipims_result = await service_client.call_hipims(
            "run_2d_simulation",
            {
                "terrain_path": terrain_path,
                "boundary_conditions": boundary_conditions,
                "simulation_duration": simulation_duration,
                "time_step": 1.0,
                "output_interval": 300,
                "use_gpu": True
            }
        )
        
        return hipims_result
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _handle_detect_and_calibrate(args: Dict[str, Any]) -> List[TextContent]:
    """处理检测和校准请求"""
    image_path = args["image_path"]
    simulation_id = args["simulation_id"]
    
    result = await _detect_and_calibrate_internal(image_path, simulation_id)
    
    return [TextContent(
        type="text",
        text=fast_json_dumps(result, ensure_ascii=False, indent=2)
    )]


async def _detect_and_calibrate_internal(image_path: str, simulation_id: str) -> Dict[str, Any]:
    """内部函数：检测和校准"""
    try:
        # 获取模拟结果
        sim_result = hipims_simulator.get_simulation_status(simulation_id)
        if sim_result is None:
            return {"success": False, "error": f"未找到模拟任务: {simulation_id}"}
        
        # 执行视觉检测
        vision_result = vision_module.detect_flood_from_image(image_path)
        
        # 执行校准
        sim_result_dict = {
            "inundation_area": sim_result.inundation_area,
            "max_water_depth": sim_result.max_water_depth,
            "inundation_extent": sim_result.inundation_extent
        }
        
        calibration_result = calibration_module.calibrate_with_vision(
            image_path=image_path,
            simulation_result=sim_result_dict
        )
        
        return {
            "success": True,
            "simulation_id": simulation_id,
            "vision_detection": {
                "flood_area": vision_result.flood_area_estimate,
                "risk_level": vision_result.risk_level,
                "detection_count": vision_result.detection_count
            },
            "calibration": calibration_result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============== 主程序入口 ==============

async def main():
    """启动 MCP Server"""
    logger.info(f"MCP Server [{SERVER_NAME}] 启动中...")
    
    _check_api_key()
    
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    
    from mcp.server.stdio import stdio_server as mcp_stdio_server
    
    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
    
    logger.info(f"MCP Server [{SERVER_NAME}] 已关闭")


if __name__ == "__main__":
    asyncio.run(main())
