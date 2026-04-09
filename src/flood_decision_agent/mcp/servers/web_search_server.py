"""Web Search MCP Server

提供网络搜索和网页内容抓取功能，封装 KIMI API 的联网查询能力。
支持：
- 网络搜索（使用多种搜索引擎）
- 网页内容抓取和解析
- 新闻搜索
- 学术搜索

环境变量:
    KIMI_API_KEY: KIMI API Key（必需，优先从系统环境变量读取）
"""

import asyncio
import json
from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps, fast_json_loads
import os
import platform
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlparse

import aiohttp
from mcp.server import Server
from mcp.types import TextContent, Tool

# 创建 MCP Server
server = Server("flood-agent-web-search")

# API 配置
KIMI_API_BASE = "https://api.moonshot.cn/v1"
SEARCH_ENGINE = "google"  # 默认搜索引擎

# 缓存
_cache: Dict[str, Any] = {}
_cache_timeout = 300  # 5分钟缓存


def _get_system_env(key: str) -> Optional[str]:
    """从系统环境变量读取（支持 Windows 用户级和系统级）"""
    try:
        import winreg
        # 先尝试用户级环境变量
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as reg_key:
                value, _ = winreg.QueryValueEx(reg_key, key)
                if value:
                    return value
        except FileNotFoundError:
            pass
        # 再尝试系统级环境变量
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as reg_key:
                value, _ = winreg.QueryValueEx(reg_key, key)
                if value:
                    return value
        except FileNotFoundError:
            pass
    except Exception:
        pass
    return None


def _get_api_key() -> Optional[str]:
    """获取 KIMI API Key

    优先级：
    1. 进程环境变量 (os.environ)
    2. Windows 用户级系统环境变量
    3. Windows 系统级环境变量
    """
    # 1. 先检查进程环境变量
    api_key = os.environ.get("KIMI_API_KEY")
    if api_key and api_key != "your-api-key":
        return api_key

    # 2. 尝试从 Windows 系统环境变量读取
    if platform.system() == "Windows":
        api_key = _get_system_env("KIMI_API_KEY")
        if api_key:
            # 缓存到进程环境变量，避免重复读取注册表
            os.environ["KIMI_API_KEY"] = api_key
            return api_key

    return None


def _get_cached(key: str) -> Optional[Any]:
    """获取缓存数据"""
    if key in _cache:
        data, timestamp = _cache[key]
        if datetime.now().timestamp() - timestamp < _cache_timeout:
            return data
        del _cache[key]
    return None


def _set_cached(key: str, data: Any):
    """设置缓存数据"""
    _cache[key] = (data, datetime.now().timestamp())


@server.list_tools()
async def list_tools() -> List[Tool]:
    """定义可用工具"""
    return [
        Tool(
            name="web_search",
            description="执行网络搜索，返回搜索结果摘要",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "返回结果数量 (1-10)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="fetch_webpage",
            description="抓取网页内容并提取文本",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "网页URL"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "最大返回字符数",
                        "default": 5000,
                        "minimum": 100,
                        "maximum": 10000
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="news_search",
            description="搜索新闻",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "days": {
                        "type": "integer",
                        "description": "搜索最近几天的新闻",
                        "default": 7,
                        "minimum": 1,
                        "maximum": 30
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="academic_search",
            description="学术搜索（论文、期刊等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="check_api_status",
            description="检查 API 服务状态",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "web_search":
            return await _handle_web_search(arguments)
        elif name == "fetch_webpage":
            return await _handle_fetch_webpage(arguments)
        elif name == "news_search":
            return await _handle_news_search(arguments)
        elif name == "academic_search":
            return await _handle_academic_search(arguments)
        elif name == "check_api_status":
            return await _handle_check_api_status(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
    except Exception as e:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": str(e, ensure_ascii=False),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)
        )]


async def _handle_web_search(args: Dict[str, Any]) -> List[TextContent]:
    """处理网络搜索"""
    api_key = _get_api_key()
    if not api_key:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": "未配置 KIMI_API_KEY 环境变量",
                "note": "请设置环境变量: KIMI_API_KEY"
            }, ensure_ascii=False)
        )]

    query = args["query"]
    num_results = args.get("num_results", 5)

    # 检查缓存
    cache_key = f"search_{query}_{num_results}"
    cached = _get_cached(cache_key)
    if cached:
        return [TextContent(type="text", text=fast_json_dumps(cached, ensure_ascii=False, indent=2))]

    # 使用 KIMI API 进行搜索
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 调用 KIMI Chat Completions API with web search
        # 使用内置的 web_search 功能（通过 tool_choice 和 tools 参数）
        payload = {
            "model": "moonshot-v1-8k",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个网络搜索助手。请根据用户的搜索请求，使用网络搜索工具获取最新信息，然后提供相关的搜索结果摘要。"
                },
                {
                    "role": "user",
                    "content": f"请搜索以下内容: {query}"
                }
            ],
            "temperature": 0.3,
            "tools": [
                {
                    "type": "builtin_function",
                    "function": {
                        "name": "$web_search"
                    }
                }
            ],
            "tool_choice": "auto"
        }

        try:
            async with session.post(
                f"{KIMI_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"API 请求失败: {resp.status} - {error_text}")

                data = await resp.json()

                # 提取搜索结果
                result = {
                    "success": True,
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "results": []
                }

                # 从响应中提取搜索结果
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    content = message.get("content", "")

                    # 尝试提取引用信息
                    citations = message.get("citations", [])

                    result["answer"] = content
                    result["citations"] = citations

                    # 构建搜索结果列表
                    for i, citation in enumerate(citations[:num_results], 1):
                        result["results"].append({
                            "index": i,
                            "title": citation.get("title", "未知标题"),
                            "url": citation.get("url", ""),
                            "snippet": citation.get("content", "")[:300]
                        })

                _set_cached(cache_key, result)

                return [TextContent(
                    type="text",
                    text=fast_json_dumps(result, ensure_ascii=False, indent=2)
                )]

        except asyncio.TimeoutError:
            return [TextContent(
                type="text",
                text=fast_json_dumps({
                    "success": False,
                    "error": "搜索请求超时",
                    "query": query
                }, ensure_ascii=False)
            )]


async def _handle_fetch_webpage(args: Dict[str, Any]) -> List[TextContent]:
    """抓取网页内容"""
    url = args["url"]
    max_length = args.get("max_length", 5000)

    # 验证 URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"无效的 URL: {url}")
    except Exception as e:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": f"URL 验证失败: {e}"
            }, ensure_ascii=False)
        )]

    # 检查缓存
    cache_key = f"webpage_{url}"
    cached = _get_cached(cache_key)
    if cached:
        return [TextContent(type="text", text=fast_json_dumps(cached, ensure_ascii=False, indent=2))]

    api_key = _get_api_key()
    if not api_key:
        return [TextContent(
            type="text",
            text=fast_json_dumps({
                "success": False,
                "error": "未配置 KIMI_API_KEY 环境变量"
            }, ensure_ascii=False)
        )]

    # 使用 KIMI API 抓取网页
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "moonshot-v1-8k",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个网页内容提取助手。请使用网络搜索工具获取网页内容，然后提取并总结网页的主要内容。"
                },
                {
                    "role": "user",
                    "content": f"请抓取并总结以下网页的内容: {url}"
                }
            ],
            "temperature": 0.3,
            "tools": [
                {
                    "type": "builtin_function",
                    "function": {
                        "name": "$web_search"
                    }
                }
            ],
            "tool_choice": "auto"
        }

        try:
            async with session.post(
                f"{KIMI_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"API 请求失败: {resp.status} - {error_text}")

                data = await resp.json()

                result = {
                    "success": True,
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                }

                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    content = message.get("content", "")

                    # 截断内容
                    if len(content) > max_length:
                        content = content[:max_length] + "..."

                    result["content"] = content
                    result["citations"] = message.get("citations", [])

                _set_cached(cache_key, result)

                return [TextContent(
                    type="text",
                    text=fast_json_dumps(result, ensure_ascii=False, indent=2)
                )]

        except asyncio.TimeoutError:
            return [TextContent(
                type="text",
                text=fast_json_dumps({
                    "success": False,
                    "error": "网页抓取超时",
                    "url": url
                }, ensure_ascii=False)
            )]


async def _handle_news_search(args: Dict[str, Any]) -> List[TextContent]:
    """搜索新闻"""
    query = args["query"]
    days = args.get("days", 7)
    num_results = args.get("num_results", 5)

    # 构建新闻搜索查询
    news_query = f"{query} 新闻"

    # 调用 web_search
    return await _handle_web_search({
        "query": news_query,
        "num_results": num_results
    })


async def _handle_academic_search(args: Dict[str, Any]) -> List[TextContent]:
    """学术搜索"""
    query = args["query"]
    num_results = args.get("num_results", 5)

    # 构建学术搜索查询
    academic_query = f"{query} 学术论文 研究"

    # 调用 web_search
    return await _handle_web_search({
        "query": academic_query,
        "num_results": num_results
    })


async def _handle_check_api_status(args: Dict[str, Any]) -> List[TextContent]:
    """检查 API 状态"""
    api_key = _get_api_key()

    status = {
        "success": True,
        "api_key_configured": bool(api_key),
        "timestamp": datetime.now().isoformat()
    }

    if api_key:
        # 测试 API 连接
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            try:
                async with session.get(
                    f"{KIMI_API_BASE}/models",
                    headers=headers,
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        status["api_status"] = "available"
                        data = await resp.json()
                        status["available_models"] = [m.get("id") for m in data.get("data", [])]
                    else:
                        status["api_status"] = "error"
                        status["error"] = f"HTTP {resp.status}"
            except Exception as e:
                status["api_status"] = "unreachable"
                status["error"] = str(e)
    else:
        status["api_status"] = "not_configured"
        status["note"] = "请设置 KIMI_API_KEY 环境变量"

    return [TextContent(
        type="text",
        text=fast_json_dumps(status, ensure_ascii=False, indent=2)
    )]


async def main():
    """启动 MCP Server（Windows 兼容版）"""
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    from mcp.server.stdio import stdio_server as mcp_stdio_server

    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
