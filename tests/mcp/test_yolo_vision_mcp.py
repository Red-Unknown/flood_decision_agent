"""
YOLO Vision MCP 服务测试
测试 YOLO11n 水利视觉检测功能
"""

import asyncio
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flood_decision_agent.mcp.clients.base import MCPClientManager


async def test_yolo_vision_mcp():
    """测试 YOLO Vision MCP 服务"""

    print("=" * 60)
    print("YOLO Vision MCP 服务测试")
    print("=" * 60)

    # 初始化客户端管理器
    manager = MCPClientManager()

    try:
        # 连接到所有启用的服务器
        print("\n[1] 连接到 MCP 服务器...")
        await manager.connect_all()

        # 获取 YOLO Vision 服务器客户端
        client = manager.clients.get("yolo_vision")
        if not client:
            print("❌ 未找到 yolo_vision 服务器连接")
            return False

        print("✅ 已连接到 yolo_vision 服务器")

        # 测试 1: 获取模型信息
        print("\n[2] 获取模型信息...")
        info_result = await client.call_tool("get_model_info", {})
        print(f"模型信息: {info_result}")

        if not info_result.get("success"):
            error_msg = info_result.get("error", "")
            if "依赖未安装" in error_msg:
                print("⚠️ 依赖未安装，请运行以下命令安装:")
                print(f"   {info_result.get('install_command')}")
                print("\n📋 注意: MCP Server 运行在独立进程中，需要在系统 Python 中安装依赖")
                print("   安装完成后重新运行测试")
                return False
            print("❌ 获取模型信息失败")
            return False

        print(f"✅ PyTorch: {info_result.get('pytorch_version')}")
        print(f"✅ Ultralytics: {info_result.get('ultralytics_version')}")
        print(f"✅ 设备: {info_result.get('device')}")
        print(f"✅ CUDA可用: {info_result.get('cuda_available')}")

        # 测试 2: 下载测试数据集
        print("\n[3] 下载测试数据集...")
        dataset_result = await client.call_tool("download_test_dataset", {
            "dataset_name": "flood_sample"
        })
        print(f"数据集下载结果: success={dataset_result.get('success')}")

        if not dataset_result.get("success"):
            print("❌ 数据集下载失败")
            return False

        dataset_dir = dataset_result.get("dataset_dir")
        created_files = dataset_result.get("created_files", [])
        print(f"✅ 数据集创建成功: {dataset_dir}")
        print(f"✅ 创建文件数: {len(created_files)}")

        # 测试 3: 检测洪水区域
        print("\n[4] 测试洪水区域检测...")
        if created_files:
            test_image = created_files[0]
            flood_result = await client.call_tool("detect_flood_areas", {
                "image_path": test_image,
                "confidence": 0.25,
                "save_result": True
            })
            print(f"洪水检测结果: success={flood_result.get('success')}")
            print(f"   检测数量: {flood_result.get('detection_count', 0)}")
            print(f"   使用设备: {flood_result.get('device')}")

        # 测试 4: 检测水体
        print("\n[5] 测试水体检测...")
        if len(created_files) > 1:
            test_image = created_files[1]
            water_result = await client.call_tool("detect_water_bodies", {
                "image_path": test_image,
                "confidence": 0.3,
                "save_result": True
            })
            print(f"水体检测结果: success={water_result.get('success')}")
            print(f"   检测数量: {water_result.get('detection_count', 0)}")

        # 测试 5: 检测基础设施
        print("\n[6] 测试基础设施检测...")
        if created_files:
            test_image = created_files[0]
            infra_result = await client.call_tool("detect_infrastructure", {
                "image_path": test_image,
                "confidence": 0.25,
                "save_result": True
            })
            print(f"基础设施检测结果: success={infra_result.get('success')}")
            print(f"   检测数量: {infra_result.get('detection_count', 0)}")

        # 测试 6: 批量检测
        print("\n[7] 测试批量检测...")
        batch_result = await client.call_tool("batch_detect", {
            "image_dir": dataset_dir,
            "task": "all",
            "confidence": 0.25
        })
        print(f"批量检测结果: success={batch_result.get('success')}")
        print(f"   总图像数: {batch_result.get('total_images', 0)}")
        print(f"   已处理: {batch_result.get('processed', 0)}")

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 断开所有连接
        print("\n[清理] 断开 MCP 服务器连接...")
        await manager.close_all()
        print("✅ 已断开所有连接")


if __name__ == "__main__":
    # 检查 API Key
    if not os.environ.get("KIMI_API_KEY"):
        print("需要kimi_api_key")
        sys.exit(1)

    # 运行测试
    success = asyncio.run(test_yolo_vision_mcp())
    sys.exit(0 if success else 1)
