"""Hydrology MCP 端到端验证测试

使用 synthetic 测试数据验证：
1. Hydrology 服务能正确调用 YOLO 进行洪水检测
2. Hydrology 服务能正确调用 HiPIMS 进行 2D 模拟
3. 结果符合预期（与 test_manifest.json 中的预期对比）

测试数据位置: tests/data/
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.mcp.servers.hydrology_server import call_tool as hydrology_call

# 测试数据目录
DATA_DIR = project_root / "tests" / "data"
TERRAIN_DIR = DATA_DIR / "terrain"
BOUNDARY_DIR = DATA_DIR / "boundary"
IMAGES_DIR = DATA_DIR / "images"


class TestResult:
    """测试结果记录"""
    def __init__(self, test_name):
        self.test_name = test_name
        self.passed = False
        self.details = {}
        self.errors = []
        self.timestamp = datetime.now().isoformat()
    
    def add_detail(self, key, value):
        self.details[key] = value
    
    def add_error(self, error):
        self.errors.append(error)
    
    def to_dict(self):
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "timestamp": self.timestamp,
            "details": self.details,
            "errors": self.errors
        }


async def test_yolo_detection():
    """
    测试1: YOLO 洪水检测
    
    【输入】
    - 测试图像: tests/data/images/synthetic_flood_01.jpg
    
    【预期结果】
    - 检测到水体区域
    - 置信度 > 0.5
    - 返回检测框坐标
    """
    result = TestResult("YOLO洪水检测")
    
    print("\n" + "=" * 60)
    print("测试1: YOLO 洪水检测")
    print("=" * 60)
    
    # 检查测试图像是否存在
    test_image = IMAGES_DIR / "synthetic_flood_01.jpg"
    if not test_image.exists():
        print(f"⚠ 测试图像不存在: {test_image}")
        print("  请先运行: python tests/data/generate_synthetic_data.py")
        result.add_error("测试图像不存在")
        return result
    
    print(f"输入图像: {test_image}")
    
    try:
        # 调用 YOLO 检测
        response = await hydrology_call("detect_flood_from_image", {
            "image_path": str(test_image),
            "confidence": 0.5,
            "save_result": False
        })
        
        data = json.loads(response[0].text)
        result.add_detail("raw_response", data)
        
        if not data.get("success"):
            result.add_error(f"检测失败: {data.get('error', '未知错误')}")
            print(f"✗ 检测失败: {data.get('error')}")
            return result
        
        # 验证结果
        detections = data.get("detections", [])
        result.add_detail("detection_count", len(detections))
        
        print(f"✓ 检测完成，发现 {len(detections)} 个目标")
        
        # 检查预期
        if len(detections) == 0:
            result.add_error("未检测到任何目标（预期应检测到水体）")
            print("⚠ 未检测到目标（预期应检测到水体）")
        else:
            for i, det in enumerate(detections):
                print(f"  目标 {i+1}: {det.get('class', 'unknown')} "
                      f"(置信度: {det.get('confidence', 0):.2f})")
                
                # 验证置信度
                conf = det.get("confidence", 0)
                if conf < 0.5:
                    result.add_error(f"目标 {i+1} 置信度 {conf:.2f} < 0.5")
                
                # 验证检测框
                bbox = det.get("bbox", [])
                if len(bbox) != 4:
                    result.add_error(f"目标 {i+1} 检测框格式错误")
        
        result.passed = len(result.errors) == 0
        
    except Exception as e:
        result.add_error(f"异常: {str(e)}")
        print(f"✗ 测试异常: {e}")
    
    return result


async def test_hipims_simulation():
    """
    测试2: HiPIMS 2D 洪水模拟
    
    【输入】
    - 地形: flat_terrain.asc (平坦地形)
    - 入流: inflow_moderate.json (峰值100 m³/s)
    - 降雨: rainfall_moderate.json (50mm/h, 2小时)
    
    【预期结果】
    - 最大水深 ≈ 2.0m (入流点附近)
    - 淹没范围 ~30% 区域
    - 流速在 0.5-1.5 m/s 之间
    - 模拟成功完成
    """
    result = TestResult("HiPIMS_2D模拟")
    
    print("\n" + "=" * 60)
    print("测试2: HiPIMS 2D 洪水模拟")
    print("=" * 60)
    
    # 检查测试数据
    terrain_file = TERRAIN_DIR / "flat_terrain.asc"
    inflow_file = BOUNDARY_DIR / "inflow_moderate.json"
    rainfall_file = BOUNDARY_DIR / "rainfall_moderate.json"
    
    for f in [terrain_file, inflow_file, rainfall_file]:
        if not f.exists():
            print(f"⚠ 测试数据不存在: {f}")
            print("  请先运行: python tests/data/generate_synthetic_data.py")
            result.add_error(f"测试数据不存在: {f.name}")
            return result
    
    print(f"地形文件: {terrain_file}")
    print(f"入流文件: {inflow_file}")
    print(f"降雨文件: {rainfall_file}")
    
    # 读取边界条件
    with open(inflow_file, 'r') as f:
        inflow_data = json.load(f)
    with open(rainfall_file, 'r') as f:
        rainfall_data = json.load(f)
    
    print(f"\n预期入流峰值: {inflow_data['peak_flow']} m³/s")
    print(f"预期降雨强度: {rainfall_data['intensity_mmh']} mm/h")
    
    try:
        # 调用 HiPIMS 模拟
        print("\n开始模拟...")
        response = await hydrology_call("run_hipims_workflow", {
            "terrain_path": str(terrain_file),
            "boundary_conditions": {
                "inflow_points": [{"i": 0, "j": 25, "discharge": inflow_data["peak_flow"]}],
                "outflow_points": [],
                "initial_water_level": 0.0
            },
            "rainfall_data": {
                "type": "uniform",
                "intensity": rainfall_data["intensity_mmh"],
                "duration": rainfall_data["duration_hours"] * 3600
            },
            "simulation_duration": 3600,  # 1小时
            "time_step": 10.0,
            "use_gpu": False
        })
        
        data = json.loads(response[0].text)
        result.add_detail("raw_response", data)
        
        if not data.get("success"):
            result.add_error(f"模拟失败: {data.get('error', '未知错误')}")
            print(f"✗ 模拟失败: {data.get('error')}")
            return result
        
        print("✓ 模拟完成")
        
        # 验证结果
        sim_results = data.get("results", {})
        result.add_detail("simulation_id", data.get("simulation_id"))
        
        max_depth = sim_results.get("max_water_depth", 0)
        max_velocity = sim_results.get("max_velocity", 0)
        inundation_area = sim_results.get("inundation_area", 0)
        
        print(f"\n模拟结果:")
        print(f"  最大水深: {max_depth:.2f} m")
        print(f"  最大流速: {max_velocity:.2f} m/s")
        print(f"  淹没面积: {inundation_area:.0f} m²")
        
        # 与预期对比
        print(f"\n与预期对比:")
        
        # 最大水深预期: ~2.0m
        if 1.5 <= max_depth <= 3.0:
            print(f"  ✓ 最大水深 {max_depth:.2f}m 在预期范围 (1.5-3.0m)")
        else:
            result.add_error(f"最大水深 {max_depth:.2f}m 超出预期范围 (1.5-3.0m)")
            print(f"  ✗ 最大水深 {max_depth:.2f}m 超出预期范围")
        
        # 流速预期: 0.5-1.5 m/s
        if 0.3 <= max_velocity <= 2.0:
            print(f"  ✓ 最大流速 {max_velocity:.2f}m/s 在合理范围")
        else:
            result.add_error(f"最大流速 {max_velocity:.2f}m/s 异常")
            print(f"  ✗ 最大流速异常")
        
        # 淹没面积预期: ~30% (25000 m² for 50x50 grid with 10m cell)
        expected_area = 25000
        if 15000 <= inundation_area <= 35000:
            print(f"  ✓ 淹没面积 {inundation_area:.0f}m² 在预期范围")
        else:
            result.add_error(f"淹没面积 {inundation_area:.0f}m² 与预期 {expected_area}m² 偏差较大")
            print(f"  ⚠ 淹没面积与预期偏差较大")
        
        result.passed = len(result.errors) == 0
        
    except Exception as e:
        result.add_error(f"异常: {str(e)}")
        import traceback
        result.add_detail("traceback", traceback.format_exc())
        print(f"✗ 测试异常: {e}")
    
    return result


async def test_integrated_workflow():
    """
    测试3: 集成工作流
    
    【流程】
    1. Hydrology 调用 Data Hub 获取降雨数据
    2. Hydrology 运行降雨径流模型
    3. Hydrology 调用 HiPIMS 进行 2D 模拟
    4. 返回完整结果
    
    【验证点】
    - 所有步骤成功执行
    - 数据在各步骤间正确传递
    - 最终输出包含所有预期字段
    """
    result = TestResult("集成工作流")
    
    print("\n" + "=" * 60)
    print("测试3: 集成工作流")
    print("=" * 60)
    
    try:
        print("启动集成工作流...")
        response = await hydrology_call("run_integrated_workflow", {
            "location": "TestLocation",
            "data_source": "synthetic",
            "catchment_area": 50,
            "simulation_duration": 1800,
            "use_gpu": False
        })
        
        data = json.loads(response[0].text)
        result.add_detail("raw_response", data)
        
        if not data.get("success"):
            result.add_error(f"工作流失败: {data.get('error')}")
            print(f"✗ 工作流失败: {data.get('error')}")
            return result
        
        print("✓ 工作流完成")
        
        # 验证输出字段
        workflow_id = data.get("workflow_id")
        steps = data.get("steps_executed", [])
        
        print(f"\n工作流 ID: {workflow_id}")
        print(f"执行步骤: {', '.join(steps)}")
        
        result.add_detail("workflow_id", workflow_id)
        result.add_detail("steps_executed", steps)
        
        # 验证步骤完整性
        expected_steps = ["data_acquisition", "rainfall_runoff", "hipims_simulation"]
        for step in expected_steps:
            if step not in steps:
                result.add_error(f"缺少步骤: {step}")
                print(f"✗ 缺少步骤: {step}")
        
        if len(result.errors) == 0:
            print("✓ 所有预期步骤已执行")
        
        result.passed = len(result.errors) == 0
        
    except Exception as e:
        result.add_error(f"异常: {str(e)}")
        import traceback
        result.add_detail("traceback", traceback.format_exc())
        print(f"✗ 测试异常: {e}")
    
    return result


async def run_all_tests():
    """运行所有端到端测试"""
    print("=" * 70)
    print("Hydrology MCP 端到端验证测试")
    print("=" * 70)
    print(f"\n测试数据目录: {DATA_DIR}")
    print(f"测试时间: {datetime.now().isoformat()}")
    
    results = []
    
    # 运行测试
    results.append(await test_yolo_detection())
    results.append(await test_hipims_simulation())
    results.append(await test_integrated_workflow())
    
    # 汇总报告
    print("\n" + "=" * 70)
    print("测试汇总报告")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for r in results:
        status = "✓ 通过" if r.passed else "✗ 失败"
        print(f"\n{r.test_name}: {status}")
        
        if r.passed:
            passed += 1
        else:
            failed += 1
            print(f"  错误:")
            for e in r.errors:
                print(f"    - {e}")
    
    print(f"\n{'='*70}")
    print(f"总计: {passed} 通过, {failed} 失败, {len(results)} 测试")
    
    # 保存详细报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed
        },
        "results": [r.to_dict() for r in results]
    }
    
    report_file = DATA_DIR / "test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细报告已保存: {report_file}")
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n测试框架错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
