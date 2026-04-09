"""Web Search MCP Server 测试脚本

测试 web_search MCP Server 的各项功能。
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.mcp.servers.web_search_server import (
    _handle_check_api_status,
    _handle_web_search,
    _handle_fetch_webpage,
    _handle_news_search,
    _handle_academic_search,
)


def check_api_key():
    """检查 API Key 是否配置"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("=" * 60)
        print("错误: 未配置 KIMI_API_KEY 环境变量")
        print("=" * 60)
        print("\n请先设置环境变量:")
        print("  Windows PowerShell: $env:KIMI_API_KEY=\"your-api-key\"")
        print("  Windows CMD: set KIMI_API_KEY=your-api-key")
        print("  Linux/Mac: export KIMI_API_KEY=your-api-key")
        print("\n然后重新运行测试。")
        sys.exit(1)
    return api_key


async def test_check_api_status():
    """测试 API 状态检查"""
    print("\n" + "=" * 60)
    print("测试 1: 检查 API 状态")
    print("=" * 60)

    result = await _handle_check_api_status({})
    data = json.loads(result[0].text)

    print(f"API Key 配置: {data.get('api_key_configured')}")
    print(f"API 状态: {data.get('api_status')}")

    if data.get('available_models'):
        print(f"可用模型: {', '.join(data['available_models'][:3])}...")

    if data.get('error'):
        print(f"错误: {data['error']}")

    return data.get('api_status') == 'available'


async def test_web_search():
    """测试网络搜索"""
    print("\n" + "=" * 60)
    print("测试 2: 网络搜索")
    print("=" * 60)

    query = "Python programming language"
    print(f"搜索关键词: {query}")

    result = await _handle_web_search({
        "query": query,
        "num_results": 3
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"✓ 搜索成功")
        print(f"  回答摘要: {data.get('answer', '')[:200]}...")
        print(f"  引用数量: {len(data.get('citations', []))}")

        if data.get('results'):
            print("\n  搜索结果:")
            for item in data['results'][:3]:
                print(f"    {item['index']}. {item['title']}")
                print(f"       URL: {item['url']}")
    else:
        print(f"✗ 搜索失败: {data.get('error')}")

    return data.get('success')


async def test_news_search():
    """测试新闻搜索"""
    print("\n" + "=" * 60)
    print("测试 3: 新闻搜索")
    print("=" * 60)

    query = "人工智能"
    print(f"搜索关键词: {query}")

    result = await _handle_news_search({
        "query": query,
        "num_results": 3
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"✓ 新闻搜索成功")
        print(f"  回答摘要: {data.get('answer', '')[:200]}...")
    else:
        print(f"✗ 新闻搜索失败: {data.get('error')}")

    return data.get('success')


async def test_academic_search():
    """测试学术搜索"""
    print("\n" + "=" * 60)
    print("测试 4: 学术搜索")
    print("=" * 60)

    query = "machine learning"
    print(f"搜索关键词: {query}")

    result = await _handle_academic_search({
        "query": query,
        "num_results": 3
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"✓ 学术搜索成功")
        print(f"  回答摘要: {data.get('answer', '')[:200]}...")
    else:
        print(f"✗ 学术搜索失败: {data.get('error')}")

    return data.get('success')


async def test_fetch_webpage():
    """测试网页抓取"""
    print("\n" + "=" * 60)
    print("测试 5: 网页内容抓取")
    print("=" * 60)

    url = "https://www.python.org"
    print(f"抓取 URL: {url}")

    result = await _handle_fetch_webpage({
        "url": url,
        "max_length": 1000
    })
    data = json.loads(result[0].text)

    if data.get('success'):
        print(f"✓ 网页抓取成功")
        content = data.get('content', '')
        print(f"  内容长度: {len(content)} 字符")
        print(f"  内容摘要: {content[:300]}...")
    else:
        print(f"✗ 网页抓取失败: {data.get('error')}")

    return data.get('success')


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Web Search MCP Server 测试")
    print("=" * 60)

    # 检查 API Key
    check_api_key()

    results = {}

    # 运行测试
    results['api_status'] = await test_check_api_status()
    results['web_search'] = await test_web_search()
    results['news_search'] = await test_news_search()
    results['academic_search'] = await test_academic_search()
    results['fetch_webpage'] = await test_fetch_webpage()

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
        sys.exit(1)
