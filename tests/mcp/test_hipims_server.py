"""HiPIMS MCP Server 端到端测试脚本

测试 HiPIMS MCP Server 的各项功能，包括：
- check_gpu_availability: 检查 GPU 可用性
- prepare_simulation_data: 准备模拟数据
- run_2d_simulation: 运行 2D 模拟
- get_simulation_status: 获取模拟状态
- list_simulation_results: 列出历史结果

包含完整的模拟工作流测试。
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.mcp.servers.hipims_server import (
    HipimsSimulator,
    SimulationConfig,
    SimulationStatus,
    _handle_check_gpu_availability,
    _handle_prepare_simulation_data,
    _handle_run_2d_simulation,
    _handle_get_simulation_status,
    _handle_list_simulation_results,
)


def check_api_key():
    """检查 API Key 是否配置"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("=" * 60)
        print("错误: 未配置 KIMI_API_KEY 环境变量")
        print("=" * 60)
        print("\n请先设置环境变量:")
        print('  Windows PowerShell: $env:KIMI_API_KEY="your-api-key"')
        print("  Windows CMD: set KIMI_API_KEY=your-api-key")
        print("  Linux/Mac: export KIMI_API_KEY=your-api-key")
        print("\n然后重新运行测试。")
        sys.exit(1)
    return api_key


async def test_check_gpu_availability():
    """测试 1: 检查 GPU 可用性"""
    print("\n" + "=" * 60)
    print("测试 1: 检查 GPU 可用性")
    print("=" * 60)

    result = await _handle_check_gpu_availability({})
    data = json.loads(result[0].text)

    print(f"成功: {data.get('success')}")
    print(f"GPU 可用: {data.get('gpu_available')}")
    print(f"设备数量: {data.get('device_count', 0)}")

    if data.get('devices'):
        print("\nGPU 设备信息:")
        for device in data['devices']:
            print(f"  设备 {device.get('id')}: {device.get('name')}")
            mem_gb = device.get('memory_total', 0) / (1024**3)
            print(f"    显存: {mem_gb:.2f} GB")

    if data.get('cuda_version'):
        print(f"\nCUDA 版本: {data.get('cuda_version')}")

    print(f"\n提示: {data.get('note')}")

    return data.get('success', False)


async def test_prepare_simulation_data():
    """测试 2: 准备模拟数据"""
    print("\n" + "=" * 60)
    print("测试 2: 准备模拟数据")
    print("=" * 60)

    # 测试数据配置
    terrain_path = "resources/data/terrain/demo_terrain.tif"
    boundary_conditions = {
        "inflow_points": [
            {"i": 10, "j": 50, "discharge": 50.0},
            {"i": 15, "j": 45, "discharge": 30.0}
        ],
        "outflow_points": [
            {"i": 90, "j": 50}
        ],
        "wall_boundaries": [],
        "initial_water_level": 0.5
    }
    rainfall_data = {
        "type": "uniform",
        "intensity": 25.0,  # mm/h
        "duration": 3600,   # 1小时
        "pattern": "constant"
    }

    print(f"地形路径: {terrain_path}")
    print(f"入流点数量: {len(boundary_conditions['inflow_points'])}")
    print(f"出流点数量: {len(boundary_conditions['outflow_points'])}")
    print(f"初始水位: {boundary_conditions['initial_water_level']} m")
    print(f"降雨强度: {rainfall_data['intensity']} mm/h")
    print(f"降雨时长: {rainfall_data['duration']} 秒")

    result = await _handle_prepare_simulation_data({
        "terrain_path": terrain_path,
        "boundary_conditions": boundary_conditions,
        "rainfall_data": rainfall_data
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"\n✓ 数据准备成功")
        result_data = data.get('data', {})
        print(f"  模拟 ID: {result_data.get('simulation_id')}")
        print(f"  状态: {result_data.get('status')}")
        print(f"  地形有效: {result_data.get('terrain_valid')}")
        print(f"  准备时间: {result_data.get('prepared_at')}")

        # 返回 simulation_id 供后续测试使用
        return True, result_data.get('simulation_id')
    else:
        print(f"\n✗ 数据准备失败: {data.get('error')}")
        return False, None


async def test_run_2d_simulation():
    """测试 3: 运行 2D 模拟"""
    print("\n" + "=" * 60)
    print("测试 3: 运行 2D 模拟")
    print("=" * 60)

    # 模拟配置
    terrain_path = "resources/data/terrain/demo_terrain.tif"
    boundary_conditions = {
        "inflow_points": [
            {"i": 10, "j": 50, "discharge": 50.0}
        ],
        "initial_water_level": 0.5
    }
    rainfall_data = {
        "type": "uniform",
        "intensity": 25.0,
        "duration": 1800  # 30分钟
    }

    print("模拟配置:")
    print(f"  地形: {terrain_path}")
    print(f"  模拟时长: 1800 秒 (30分钟)")
    print(f"  时间步长: 1.0 秒")
    print(f"  输出间隔: 300 秒 (5分钟)")
    print(f"  使用 GPU: True")
    print(f"  GPU 设备: 0")

    result = await _handle_run_2d_simulation({
        "terrain_path": terrain_path,
        "boundary_conditions": boundary_conditions,
        "rainfall_data": rainfall_data,
        "simulation_duration": 1800.0,
        "time_step": 1.0,
        "output_interval": 300.0,
        "use_gpu": True,
        "gpu_device": 0
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"\n✓ 模拟运行成功")
        print(f"  模拟 ID: {data.get('simulation_id')}")
        print(f"  状态: {data.get('status')}")
        print(f"  消息: {data.get('message')}")

        # 打印结果摘要
        results = data.get('results', {})
        print(f"\n  模拟结果:")
        print(f"    最大水深: {results.get('max_water_depth', 0):.4f} m")
        print(f"    最大流速: {results.get('max_velocity', 0):.4f} m/s")
        print(f"    淹没面积: {results.get('inundation_area', 0):.2f} m²")

        # 打印淹没范围分级
        extent = results.get('inundation_extent', {})
        if extent and 'levels' in extent:
            print(f"\n  淹没范围分级:")
            for level_name, level_info in extent['levels'].items():
                depth_range = level_info.get('depth_range', [0, 0])
                area = level_info.get('area', 0)
                percentage = level_info.get('percentage', 0)
                print(f"    {level_name}: {area:.2f} m² ({percentage:.2f}%) - 水深 {depth_range[0]}~{depth_range[1]} m")

        # 打印时间信息
        timing = data.get('timing', {})
        if timing:
            print(f"\n  时间信息:")
            print(f"    开始时间: {timing.get('start_time')}")
            print(f"    结束时间: {timing.get('end_time')}")

        return True, data.get('simulation_id')
    else:
        print(f"\n✗ 模拟运行失败: {data.get('message')}")
        return False, None


async def test_get_simulation_status(simulation_id: str):
    """测试 4: 获取模拟状态"""
    print("\n" + "=" * 60)
    print("测试 4: 获取模拟状态")
    print("=" * 60)

    print(f"查询模拟 ID: {simulation_id}")

    result = await _handle_get_simulation_status({
        "simulation_id": simulation_id
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"\n✓ 状态查询成功")
        print(f"  模拟 ID: {data.get('simulation_id')}")
        print(f"  状态: {data.get('status')}")
        print(f"  进度: {data.get('progress', 0):.1f}%")
        print(f"  开始时间: {data.get('start_time')}")
        print(f"  结束时间: {data.get('end_time')}")

        # 打印结果摘要
        summary = data.get('summary', {})
        if summary:
            print(f"\n  结果摘要:")
            print(f"    最大水深: {summary.get('max_water_depth', 0):.4f} m")
            print(f"    最大流速: {summary.get('max_velocity', 0):.4f} m/s")
            print(f"    淹没面积: {summary.get('inundation_area', 0):.2f} m²")

        return True
    else:
        print(f"\n✗ 状态查询失败: {data.get('error')}")
        return False


async def test_list_simulation_results():
    """测试 5: 列出历史模拟结果"""
    print("\n" + "=" * 60)
    print("测试 5: 列出历史模拟结果")
    print("=" * 60)

    result = await _handle_list_simulation_results({
        "limit": 5
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"✓ 结果列表获取成功")
        print(f"  总数: {data.get('total', 0)}")
        print(f"  限制: {data.get('limit', 0)}")

        results = data.get('results', [])
        if results:
            print(f"\n  最近 {len(results)} 条模拟记录:")
            for i, sim in enumerate(results, 1):
                print(f"\n  [{i}] 模拟 ID: {sim.get('simulation_id')}")
                print(f"      状态: {sim.get('status')}")
                print(f"      进度: {sim.get('progress', 0):.1f}%")
                print(f"      最大水深: {sim.get('max_water_depth', 0):.4f} m")
                print(f"      淹没面积: {sim.get('inundation_area', 0):.2f} m²")
                print(f"      开始时间: {sim.get('start_time')}")
        else:
            print("\n  暂无模拟记录")

        return True
    else:
        print(f"✗ 结果列表获取失败")
        return False


async def test_full_simulation_workflow():
    """测试 6: 完整模拟工作流"""
    print("\n" + "=" * 60)
    print("测试 6: 完整模拟工作流")
    print("=" * 60)

    print("执行完整工作流: GPU检查 -> 数据准备 -> 运行模拟 -> 查询状态 -> 列出结果")

    # 步骤 1: 检查 GPU
    print("\n[步骤 1/5] 检查 GPU 可用性...")
    gpu_result = await _handle_check_gpu_availability({})
    gpu_data = json.loads(gpu_result[0].text)
    if gpu_data.get('success'):
        print(f"  ✓ GPU 检查完成，可用: {gpu_data.get('gpu_available')}")
    else:
        print(f"  ✗ GPU 检查失败")
        return False

    # 步骤 2: 准备数据
    print("\n[步骤 2/5] 准备模拟数据...")
    prep_result = await _handle_prepare_simulation_data({
        "terrain_path": "resources/data/terrain/demo_terrain.tif",
        "boundary_conditions": {
            "inflow_points": [{"i": 10, "j": 50, "discharge": 50.0}],
            "initial_water_level": 0.3
        },
        "rainfall_data": {
            "type": "uniform",
            "intensity": 20.0,
            "duration": 1200
        }
    })
    prep_data = json.loads(prep_result[0].text)
    if prep_data.get('success'):
        simulation_id = prep_data['data']['simulation_id']
        print(f"  ✓ 数据准备完成，模拟 ID: {simulation_id}")
    else:
        print(f"  ✗ 数据准备失败")
        return False

    # 步骤 3: 运行模拟（使用较短的时长以便快速测试）
    print("\n[步骤 3/5] 运行 2D 模拟...")
    sim_result = await _handle_run_2d_simulation({
        "terrain_path": "resources/data/terrain/demo_terrain.tif",
        "boundary_conditions": {
            "inflow_points": [{"i": 10, "j": 50, "discharge": 50.0}],
            "initial_water_level": 0.3
        },
        "rainfall_data": {
            "type": "uniform",
            "intensity": 20.0,
            "duration": 1200
        },
        "simulation_duration": 1200.0,
        "time_step": 1.0,
        "output_interval": 300.0,
        "use_gpu": True,
        "gpu_device": 0
    })
    sim_data = json.loads(sim_result[0].text)
    if sim_data.get('success'):
        simulation_id = sim_data.get('simulation_id')
        print(f"  ✓ 模拟运行完成，ID: {simulation_id}")
        results = sim_data.get('results', {})
        print(f"    最大水深: {results.get('max_water_depth', 0):.4f} m")
        print(f"    淹没面积: {results.get('inundation_area', 0):.2f} m²")
    else:
        print(f"  ✗ 模拟运行失败: {sim_data.get('message')}")
        return False

    # 步骤 4: 查询状态
    print("\n[步骤 4/5] 查询模拟状态...")
    status_result = await _handle_get_simulation_status({
        "simulation_id": simulation_id
    })
    status_data = json.loads(status_result[0].text)
    if status_data.get('success'):
        print(f"  ✓ 状态查询完成")
        print(f"    状态: {status_data.get('status')}")
        print(f"    进度: {status_data.get('progress', 0):.1f}%")
    else:
        print(f"  ✗ 状态查询失败")
        return False

    # 步骤 5: 列出结果
    print("\n[步骤 5/5] 列出历史模拟结果...")
    list_result = await _handle_list_simulation_results({"limit": 5})
    list_data = json.loads(list_result[0].text)
    if list_data.get('success'):
        print(f"  ✓ 结果列表获取完成")
        print(f"    共 {list_data.get('total', 0)} 条记录")
    else:
        print(f"  ✗ 结果列表获取失败")
        return False

    print("\n" + "=" * 60)
    print("✓ 完整工作流测试通过！")
    print("=" * 60)

    return True


async def test_edge_cases():
    """测试 7: 边界情况处理"""
    print("\n" + "=" * 60)
    print("测试 7: 边界情况处理")
    print("=" * 60)

    all_passed = True

    # 测试 7.1: 查询不存在的模拟 ID
    print("\n[测试 7.1] 查询不存在的模拟 ID...")
    result = await _handle_get_simulation_status({
        "simulation_id": "NON_EXISTENT_ID_12345"
    })
    data = json.loads(result[0].text)
    if not data.get('success') and '未找到' in data.get('error', ''):
        print(f"  ✓ 正确处理不存在的 ID")
    else:
        print(f"  ✗ 未正确处理不存在的 ID")
        all_passed = False

    # 测试 7.2: 无效的地形路径
    print("\n[测试 7.2] 无效的地形路径...")
    result = await _handle_prepare_simulation_data({
        "terrain_path": "/invalid/path/to/terrain.tif",
        "boundary_conditions": {
            "inflow_points": [{"i": 10, "j": 50, "discharge": 50.0}]
        }
    })
    data = json.loads(result[0].text)
    if data.get('success'):
        # 即使地形无效，也应该返回 simulation_id
        print(f"  ✓ 处理无效地形路径（terrain_valid: {data['data'].get('terrain_valid')}）")
    else:
        print(f"  ✗ 处理失败")
        all_passed = False

    # 测试 7.3: 空边界条件
    print("\n[测试 7.3] 空边界条件...")
    result = await _handle_prepare_simulation_data({
        "terrain_path": "resources/data/terrain/demo_terrain.tif",
        "boundary_conditions": {}
    })
    data = json.loads(result[0].text)
    if data.get('success'):
        print(f"  ✓ 处理空边界条件")
    else:
        print(f"  ✗ 处理失败")
        all_passed = False

    # 测试 7.4: 无降雨数据
    print("\n[测试 7.4] 无降雨数据...")
    result = await _handle_prepare_simulation_data({
        "terrain_path": "resources/data/terrain/demo_terrain.tif",
        "boundary_conditions": {
            "inflow_points": [{"i": 10, "j": 50, "discharge": 50.0}]
        }
        # 不传入 rainfall_data
    })
    data = json.loads(result[0].text)
    if data.get('success') and data['data'].get('rainfall_data') is None:
        print(f"  ✓ 正确处理无降雨数据")
    else:
        print(f"  ✗ 未正确处理无降雨数据")
        all_passed = False

    return all_passed


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("HiPIMS MCP Server 端到端测试")
    print("=" * 60)
    print("\n测试内容:")
    print("  1. 检查 GPU 可用性")
    print("  2. 准备模拟数据")
    print("  3. 运行 2D 模拟")
    print("  4. 获取模拟状态")
    print("  5. 列出历史模拟结果")
    print("  6. 完整模拟工作流")
    print("  7. 边界情况处理")
    print("=" * 60)

    # 检查 API Key
    check_api_key()

    results = {}

    # 运行测试
    results['check_gpu_availability'] = await test_check_gpu_availability()

    prep_result, simulation_id = await test_prepare_simulation_data()
    results['prepare_simulation_data'] = prep_result

    sim_result, sim_id = await test_run_2d_simulation()
    results['run_2d_simulation'] = sim_result

    if sim_id:
        results['get_simulation_status'] = await test_get_simulation_status(sim_id)
    else:
        results['get_simulation_status'] = False

    results['list_simulation_results'] = await test_list_simulation_results()

    results['full_simulation_workflow'] = await test_full_simulation_workflow()

    results['edge_cases'] = await test_edge_cases()

    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    test_names = {
        'check_gpu_availability': '检查 GPU 可用性',
        'prepare_simulation_data': '准备模拟数据',
        'run_2d_simulation': '运行 2D 模拟',
        'get_simulation_status': '获取模拟状态',
        'list_simulation_results': '列出历史结果',
        'full_simulation_workflow': '完整模拟工作流',
        'edge_cases': '边界情况处理'
    }

    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        display_name = test_names.get(test_name, test_name)
        print(f"  {display_name}: {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    print(f"\n总计: {passed_count}/{total_count} 项测试通过")

    if passed_count == total_count:
        print("\n🎉 所有测试通过！HiPIMS MCP Server 工作正常。")
        return 0
    else:
        print(f"\n⚠️ {total_count - passed_count} 项测试未通过")
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
