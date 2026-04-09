"""
降雨数据 MCP 服务测试
测试降雨数据获取功能
"""

import asyncio
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flood_decision_agent.mcp.clients.base import MCPClientManager


async def test_rainfall_mcp():
    """测试降雨数据 MCP 服务"""

    print("=" * 60)
    print("降雨数据 MCP 服务测试")
    print("=" * 60)

    # 初始化客户端管理器
    manager = MCPClientManager()

    try:
        # 连接到所有启用的服务器
        print("\n[1] 连接到 MCP 服务器...")
        await manager.connect_all()

        # 获取降雨服务器客户端
        client = manager.clients.get("rainfall")
        if not client:
            print("[X] 未找到 rainfall 服务器连接")
            return False

        print("[OK] 已连接到 rainfall 服务器")

        # 测试 1: 检查 API 状态
        print("\n[2] 检查 API 状态...")
        status_result = await client.call_tool("check_api_status", {})
        print(f"API 状态: {status_result}")

        if not status_result.get("success"):
            print("[X] API 状态检查失败")
            return False

        providers = status_result.get("providers", {})
        has_api_key = any(p.get("has_api_key") for p in providers.values())

        if not has_api_key:
            print("[!] 未配置 API Key")
            print("请设置环境变量:")
            print("  - OPENWEATHER_API_KEY (OpenWeatherMap)")
            print("  - QWEATHER_API_KEY (和风天气)")
            print("\n免费获取 API Key:")
            print("  - OpenWeatherMap: https://openweathermap.org/api")
            print("  - 和风天气: https://dev.qweather.com/")
            print("\n跳过实际数据获取测试...")
            return True

        # 测试 2: 获取当前降雨数据
        print("\n[3] 测试获取当前降雨数据...")
        try:
            current_result = await client.call_tool("get_current_rainfall", {
                "city": "北京",
                "provider": "auto"
            })
            print(f"当前降雨数据: success={current_result.get('success')}")
            if current_result.get("success"):
                current = current_result.get("current", {})
                print(f"  城市: {current_result.get('city')}")
                print(f"  温度: {current.get('temperature')}C")
                print(f"  天气: {current.get('weather')}")
                print(f"  降雨量: {current.get('rain_1h', current.get('precipitation', 0))}mm")
        except Exception as e:
            print(f"  [WARN] 获取当前降雨数据失败: {e}")

        # 测试 3: 获取降雨预报
        print("\n[4] 测试获取降雨预报...")
        try:
            forecast_result = await client.call_tool("get_rainfall_forecast", {
                "city": "上海",
                "days": 3,
                "provider": "auto"
            })
            print(f"降雨预报: success={forecast_result.get('success')}")
            if forecast_result.get("success"):
                forecasts = forecast_result.get("forecasts", [])
                print(f"  预报天数: {len(forecasts)}")
                for f in forecasts[:3]:
                    date = f.get("date") or f.get("datetime", "")
                    precip = f.get("precipitation") or f.get("rain_3h", 0)
                    print(f"    {date}: {precip}mm")
        except Exception as e:
            print(f"  [WARN] 获取降雨预报失败: {e}")

        # 测试 4: 获取逐小时预报
        print("\n[5] 测试获取逐小时降雨预报...")
        try:
            hourly_result = await client.call_tool("get_hourly_rainfall", {
                "city": "广州",
                "hours": 6,
                "provider": "auto"
            })
            print(f"逐小时预报: success={hourly_result.get('success')}")
            if hourly_result.get("success"):
                forecasts = hourly_result.get("forecasts", [])
                print(f"  预报小时数: {len(forecasts)}")
                for f in forecasts[:3]:
                    dt = f.get("datetime") or f.get("date", "")
                    precip = f.get("precipitation") or f.get("rain_3h", 0)
                    print(f"    {dt}: {precip}mm")
        except Exception as e:
            print(f"  [WARN] 获取逐小时预报失败: {e}")

        # 测试 5: 根据坐标获取降雨数据
        print("\n[6] 测试根据坐标获取降雨数据...")
        try:
            coords_result = await client.call_tool("get_rainfall_by_coords", {
                "lat": 39.9042,  # 北京坐标
                "lon": 116.4074,
                "provider": "auto"
            })
            print(f"坐标查询: success={coords_result.get('success')}")
            if coords_result.get("success"):
                coords = coords_result.get("coordinates", {})
                current = coords_result.get("current", {})
                print(f"  坐标: ({coords.get('lat')}, {coords.get('lon')})")
                print(f"  位置: {coords_result.get('location', 'N/A')}")
                print(f"  温度: {current.get('temperature')}C")
        except Exception as e:
            print(f"  [WARN] 坐标查询失败: {e}")

        print("\n" + "=" * 60)
        print("[OK] 测试完成!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[X] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 断开所有连接
        print("\n[清理] 断开 MCP 服务器连接...")
        await manager.close_all()
        print("[OK] 已断开所有连接")


if __name__ == "__main__":
    # 检查 API Key
    if not os.environ.get("KIMI_API_KEY"):
        print("需要kimi_api_key")
        sys.exit(1)

    # 运行测试
    success = asyncio.run(test_rainfall_mcp())
    sys.exit(0 if success else 1)
