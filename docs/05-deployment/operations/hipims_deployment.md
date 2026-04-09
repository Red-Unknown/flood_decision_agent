# HiPIMS 部署与使用指南

## 简介

**HiPIMS** (High-Performance Integrated Hydrodynamic Modelling System) 是一个高性能集成水动力模拟系统，专为洪水模拟和水动力分析设计。

### 核心特性

- **GPU 加速计算**：基于 CUDA 技术，利用 NVIDIA GPU 实现大规模并行计算
- **2D 浅水方程求解**：完整求解 2D Saint-Venant 方程组
- **高分辨率模拟**：支持米级甚至亚米级空间分辨率的洪水演进模拟
- **实时降雨驱动**：可接入实时降雨数据进行动态洪水预报
- **多种边界条件**：支持入流、出流、固壁等多种边界条件类型

### 应用场景

- 城市内涝模拟与风险评估
- 河流洪水演进预测
- 水库溃坝情景分析
- 气候变化情景下的洪水风险研究

---

## Windows 部署步骤

### 1. 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10/11 64位 | Windows 11 64位 |
| 内存 | 8 GB | 32 GB 或更高 |
| 存储 | 10 GB 可用空间 | SSD，50 GB 可用空间 |
| GPU | NVIDIA GTX 1060 | NVIDIA RTX 3080 或更高 |
| CUDA | 11.0+ | 12.0+ |

### 2. 安装 NVIDIA 驱动和 CUDA

#### 2.1 安装 NVIDIA 显卡驱动

1. 访问 [NVIDIA 驱动下载页面](https://www.nvidia.com/Download/index.aspx)
2. 选择您的显卡型号和操作系统
3. 下载并安装最新驱动

#### 2.2 安装 CUDA Toolkit

```powershell
# 方法1：使用网络安装程序
# 下载地址：https://developer.nvidia.com/cuda-downloads
# 选择 Windows -> x86_64 -> 10/11 -> exe(network)

# 方法2：使用 conda 安装（推荐）
conda install -c nvidia cuda-toolkit=12.1
```

验证 CUDA 安装：
```powershell
nvcc --version
```

### 3. 安装 Python 依赖

```powershell
# 激活 conda 环境
conda activate intelligent_decision

# 安装 PyTorch（带 CUDA 支持）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 或安装 CuPy（HiPIMS 原生支持的 GPU 库）
pip install cupy-cuda12x

# 安装其他依赖
pip install numpy scipy matplotlib rasterio
```

### 4. 验证 GPU 可用性

```python
# test_gpu.py
import torch

print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU 数量: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
```

运行测试：
```powershell
python test_gpu.py
```

---

## GPU 配置说明

### GPU 设备选择

在运行模拟时，可以通过 `gpu_device` 参数指定使用的 GPU：

```json
{
  "use_gpu": true,
  "gpu_device": 0  // 使用第 0 块 GPU
}
```

### 多 GPU 配置

如果系统有多个 GPU，可以并行运行多个模拟任务：

```python
# 任务1使用 GPU 0
simulation_1 = {
    "use_gpu": true,
    "gpu_device": 0
}

# 任务2使用 GPU 1
simulation_2 = {
    "use_gpu": true,
    "gpu_device": 1
}
```

### 显存优化建议

| 网格尺寸 | 估算显存 | 适用 GPU |
|---------|---------|---------|
| 100×100 | ~500 MB | GTX 1060 6GB |
| 500×500 | ~2 GB | RTX 2060 6GB |
| 1000×1000 | ~8 GB | RTX 3070 8GB |
| 2000×2000 | ~32 GB | RTX 4090 24GB / A100 |

### 性能调优

1. **时间步长选择**：较小的时间步长提高稳定性但降低速度
2. **输出频率**：降低输出频率减少 I/O 开销
3. **网格分辨率**：根据研究区域大小选择合适的分辨率

---

## MCP 接口使用示例

### 1. 检查 GPU 可用性

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def check_gpu():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.hipims_server"],
        env={"PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "check_gpu_availability",
                {}
            )
            print(result)

asyncio.run(check_gpu())
```

### 2. 准备模拟数据

```python
async def prepare_simulation():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "prepare_simulation_data",
                {
                    "terrain_path": "resources/data/terrain/demo_terrain.tif",
                    "boundary_conditions": {
                        "inflow_points": [
                            {"i": 10, "j": 50, "discharge": 50.0}
                        ],
                        "outflow_points": [
                            {"i": 90, "j": 50}
                        ],
                        "initial_water_level": 0.5
                    },
                    "rainfall_data": {
                        "type": "uniform",
                        "intensity": 25.0,  # mm/h
                        "duration": 3600,   # 1小时
                        "pattern": "constant"
                    }
                }
            )
            print(result)
```

### 3. 运行 2D 模拟

```python
async def run_simulation():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "run_2d_simulation",
                {
                    "terrain_path": "resources/data/terrain/demo_terrain.tif",
                    "boundary_conditions": {
                        "inflow_points": [
                            {"i": 10, "j": 50, "discharge": 50.0}
                        ],
                        "initial_water_level": 0.5
                    },
                    "rainfall_data": {
                        "type": "uniform",
                        "intensity": 25.0,
                        "duration": 3600,
                        "pattern": "constant"
                    },
                    "simulation_duration": 7200,  # 2小时
                    "time_step": 1.0,
                    "output_interval": 300,       # 每5分钟输出
                    "use_gpu": True,
                    "gpu_device": 0
                }
            )
            print(result)
```

### 4. 查询模拟状态

```python
async def check_status(simulation_id: str):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "get_simulation_status",
                {"simulation_id": simulation_id}
            )
            print(result)
```

### 5. 列出历史结果

```python
async def list_results():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "list_simulation_results",
                {"limit": 10}
            )
            print(result)
```

---

## 完整工作流示例

```python
"""
HiPIMS 完整模拟工作流
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def full_workflow():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.hipims_server"],
        env={"PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 步骤1: 检查 GPU
            print("步骤1: 检查 GPU 可用性...")
            gpu_result = await session.call_tool(
                "check_gpu_availability", {}
            )
            print(gpu_result)
            
            # 步骤2: 准备数据
            print("\n步骤2: 准备模拟数据...")
            prep_result = await session.call_tool(
                "prepare_simulation_data",
                {
                    "terrain_path": "resources/data/terrain/demo.tif",
                    "boundary_conditions": {
                        "inflow_points": [{"i": 10, "j": 50, "discharge": 50.0}],
                        "initial_water_level": 0.5
                    },
                    "rainfall_data": {
                        "type": "uniform",
                        "intensity": 25.0,
                        "duration": 3600
                    }
                }
            )
            print(prep_result)
            
            # 步骤3: 运行模拟
            print("\n步骤3: 运行 2D 模拟...")
            sim_result = await session.call_tool(
                "run_2d_simulation",
                {
                    "terrain_path": "resources/data/terrain/demo.tif",
                    "boundary_conditions": {
                        "inflow_points": [{"i": 10, "j": 50, "discharge": 50.0}],
                        "initial_water_level": 0.5
                    },
                    "rainfall_data": {
                        "type": "uniform",
                        "intensity": 25.0,
                        "duration": 3600
                    },
                    "simulation_duration": 3600,
                    "use_gpu": True
                }
            )
            print(sim_result)
            
            # 步骤4: 查询结果
            print("\n步骤4: 查询模拟结果...")
            sim_id = sim_result.content[0].text  # 解析获取 simulation_id
            status_result = await session.call_tool(
                "get_simulation_status",
                {"simulation_id": sim_id}
            )
            print(status_result)

if __name__ == "__main__":
    asyncio.run(full_workflow())
```

---

## 故障排除

### 常见问题

#### 1. CUDA 未找到

**症状**：`CUDA not available`

**解决方案**：
```powershell
# 检查 NVIDIA 驱动
nvidia-smi

# 重新安装 PyTorch CUDA 版本
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

#### 2. 显存不足

**症状**：`CUDA out of memory`

**解决方案**：
- 减小网格尺寸
- 减少模拟时长
- 使用更高显存的 GPU
- 关闭其他占用显存的程序

#### 3. 模拟发散

**症状**：水位或流速异常增大

**解决方案**：
- 减小时间步长
- 检查边界条件设置
- 验证地形数据质量

---

## 参考资料

- [HiPIMS 官方文档](https://www.hipims.org/)
- [CUDA 编程指南](https://docs.nvidia.com/cuda/)
- [PyTorch CUDA 文档](https://pytorch.org/docs/stable/cuda.html)
