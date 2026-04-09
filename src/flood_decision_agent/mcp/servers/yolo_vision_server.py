"""YOLO Vision MCP Server

基于 YOLO11n 的水利视觉检测服务：
- 洪水区域检测
- 水体识别
- 堤坝/基础设施检测
- 支持 CPU/GPU 自动切换

模型: YOLO11n (轻量级，适合快速推理)

安装依赖:
    pip install ultralytics opencv-python numpy
"""

import asyncio
import os
import platform
import sys

from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps, fast_json_loads
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    # 如果 mcp 模块不可用，创建一个模拟实现
    print("错误: mcp 模块未安装。请运行: pip install mcp", file=sys.stderr)
    sys.exit(1)

# 创建 MCP Server
server = Server("flood-agent-yolo-vision")

# 配置
MODELS_DIR = "./models"
DATASETS_DIR = "./datasets"
RESULTS_DIR = "./results/yolo"

# 全局模型缓存
_model_cache: Dict[str, Any] = {}
_device: str = "cpu"

# 依赖检查标志
_deps_available = False
_deps_error = None

def _check_dependencies():
    """检查依赖是否可用"""
    global _deps_available, _deps_error
    try:
        import ultralytics
        import cv2
        import numpy as np
        _deps_available = True
        return True
    except ImportError as e:
        _deps_error = str(e)
        return False

# 初始化时检查依赖
_deps_available = _check_dependencies()


def _ensure_dirs():
    """确保目录存在"""
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(DATASETS_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)


def _get_device() -> str:
    """获取可用设备 (cuda/cpu)"""
    global _device
    if _device is None:
        try:
            import torch
            _device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            _device = "cpu"
    return _device


def _load_model(model_name: str = "yolo11n") -> Any:
    """加载 YOLO 模型（带缓存）"""
    global _model_cache

    if model_name in _model_cache:
        return _model_cache[model_name]

    try:
        from ultralytics import YOLO

        # 尝试加载预训练模型
        model_path = f"{model_name}.pt"

        # 检查本地是否存在
        local_path = os.path.join(MODELS_DIR, model_path)
        if os.path.exists(local_path):
            model = YOLO(local_path)
        else:
            # 从 ultralytics 下载
            model = YOLO(model_path)
            # 保存到本地
            model.save(local_path)

        # 移动到正确设备
        device = _get_device()
        model.to(device)

        _model_cache[model_name] = model
        return model

    except Exception as e:
        raise RuntimeError(f"模型加载失败: {e}")


def _check_deps_response():
    """返回依赖检查失败的响应"""
    if not _deps_available:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": f"依赖未安装: {_deps_error}",
                "install_command": "pip install ultralytics opencv-python numpy",
                "note": "请在系统 Python 环境中运行上述命令安装依赖"
            }, ensure_ascii=False, indent=2)
        )]
    return None


@server.list_tools()
async def list_tools() -> List[Tool]:
    """定义可用工具"""
    return [
        Tool(
            name="detect_flood_areas",
            description="检测图像中的洪水区域",
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
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="detect_water_bodies",
            description="检测水体（河流、湖泊、水库等）",
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
                        "default": 0.3
                    },
                    "save_result": {
                        "type": "boolean",
                        "description": "是否保存结果图像",
                        "default": True
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="detect_infrastructure",
            description="检测水利基础设施（堤坝、桥梁、水闸等）",
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
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="batch_detect",
            description="批量检测目录中的图像",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_dir": {
                        "type": "string",
                        "description": "图像目录路径"
                    },
                    "task": {
                        "type": "string",
                        "description": "检测任务类型",
                        "enum": ["flood", "water", "infrastructure", "all"],
                        "default": "all"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "置信度阈值 (0-1)",
                        "default": 0.25
                    }
                },
                "required": ["image_dir"]
            }
        ),
        Tool(
            name="get_model_info",
            description="获取模型信息",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="download_test_dataset",
            description="下载小规模水利测试数据集",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_name": {
                        "type": "string",
                        "description": "数据集名称",
                        "enum": ["flood_sample", "water_body_sample"],
                        "default": "flood_sample"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    _ensure_dirs()

    try:
        if name == "detect_flood_areas":
            return await _handle_detect_flood(arguments)
        elif name == "detect_water_bodies":
            return await _handle_detect_water(arguments)
        elif name == "detect_infrastructure":
            return await _handle_detect_infrastructure(arguments)
        elif name == "batch_detect":
            return await _handle_batch_detect(arguments)
        elif name == "get_model_info":
            return await _handle_model_info(arguments)
        elif name == "download_test_dataset":
            return await _handle_download_dataset(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
    except Exception as e:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }, ensure_ascii=False)
        )]


async def _handle_detect_flood(args: Dict[str, Any]) -> List[TextContent]:
    """检测洪水区域"""
    # 检查依赖
    deps_error = _check_deps_response()
    if deps_error:
        return deps_error

    image_path = args["image_path"]
    confidence = args.get("confidence", 0.25)
    save_result = args.get("save_result", True)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像不存在: {image_path}")

    # 加载模型
    model = _load_model("yolo11n")

    # 执行检测
    results = model(image_path, conf=confidence, verbose=False)

    # 解析结果
    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                cls_name = result.names[cls_id]
                conf = float(box.conf[0])

                # 只保留与洪水相关的类别
                flood_related = ["water", "flood", "river", "lake", "puddle"]
                if any(keyword in cls_name.lower() for keyword in flood_related):
                    detections.append({
                        "class": cls_name,
                        "confidence": round(conf, 4),
                        "bbox": box.xyxy[0].tolist()
                    })

    # 保存结果图像
    result_path = None
    if save_result and detections:
        result_path = os.path.join(
            RESULTS_DIR,
            f"flood_detect_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )
        results[0].save(result_path)

    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "task": "flood_detection",
            "image_path": image_path,
            "detection_count": len(detections),
            "detections": detections,
            "result_image": result_path,
            "device": _get_device(),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_detect_water(args: Dict[str, Any]) -> List[TextContent]:
    """检测水体"""
    # 检查依赖
    deps_error = _check_deps_response()
    if deps_error:
        return deps_error

    image_path = args["image_path"]
    confidence = args.get("confidence", 0.3)
    save_result = args.get("save_result", True)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像不存在: {image_path}")

    model = _load_model("yolo11n")
    results = model(image_path, conf=confidence, verbose=False)

    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                cls_name = result.names[cls_id]
                conf = float(box.conf[0])

                # 水体相关类别
                water_related = ["water", "river", "lake", "sea", "pond"]
                if any(keyword in cls_name.lower() for keyword in water_related):
                    detections.append({
                        "class": cls_name,
                        "confidence": round(conf, 4),
                        "bbox": box.xyxy[0].tolist()
                    })

    # 保存结果
    result_path = None
    if save_result and detections:
        result_path = os.path.join(
            RESULTS_DIR,
            f"water_detect_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )
        results[0].save(result_path)

    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "task": "water_body_detection",
            "image_path": image_path,
            "detection_count": len(detections),
            "detections": detections,
            "result_image": result_path,
            "device": _get_device(),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_detect_infrastructure(args: Dict[str, Any]) -> List[TextContent]:
    """检测水利基础设施"""
    # 检查依赖
    deps_error = _check_deps_response()
    if deps_error:
        return deps_error

    image_path = args["image_path"]
    confidence = args.get("confidence", 0.25)
    save_result = args.get("save_result", True)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像不存在: {image_path}")

    model = _load_model("yolo11n")
    results = model(image_path, conf=confidence, verbose=False)

    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                cls_name = result.names[cls_id]
                conf = float(box.conf[0])

                # 基础设施相关类别
                infra_related = ["bridge", "dam", "building", "house", "tower"]
                if any(keyword in cls_name.lower() for keyword in infra_related):
                    detections.append({
                        "class": cls_name,
                        "confidence": round(conf, 4),
                        "bbox": box.xyxy[0].tolist()
                    })

    # 保存结果
    result_path = None
    if save_result and detections:
        result_path = os.path.join(
            RESULTS_DIR,
            f"infra_detect_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )
        results[0].save(result_path)

    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "task": "infrastructure_detection",
            "image_path": image_path,
            "detection_count": len(detections),
            "detections": detections,
            "result_image": result_path,
            "device": _get_device(),
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_batch_detect(args: Dict[str, Any]) -> List[TextContent]:
    """批量检测"""
    # 检查依赖
    deps_error = _check_deps_response()
    if deps_error:
        return deps_error

    image_dir = args["image_dir"]
    task = args.get("task", "all")
    confidence = args.get("confidence", 0.25)

    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"目录不存在: {image_dir}")

    # 获取所有图像文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = [
        f for f in os.listdir(image_dir)
        if any(f.lower().endswith(ext) for ext in image_extensions)
    ]

    if not image_files:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": True,
                "task": "batch_detection",
                "image_dir": image_dir,
                "total_images": 0,
                "processed": 0,
                "message": "目录中没有图像文件"
            }, ensure_ascii=False)
        )]

    model = _load_model("yolo11n")

    results_summary = []
    for img_file in image_files[:10]:  # 限制最多处理10张
        img_path = os.path.join(image_dir, img_file)

        try:
            results = model(img_path, conf=confidence, verbose=False)

            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        cls_name = result.names[cls_id]
                        conf = float(box.conf[0])
                        detections.append({
                            "class": cls_name,
                            "confidence": round(conf, 4)
                        })

            results_summary.append({
                "filename": img_file,
                "detections_count": len(detections),
                "detections": detections
            })

        except Exception as e:
            results_summary.append({
                "filename": img_file,
                "error": str(e)
            })

    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "task": "batch_detection",
            "image_dir": image_dir,
            "total_images": len(image_files),
            "processed": len(results_summary),
            "device": _get_device(),
            "results": results_summary,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_model_info(args: Dict[str, Any]) -> List[TextContent]:
    """获取模型信息"""
    # 检查依赖
    if not _deps_available:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": f"依赖未安装: {_deps_error}",
                "install_command": "pip install ultralytics opencv-python numpy",
                "note": "请在系统 Python 环境中运行上述命令安装依赖"
            }, ensure_ascii=False, indent=2)
        )]

    try:
        import torch
        import ultralytics

        device = _get_device()

        # 尝试加载模型获取详细信息
        try:
            model = _load_model("yolo11n")
            model_info = {
                "model_name": "yolo11n",
                "model_loaded": True,
                "task": model.task if hasattr(model, 'task') else "detect"
            }
        except Exception as e:
            model_info = {
                "model_name": "yolo11n",
                "model_loaded": False,
                "error": str(e)
            }

        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": True,
                "pytorch_version": torch.__version__,
                "ultralytics_version": ultralytics.__version__,
                "cuda_available": torch.cuda.is_available(),
                "device": device,
                "model": model_info,
                "models_dir": os.path.abspath(MODELS_DIR),
                "datasets_dir": os.path.abspath(DATASETS_DIR),
                "results_dir": os.path.abspath(RESULTS_DIR)
            }, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }, ensure_ascii=False)
        )]


async def _handle_download_dataset(args: Dict[str, Any]) -> List[TextContent]:
    """下载测试数据集"""
    # 检查依赖
    if not _deps_available:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": f"依赖未安装: {_deps_error}",
                "install_command": "pip install opencv-python numpy",
                "note": "请在系统 Python 环境中运行上述命令安装依赖"
            }, ensure_ascii=False, indent=2)
        )]

    dataset_name = args.get("dataset_name", "flood_sample")

    _ensure_dirs()

    # 创建示例数据集目录
    dataset_dir = os.path.join(DATASETS_DIR, dataset_name)
    os.makedirs(dataset_dir, exist_ok=True)

    # 创建示例图像（使用 OpenCV 生成模拟图像）
    try:
        import numpy as np
        import cv2

        # 生成几张模拟的水利场景图像
        created_files = []
        for i in range(3):
            # 创建随机图像
            img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

            # 添加一些模拟的水体区域（蓝色）
            if i % 2 == 0:  # 模拟洪水场景
                cv2.rectangle(img, (100, 200), (400, 400), (200, 100, 50), -1)
                cv2.putText(img, "Flood Area", (150, 350),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            else:  # 模拟正常水体
                cv2.ellipse(img, (320, 300), (150, 100), 0, 0, 360, (255, 150, 50), -1)
                cv2.putText(img, "Water Body", (250, 310),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # 保存图像
            img_path = os.path.join(dataset_dir, f"sample_{i+1:03d}.jpg")
            cv2.imwrite(img_path, img)
            created_files.append(img_path)

        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": True,
                "dataset_name": dataset_name,
                "dataset_dir": os.path.abspath(dataset_dir),
                "created_files": created_files,
                "file_count": len(created_files),
                "note": "这是模拟数据集，用于测试 YOLO 检测功能。实际使用时请替换为真实水利图像。"
            }, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "note": "请确保已安装 opencv-python 和 numpy"
            }, ensure_ascii=False)
        )]


async def main():
    """启动 MCP Server（Windows 兼容版）"""
    _ensure_dirs()

    # Windows 环境设置
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        # 解决 OpenMP 冲突
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    from mcp.server.stdio import stdio_server as mcp_stdio_server

    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
