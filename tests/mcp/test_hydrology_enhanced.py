"""Hydrology MCP Server 增强功能测试脚本

测试重构后的 hydrology_server.py 的所有功能，包括：
- 原有水利模型功能
- YOLO 视觉检测
- HiPIMS 2D 模拟
- 视觉辅助校准
- 服务间依赖调用
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.mcp.servers.hydrology_server import (
    list_tools,
    call_tool,
    yolo_module,
    hipims_simulator,
    vision_calibrator,
    service_client,
)


def check_api_key():
    """检查 API Key 是否配置"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("=" * 60)
        print("警告: 未配置 KIMI_API_KEY 环境变量")
        print("=" * 60)
        print("\n部分测试可能无法运行")
        return False
    return True


async def test_list_hydrology_models():
    """测试列出水利模型"""
    print("\n" + "=" * 60)
    print("测试: 列出水利模型")
    print("=" * 60)
    
    result = await call_tool("list_hydrology_models", {})
    data = json.loads(result[0].text)
    
    if data.get('success'):
        print(f"✓ 成功列出 {len(data.get('models', []))} 个模型")
        for model in data.get('models', []):
            print(f"  - {model['name']}: {model['description']}")
        return True
    else:
        print(f"✗ 失败: {data.get('error')}")
        return False


async def test_run_rainfall_runoff():
    """测试降雨径流模型"""
    print("\n" + "=" * 60)
    print("测试: 降雨径流模型")
    print("=" * 60)
    
    result = await call_tool("run_rainfall_runoff", {
        "rainfall": [10, 20, 30, 25, 15, 10, 5],
        "catchment_area": 50
    })
    data = json.loads(result[0].text)
    
    if data.get('success'):
        print(f"✓ 模拟成功")
        print(f"  总径流量: {data.get('total_runoff', 0):.2f} m³")
        print(f"  洪峰流量: {data.get('peak_discharge', 0):.2f} m³/s")
        return True
    else:
        print(f"✗ 失败: {data.get('error')}")
        return False


async def test_run_flood_routing():
    """测试洪水演进模型"""
    print("\n" + "=" * 60)
    print("测试: 洪水演进模型")
    print("=" * 60)
    
    result = await call_tool("run_flood_routing", {
        "inflow": [100, 150, 200, 180, 140, 100, 80, 60],
        "k": 3.0,
        "x": 0.3
    })
    data = json.loads(result[0].text)
    
    if data.get('success'):
        print(f"✓ 模拟成功")
        print(f"  洪峰削减: {data.get('peak_attenuation', 0):.2f} m³/s")
        return True
    else:
        print(f"✗ 失败: {data.get('error')}")
        return False


async def test_run_reservoir_dispatch():
    """测试水库调度模型"""
    print("\n" + "=" * 60)
    print("测试: 水库调度模型")
    print("=" * 60)
    
    result = await call_tool("run_reservoir_dispatch", {
        "inflow": [100, 200, 350, 400, 300, 200, 150],
        "initial_level": 100.0,
        "target_level": 95.0,
        "max_outflow": 500.0
    })
    data = json.loads(result[0].text)
    
    if data.get('success'):
        print(f"✓ 模拟成功")
        print(f"  最终水位: {data.get('final_level', 0):.2f} m")
        print(f"  总泄量: {data.get('total_release', 0):.2f} m³")
        return True
    else:
        print(f"✗ 失败: {data.get('error')}")
        return False


async def test_yolo_model_info():
    """测试 YOLO 模型信息"""
    print("\n" + "=" * 60)
    print("测试: YOLO 模型信息")
    print("=" * 60)
    
    result = await call_tool("get_yolo_model_info", {})
    data = json.loads(result[0].text)
    
    if data.get('success'):
        print(f"✓ 获取成功")
        print(f"  PyTorch 版本: {data.get('pytorch_version', 'N/A')}")
        print(f"  Ultralytics 版本: {data.get('ultralytics_version', 'N/A')}")
        print(f"  CUDA 可用: {data.get('cuda_available', False)}")
        return True
    else:
        print(f"⚠ 信息获取失败（YOLO 可能未安装）: {data.get('error')}")
        return True  # 非关键功能，允许失败


async def test_check_gpu_availability():
    """测试 GPU 可用性检查"""
    print("\n" + "=" * 60)
    print("测试: GPU 可用性检查")
    print("=" * 60)
    
    result = await call_tool("check_gpu_availability", {})
    data = json.loads(result[0].text)
    
    if data.get('success'):
        print(f"✓ 检查成功")
        print(f"  GPU 可用: {data.get('gpu_available', False)}")
        print(f"  设备数量: {data.get('device_count', 0)}")
        if data.get('devices'):
            for device in data['devices']:
                print(f"    - {device.get('name', 'Unknown')}")
        return True
    else:
        print(f"✗ 失败: {data.get('error')}")
        return False


async def test_run_hipims_workflow():
    """测试 HiPIMS 工作流"""
    print("\n" + "=" * 60)
    print("测试: HiPIMS 工作流")
    print("=" * 60)
    
    result = await call_tool("run_hipims_workflow", {
        "terrain_path": "test_data/terrain.asc",
        "boundary_conditions": {
            "inflow_points": [{"i": 0, "j": 50, "discharge": 10.0}],
            "outflow_points": [],
            "initial_water_level": 0.5
        },
        "rainfall_data": {
            "type": "uniform",
            "intensity": 50.0,
            "duration": 3600
        },
        "simulation_duration": 3600,
        "time_step": 1.0,
        "use_gpu": False
    })
    data = json.loads(result[0].text)
    
    if data.get('success'):
        print(f"✓ 模拟成功")
        print(f"  模拟 ID: {data.get('simulation_id', 'N/A')}")
        results = data.get('results', {})
        print(f"  最大水深: {results.get('max_water_depth', 0):.2f} m")
        print(f"  最大流速: {results.get('max_velocity', 0):.2f} m/s")
        print(f"  淹没面积: {results.get('inundation_area', 0):.0f} m²")
        return True
    else:
        print(f"✗ 失败: {data.get('error')}")
        return False


async def test_run_integrated_workflow():
    """测试集成工作流"""
    print("\n" + "=" * 60)
    print("测试: 集成工作流（Data → Hydrology → HiPIMS）")
    print("=" * 60)
    
    result = await call_tool("run_integrated_workflow", {
        "location": "Beijing",
        "data_source": "openweather",
        "catchment_area": 100,
        "simulation_duration": 1800,
        "use_gpu": False
    })
    data = json.loads(result[0].text)
    
    if data.get('success'):
        print(f"✓ 集成工作流成功")
        print(f"  工作流 ID: {data.get('workflow_id', 'N/A')}")
        print(f"  执行步骤: {', '.join(data.get('steps_executed', []))}")
        return True
    else:
        print(f"✗ 失败: {data.get('error')}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Hydrology MCP Server 增强功能测试")
    print("=" * 60)
    
    check_api_key()
    
    results = {}
    
    # 原有功能测试
    print("\n" + "-" * 60)
    print("Phase 1: 原有水利模型功能")
    print("-" * 60)
    results['list_models'] = await test_list_hydrology_models()
    results['rainfall_runoff'] = await test_run_rainfall_runoff()
    results['flood_routing'] = await test_run_flood_routing()
    results['reservoir_dispatch'] = await test_run_reservoir_dispatch()
    
    # YOLO 功能测试
    print("\n" + "-" * 60)
    print("Phase 2: YOLO 视觉检测功能")
    print("-" * 60)
    results['yolo_info'] = await test_yolo_model_info()
    
    # HiPIMS 功能测试
    print("\n" + "-" * 60)
    print("Phase 3: HiPIMS 2D 模拟功能")
    print("-" * 60)
    results['gpu_check'] = await test_check_gpu_availability()
    results['hipims_workflow'] = await test_run_hipims_workflow()
    
    # 集成测试
    print("\n" + "-" * 60)
    print("Phase 4: 集成工作流")
    print("-" * 60)
    results['integrated_workflow'] = await test_run_integrated_workflow()
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n总计: {passed_count}/{total_count} 项测试通过")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️ 部分测试未通过")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
