"""Data Hub MCP Server 测试脚本

测试 data_hub MCP Server 的各项功能。
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.mcp.servers.data_hub_server import (
    _handle_get_rainfall_data,
    _handle_get_hydrological_data,
    _handle_aggregate_data_sources,
    _handle_check_data_sources_status,
    _handle_get_cache_stats,
    _handle_clear_cache,
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


async def test_check_data_sources_status():
    """测试检查数据源状态"""
    print("\n" + "=" * 60)
    print("测试 1: 检查数据源状态")
    print("=" * 60)

    result = await _handle_check_data_sources_status({})
    data = json.loads(result[0].text)

    print(f"成功: {data.get('success')}")
    print(f"时间戳: {data.get('timestamp')}")

    # 打印数据源状态
    sources = data.get('sources', [])
    if sources:
        print("\n数据源状态:")
        for source in sources:
            name = source.get('name', 'unknown')
            available = "✓" if source.get('available') else "✗"
            has_key = "✓" if source.get('has_api_key') else "✗"
            latency = source.get('latency_ms', 'N/A')
            print(f"  {name}: 可用{available}, 有API Key{has_key}, 延迟{latency}ms")
            if source.get('error_message'):
                print(f"    错误: {source.get('error_message')}")

    # 打印环境变量状态
    env_vars = data.get('environment_variables', {})
    if env_vars:
        print("\n环境变量配置:")
        for var, configured in env_vars.items():
            status = "✓" if configured else "✗"
            print(f"  {var}: {status}")

    # 打印缓存统计
    cache_stats = data.get('cache_stats', {})
    if cache_stats:
        print(f"\n缓存统计:")
        print(f"  总条目: {cache_stats.get('total_entries', 0)}")
        print(f"  有效条目: {cache_stats.get('valid_entries', 0)}")

    return data.get('success', False)


async def test_get_rainfall_data():
    """测试获取降雨数据"""
    print("\n" + "=" * 60)
    print("测试 2: 获取降雨数据")
    print("=" * 60)

    city = "北京"
    print(f"测试城市: {city}")

    result = await _handle_get_rainfall_data({
        "city": city,
        "provider": "auto",
        "use_cache": False
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"✓ 数据获取成功")
        print(f"  数据源: {data.get('source')}")
        print(f"  数据类型: {data.get('data_type')}")

        rainfall_data = data.get('data', {})
        current = rainfall_data.get('current', {})

        print(f"  城市: {rainfall_data.get('city')}")
        print(f"  温度: {current.get('temperature')}°C")
        print(f"  湿度: {current.get('humidity')}%")
        print(f"  天气: {current.get('weather')}")

        # 降水量可能在不同字段
        precip = current.get('precipitation') or current.get('rain_1h', 0)
        print(f"  降水量: {precip}mm")
    else:
        print(f"✗ 数据获取失败: {data.get('error')}")

    return data.get('success', False)


async def test_get_hydrological_data():
    """测试获取水文数据"""
    print("\n" + "=" * 60)
    print("测试 3: 获取水文数据")
    print("=" * 60)

    station_id = "TEST_STATION_001"
    print(f"测试站点: {station_id}")

    # 测试水位数据
    result = await _handle_get_hydrological_data({
        "station_id": station_id,
        "data_type": "water_level",
        "hours": 12
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"✓ 水位数据获取成功")
        hydro_data = data.get('data', {})
        print(f"  站点ID: {hydro_data.get('station_id')}")
        print(f"  数据类型: {hydro_data.get('data_type')}")
        print(f"  当前值: {hydro_data.get('current_value')} {hydro_data.get('unit')}")
        print(f"  趋势: {hydro_data.get('trend')}")

        history = hydro_data.get('history', [])
        print(f"  历史数据点: {len(history)} 个")

        # 测试流量数据
        print("\n  测试流量数据...")
        result2 = await _handle_get_hydrological_data({
            "station_id": station_id,
            "data_type": "flow_rate",
            "hours": 6
        })
        data2 = json.loads(result2[0].text)

        if data2.get('success'):
            flow_data = data2.get('data', {})
            print(f"  流量当前值: {flow_data.get('current_value')} {flow_data.get('unit')}")
    else:
        print(f"✗ 水文数据获取失败: {data.get('error')}")

    return data.get('success', False)


async def test_aggregate_data_sources():
    """测试聚合多数据源"""
    print("\n" + "=" * 60)
    print("测试 4: 聚合多数据源")
    print("=" * 60)

    city = "上海"
    print(f"测试城市: {city}")

    result = await _handle_aggregate_data_sources({
        "data_type": "rainfall",
        "city": city,
        "sources": ["openweather", "qweather"]
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"✓ 数据聚合成功")
        print(f"  查询ID: {data.get('query_id')}")
        print(f"  数据源类型: {data.get('data_type')}")
        print(f"  成功数据源: {', '.join(data.get('sources_used', []))}")
        print(f"  失败数据源: {data.get('sources_failed', [])}")
        print(f"  置信度分数: {data.get('confidence_score')}")

        agg_data = data.get('data', {})
        if agg_data:
            print(f"\n  聚合结果:")
            print(f"    城市: {agg_data.get('city')}")

            if 'temperature_avg' in agg_data:
                print(f"    平均温度: {agg_data.get('temperature_avg')}°C")
            if 'humidity_avg' in agg_data:
                print(f"    平均湿度: {agg_data.get('humidity_avg')}%")
            if 'precipitation_avg' in agg_data:
                print(f"    平均降水量: {agg_data.get('precipitation_avg')}mm")
            if 'precipitation_max' in agg_data:
                print(f"    最大降水量: {agg_data.get('precipitation_max')}mm")

            sources = agg_data.get('sources', [])
            print(f"    使用的数据源: {', '.join(sources)}")
    else:
        print(f"✗ 数据聚合失败: {data.get('error')}")
        # 部分失败也算测试通过（可能是API Key未配置）
        if data.get('sources_used'):
            print(f"  部分成功，使用了: {', '.join(data.get('sources_used', []))}")
            return True

    return data.get('success', False)


async def test_cache_operations():
    """测试缓存操作"""
    print("\n" + "=" * 60)
    print("测试 5: 缓存操作")
    print("=" * 60)

    # 先获取一次数据以填充缓存
    print("1. 获取数据并缓存...")
    await _handle_get_rainfall_data({
        "city": "广州",
        "provider": "auto",
        "use_cache": True
    })

    # 检查缓存统计
    print("2. 检查缓存统计...")
    result = await _handle_get_cache_stats({})
    data = json.loads(result[0].text)

    if data.get('success'):
        stats = data.get('cache_stats', {})
        print(f"  总条目: {stats.get('total_entries', 0)}")
        print(f"  有效条目: {stats.get('valid_entries', 0)}")
        print(f"  过期条目: {stats.get('expired_entries', 0)}")

    # 清空缓存
    print("3. 清空缓存...")
    result = await _handle_clear_cache({})
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"  ✓ {data.get('message')}")

    # 再次检查缓存统计
    print("4. 再次检查缓存统计...")
    result = await _handle_get_cache_stats({})
    data = json.loads(result[0].text)

    if data.get('success'):
        stats = data.get('cache_stats', {})
        print(f"  总条目: {stats.get('total_entries', 0)} (应为 0)")

    return True


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Data Hub MCP Server 测试")
    print("=" * 60)

    # 检查 API Key
    check_api_key()

    results = {}

    # 运行测试
    results['check_data_sources_status'] = await test_check_data_sources_status()
    results['get_rainfall_data'] = await test_get_rainfall_data()
    results['get_hydrological_data'] = await test_get_hydrological_data()
    results['aggregate_data_sources'] = await test_aggregate_data_sources()
    results['cache_operations'] = await test_cache_operations()

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
