# YOLO Vision MCP Server 脚本

本目录包含用于运行和测试 YOLO Vision MCP Server 的独立脚本。

## 文件说明

| 文件 | 用途 |
|------|------|
| `run_yolo_mcp_server.py` | 启动 YOLO Vision MCP Server（自动检查/安装依赖） |
| `test_yolo_vision.py` | 运行 YOLO 视觉检测测试（生成测试数据集并检测） |
| `install_yolo_deps.ps1` | PowerShell 脚本，手动安装 YOLO 依赖 |

## 快速开始

### 1. 运行 YOLO 视觉测试

```bash
python scripts/test_yolo_vision.py
```

此脚本会：
1. 自动检查并安装 YOLO 依赖（ultralytics, opencv-python, numpy）
2. 生成 5 张测试图像（模拟洪水、水体、基础设施场景）
3. 下载 YOLO11n 模型（如果未下载）
4. 运行检测并输出结果

### 2. 启动 YOLO MCP Server

```bash
python scripts/run_yolo_mcp_server.py
```

此脚本会：
1. 自动检查并安装 MCP 和 YOLO 依赖
2. 启动 YOLO Vision MCP Server
3. 等待 MCP 客户端连接

## 依赖说明

YOLO Vision 功能是可选的，主要依赖：
- `ultralytics` - YOLO 模型框架
- `opencv-python` - 图像处理
- `numpy` - 数值计算
- `mcp` - MCP 协议支持

这些依赖可以通过以下方式安装：

```bash
# 方式1：使用测试脚本（推荐）
python scripts/test_yolo_vision.py

# 方式2：使用 PowerShell 脚本
.\scripts\install_yolo_deps.ps1

# 方式3：手动安装
pip install ultralytics opencv-python numpy mcp
```

## 测试数据集

测试脚本会在 `datasets/flood_sample/` 目录下生成模拟图像：
- `sample_001_flood.jpg` - 洪水场景
- `sample_002_water.jpg` - 正常水体
- `sample_003_infrastructure.jpg` - 水利基础设施
- `sample_004_flood.jpg` - 洪水场景
- `sample_005_water.jpg` - 正常水体

## 模型文件

YOLO 模型会自动下载到 `models/` 目录：
- `yolo11n.pt` - YOLO11n 轻量级模型（约 5MB）

## 检测结果

检测结果保存在 `results/yolo/` 目录下。
