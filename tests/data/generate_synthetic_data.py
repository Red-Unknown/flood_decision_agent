"""Synthetic 测试数据生成器

为验证 Hydrology MCP 服务生成测试数据：
1. 模拟地形数据（DEM）- 用于 HiPIMS
2. 测试图像数据 - 用于 YOLO 洪水检测
3. 边界条件数据 - 入流、降雨等

所有数据都经过人工设计，具有可预测的结果，便于验证模型正确性。
"""

import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta

# 测试数据目录
DATA_DIR = Path(__file__).parent
TERRAIN_DIR = DATA_DIR / "terrain"
IMAGES_DIR = DATA_DIR / "images"
BOUNDARY_DIR = DATA_DIR / "boundary"

# 创建目录
TERRAIN_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
BOUNDARY_DIR.mkdir(exist_ok=True)


def generate_flat_terrain():
    """
    场景1: 平坦地形
    
    【预期结果】
    - 水流均匀分布
    - 淹没范围对称
    - 最大水深 ≈ 2.0m (在入流点)
    - 适合验证基础水流计算
    """
    size = 50
    elevation = np.ones((size, size)) * 10.0  # 平坦，高程10m
    
    # 添加轻微坡度便于排水 (0.1% 坡度，向东)
    for i in range(size):
        elevation[i, :] = 10.0 - (i / size) * 0.5
    
    metadata = {
        "name": "flat_terrain",
        "description": "平坦地形，轻微坡度",
        "size": f"{size}x{size}",
        "cell_size": 10,  # 10m x 10m
        "expected": {
            "max_depth": "~2.0m (入流点)",
            "flow_pattern": "均匀向东流动",
            "inundation_area": "~30% 区域",
            "verification_points": [
                "水深从入流点向西递减",
                "流速在0.5-1.5 m/s之间",
                "淹没范围大致对称"
            ]
        }
    }
    
    return elevation, metadata


def generate_valley_terrain():
    """
    场景2: 河谷地形
    
    【预期结果】
    - 水流沿河道集中
    - 两岸高地不被淹没
    - 最大水深 ≈ 3.5m (河道中心)
    - 适合验证地形约束效果
    """
    size = 50
    elevation = np.ones((size, size)) * 20.0
    
    # 创建河谷 (中间低，两边高)
    for i in range(size):
        for j in range(size):
            # 河谷在中心 (j=25)
            dist_from_center = abs(j - 25)
            if dist_from_center < 5:
                elevation[i, j] = 8.0  # 河道底部
            elif dist_from_center < 10:
                elevation[i, j] = 12.0  # 河岸
            else:
                elevation[i, j] = 20.0  # 高地
    
    # 添加纵向坡度 (北向南)
    for i in range(size):
        elevation[i, :] -= (i / size) * 2.0
    
    metadata = {
        "name": "valley_terrain",
        "description": "河谷地形，中间河道，两岸高地",
        "size": f"{size}x{size}",
        "cell_size": 10,
        "expected": {
            "max_depth": "~3.5m (河道中心)",
            "flow_pattern": "沿河道向南流动",
            "inundation_area": "~20% 区域(主要在河道)",
            "verification_points": [
                "两岸高地(depth<0.1m)不被淹没",
                "水流集中在河道内",
                "河道中心流速 > 2.0 m/s"
            ]
        }
    }
    
    return elevation, metadata


def generate_basin_terrain():
    """
    场景3: 盆地地形（易积水）
    
    【预期结果】
    - 水向中心汇集
    - 形成湖泊/积水区
    - 最大水深 ≈ 4.0m (中心)
    - 适合验证积水效果
    """
    size = 50
    elevation = np.ones((size, size)) * 15.0
    
    # 创建盆地 (中心低，四周高)
    center_x, center_y = 25, 25
    for i in range(size):
        for j in range(size):
            dist = np.sqrt((i - center_x)**2 + (j - center_y)**2)
            # 盆地深度随距离增加
            depth = min(dist * 0.3, 8.0)  # 最大深度8m
            elevation[i, j] = 15.0 - depth
    
    # 添加出口 (东北角较低)
    elevation[0:5, 45:50] = 5.0
    
    metadata = {
        "name": "basin_terrain",
        "description": "盆地地形，中心低洼，易积水",
        "size": f"{size}x{size}",
        "cell_size": 10,
        "expected": {
            "max_depth": "~4.0m (盆地中心)",
            "flow_pattern": "向中心汇集后从东北流出",
            "inundation_area": "~60% 区域",
            "verification_points": [
                "中心形成积水区",
                "水深从中心向边缘递减",
                "出口处有明渠流"
            ]
        }
    }
    
    return elevation, metadata


def save_terrain_ascii(elevation, metadata, filename):
    """保存地形为 ASCII Grid 格式"""
    size = elevation.shape[0]
    cell_size = metadata.get("cell_size", 10)
    
    filepath = TERRAIN_DIR / filename
    with open(filepath, 'w') as f:
        # ASCII Grid 头
        f.write(f"NCOLS {size}\n")
        f.write(f"NROWS {size}\n")
        f.write(f"XLLCENTER 0.0\n")
        f.write(f"YLLCENTER 0.0\n")
        f.write(f"CELLSIZE {cell_size}\n")
        f.write(f"NODATA_VALUE -9999\n")
        
        # 数据 (从北到南)
        for i in range(size):
            row = elevation[i, :]
            f.write(' '.join([f'{v:.2f}' for v in row]) + '\n')
    
    # 保存元数据
    meta_filepath = TERRAIN_DIR / f"{filepath.stem}_metadata.json"
    with open(meta_filepath, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 地形已保存: {filepath}")
    print(f"✓ 元数据已保存: {meta_filepath}")
    
    return filepath


def generate_inflow_hydrograph(scenario="moderate"):
    """
    生成入流过程线
    
    【场景】
    - moderate: 中等洪水，峰值 100 m³/s
    - small: 小洪水，峰值 50 m³/s
    - extreme: 极端洪水，峰值 200 m³/s
    
    【预期】
    - 流量从零开始，上升到峰值，再回落
    - 总历时 2-4 小时
    """
    duration = 4 * 3600  # 4小时
    dt = 300  # 5分钟间隔
    n_steps = duration // dt
    
    time = np.arange(0, duration + dt, dt)
    
    if scenario == "moderate":
        peak = 100.0  # m³/s
    elif scenario == "small":
        peak = 50.0
    elif scenario == "extreme":
        peak = 200.0
    else:
        peak = 100.0
    
    # 三角形洪水过程线
    inflow = np.zeros_like(time, dtype=float)
    peak_idx = len(time) // 3  # 峰值在1/3处
    
    for i, t in enumerate(time):
        if i <= peak_idx:
            # 上升段
            inflow[i] = peak * (i / peak_idx)
        else:
            # 下降段
            inflow[i] = peak * (1 - (i - peak_idx) / (len(time) - peak_idx))
    
    # 保存
    data = {
        "time_seconds": time.tolist(),
        "inflow_cms": inflow.tolist(),
        "scenario": scenario,
        "peak_flow": peak,
        "duration_hours": duration / 3600,
        "expected": {
            "peak_time": f"{time[peak_idx]/3600:.1f}小时",
            "total_volume": f"{np.trapz(inflow, time)/1e6:.2f}百万m³",
            "verification": "流量应从0上升到峰值再回落到0"
        }
    }
    
    filepath = BOUNDARY_DIR / f"inflow_{scenario}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 入流过程线已保存: {filepath}")
    return filepath


def generate_rainfall_data(scenario="moderate"):
    """
    生成降雨数据
    
    【场景】
    - moderate: 50mm/h，持续2小时
    - light: 20mm/h，持续1小时
    - heavy: 100mm/h，持续3小时
    """
    if scenario == "moderate":
        intensity = 50.0  # mm/h
        duration = 2  # hours
    elif scenario == "light":
        intensity = 20.0
        duration = 1
    elif scenario == "heavy":
        intensity = 100.0
        duration = 3
    else:
        intensity = 50.0
        duration = 2
    
    data = {
        "type": "uniform",
        "intensity_mmh": intensity,
        "duration_hours": duration,
        "total_rainfall_mm": intensity * duration,
        "scenario": scenario,
        "expected": {
            "runoff_coefficient": "0.6-0.8 (取决于地表)",
            "peak_runoff": f"{intensity * 0.7:.0f} mm/h (估算)",
            "verification": f"总降雨量应为 {intensity * duration} mm"
        }
    }
    
    filepath = BOUNDARY_DIR / f"rainfall_{scenario}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 降雨数据已保存: {filepath}")
    return filepath


def create_synthetic_flood_image():
    """
    创建合成洪水检测图像
    
    【说明】
    由于 YOLO 需要真实图像，这里创建模拟图像用于测试框架
    实际测试时需要替换为真实洪水图像
    
    【预期检测结果】
    - 图像中应检测到水体区域
    - 置信度应在 0.5-0.9 之间
    """
    try:
        from PIL import Image, ImageDraw
        
        # 创建模拟图像 (640x480)
        img = Image.new('RGB', (640, 480), color='skyblue')
        draw = ImageDraw.Draw(img)
        
        # 绘制地面 (下半部分)
        draw.rectangle([0, 300, 640, 480], fill='saddlebrown')
        
        # 绘制水体 (蓝色区域，模拟洪水)
        # 场景1: 河流泛滥
        draw.polygon([(100, 320), (200, 300), (400, 310), (540, 330), 
                      (550, 400), (400, 420), (200, 410), (80, 380)], 
                     fill='steelblue')
        
        # 保存
        filepath = IMAGES_DIR / "synthetic_flood_01.jpg"
        img.save(filepath, quality=95)
        print(f"✓ 合成洪水图像已保存: {filepath}")
        
        # 创建元数据
        metadata = {
            "filename": "synthetic_flood_01.jpg",
            "description": "合成洪水图像 - 河流泛滥场景",
            "size": "640x480",
            "expected_detections": [
                {"class": "water", "confidence": "0.7-0.9", "area": "center"},
                {"class": "flood", "confidence": "0.6-0.8", "area": "lower"}
            ],
            "verification": "YOLO应检测到水体，置信度>0.5"
        }
        
        meta_filepath = IMAGES_DIR / "synthetic_flood_01_metadata.json"
        with open(meta_filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return filepath
        
    except ImportError:
        print("⚠ PIL 未安装，跳过图像生成")
        print("  如需生成测试图像，请运行: pip install Pillow")
        return None


def generate_test_manifest():
    """生成测试清单，汇总所有测试数据"""
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "test_scenarios": [
            {
                "id": "TS001",
                "name": "平坦地形中等洪水",
                "terrain": "flat_terrain.asc",
                "inflow": "inflow_moderate.json",
                "rainfall": "rainfall_moderate.json",
                "expected_focus": [
                    "验证基础水流计算",
                    "检查淹没范围对称性",
                    "确认最大水深位置"
                ]
            },
            {
                "id": "TS002",
                "name": "河谷地形洪水演进",
                "terrain": "valley_terrain.asc",
                "inflow": "inflow_moderate.json",
                "rainfall": "rainfall_light.json",
                "expected_focus": [
                    "验证河道约束效果",
                    "检查两岸高地是否被保护",
                    "确认水流沿河道集中"
                ]
            },
            {
                "id": "TS003",
                "name": "盆地地形积水模拟",
                "terrain": "basin_terrain.asc",
                "inflow": "inflow_small.json",
                "rainfall": "rainfall_heavy.json",
                "expected_focus": [
                    "验证积水效果",
                    "检查中心最大水深",
                    "确认出口流量"
                ]
            }
        ],
        "verification_checklist": [
            "□ HiPIMS 能正确读取地形文件",
            "□ 模拟运行完成无错误",
            "□ 输出结果符合预期范围",
            "□ 水深分布与地形一致",
            "□ 流速在合理范围内 (0-5 m/s)",
            "□ 淹没面积符合预期",
            "□ YOLO 能检测到水体",
            "□ Hydrology 能调用 HiPIMS",
            "□ Hydrology 能调用 YOLO"
        ]
    }
    
    filepath = DATA_DIR / "test_manifest.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 测试清单已生成: {filepath}")
    return filepath


def main():
    """主函数：生成所有测试数据"""
    print("=" * 60)
    print("Synthetic 测试数据生成器")
    print("=" * 60)
    print()
    
    # 1. 生成地形数据
    print("【1/4】生成地形数据...")
    print("-" * 60)
    
    terrains = [
        generate_flat_terrain(),
        generate_valley_terrain(),
        generate_basin_terrain()
    ]
    
    for elevation, metadata in terrains:
        save_terrain_ascii(elevation, metadata, f"{metadata['name']}.asc")
        print()
    
    # 2. 生成边界条件
    print("【2/4】生成边界条件数据...")
    print("-" * 60)
    
    generate_inflow_hydrograph("small")
    generate_inflow_hydrograph("moderate")
    generate_inflow_hydrograph("extreme")
    print()
    
    generate_rainfall_data("light")
    generate_rainfall_data("moderate")
    generate_rainfall_data("heavy")
    print()
    
    # 3. 生成测试图像
    print("【3/4】生成测试图像...")
    print("-" * 60)
    create_synthetic_flood_image()
    print()
    
    # 4. 生成测试清单
    print("【4/4】生成测试清单...")
    print("-" * 60)
    generate_test_manifest()
    print()
    
    # 总结
    print("=" * 60)
    print("测试数据生成完成！")
    print("=" * 60)
    print(f"\n数据目录: {DATA_DIR}")
    print(f"  - 地形: {TERRAIN_DIR}")
    print(f"  - 边界: {BOUNDARY_DIR}")
    print(f"  - 图像: {IMAGES_DIR}")
    print()
    print("下一步:")
    print("  1. 查看 test_manifest.json 了解测试场景")
    print("  2. 运行端到端验证脚本")
    print("  3. 对比实际输出与预期结果")


if __name__ == "__main__":
    main()
