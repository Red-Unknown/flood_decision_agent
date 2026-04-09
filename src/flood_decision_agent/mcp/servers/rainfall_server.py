"""Rainfall Data MCP Server

降雨数据服务 - 提供实时和历史降雨数据查询
仅支持：和风天气

环境变量:
    QWEATHER_API_KEY: 和风天气 API Key
"""

import asyncio
import os
import platform
import sys
from pathlib import Path

from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps, fast_json_loads
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import aiohttp
from mcp.server import Server
from mcp.types import TextContent, Tool

from src.flood_decision_agent.mcp.log import get_mcp_logger, ToolCallContext
from src.flood_decision_agent.mcp.log.error_formatter import format_error as format_error_dict

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
from flood_decision_agent.infrastructure.config_loader import get_api_key

SERVER_NAME = "rainfall"
logger = get_mcp_logger(SERVER_NAME)

# 创建 MCP Server
server = Server("flood-agent-rainfall")

# 和风天气配置
QWEATHER_BASE_URL = "https://m92k5pcp5g.re.qweatherapi.com/v7"

# 缓存
_cache: Dict[str, Any] = {}
_cache_timeout = 300  # 5分钟缓存

# 常用城市ID映射表（和风天气）
CITY_ID_MAP = {
    # 直辖市
    "北京": "101010100",
    "上海": "101020100",
    "天津": "101030100",
    "重庆": "101040100",
    # 省会城市
    "广州": "101280101",
    "深圳": "101280601",
    "杭州": "101210101",
    "南京": "101190101",
    "武汉": "101200101",
    "成都": "101270101",
    "西安": "101110101",
    "郑州": "101180101",
    "长沙": "101250101",
    "沈阳": "101070101",
    "济南": "101120101",
    "哈尔滨": "101050101",
    "石家庄": "101090101",
    "太原": "101100101",
    "合肥": "101220101",
    "南昌": "101240101",
    "福州": "101230101",
    "昆明": "101290101",
    "贵阳": "101260101",
    "南宁": "101300101",
    "海口": "101310101",
    "兰州": "101160101",
    "西宁": "101150101",
    "银川": "101170101",
    "乌鲁木齐": "101130101",
    "拉萨": "101140101",
    "呼和浩特": "101080101",
    "长春": "101060101",
    # 其他城市
    "苏州": "101190401",
    "青岛": "101120201",
    "大连": "101070201",
    "厦门": "101230201",
    "宁波": "101210401",
    "无锡": "101190201",
    "常州": "101190401",
    "金坛": "101190401",  # 金坛区属于常州市
}

CITY_ALIASES = {
    "金坛": "金坛区",
    "江阴": "江阴市",
    "宜兴": "宜兴市",
    "溧阳": "溧阳市",
    "常熟": "常熟市",
    "张家港": "张家港市",
    "昆山": "昆山市",
    "太仓": "太仓市",
    "北京": "北京市",
    "上海": "上海市",
    "天津": "天津市",
    "重庆": "重庆市",
    "广州": "广州市",
    "深圳": "深圳市",
    "杭州": "杭州市",
    "南京": "南京市",
    "武汉": "武汉市",
    "成都": "成都市",
    "西安": "西安市",
}


def _normalize_city_name(city_name: str) -> str:
    """标准化城市名称
    
    1. 去除空格
    2. 如果输入本身在映射表中，直接返回
    3. 查别名表
    4. 去除"市"后缀
    5. 返回标准化名称
    """
    if not city_name:
        return city_name
    
    city_name = city_name.strip()
    
    if city_name in CITY_ID_MAP:
        return city_name
    
    if city_name in CITY_ALIASES:
        normalized = CITY_ALIASES[city_name]
        if normalized in CITY_ID_MAP:
            return normalized
        return city_name
    
    if city_name.endswith("市"):
        normalized = city_name[:-1]
        if normalized in CITY_ID_MAP:
            return normalized
    
    return city_name


def _get_city_id(city_name: str) -> Optional[str]:
    """获取城市ID
    
    1. 先标准化城市名称
    2. 查映射表
    """
    normalized = _normalize_city_name(city_name)
    
    if normalized in CITY_ID_MAP:
        return CITY_ID_MAP[normalized]
    
    return None


def _get_api_key(provider: str) -> Optional[str]:
    """获取 API Key"""
    if provider == "qweather":
        return get_api_key("QWEATHER_API_KEY", required=False)
    return None


def _require_api_key(provider: str) -> str:
    """获取必需的 API Key"""
    key = _get_api_key(provider)
    if not key:
        raise ValueError(f"未配置 {provider.upper()}_API_KEY，请在 configs/.env.local 中配置")
    return key


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
            name="get_current_rainfall",
            description="获取当前降雨数据（实时天气）",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称（中文或英文）"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_rainfall_forecast",
            description="获取降雨预报（未来几天）",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    },
                    "days": {
                        "type": "integer",
                        "description": "预报天数 (1-5)",
                        "default": 3,
                        "minimum": 1,
                        "maximum": 5
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_hourly_rainfall",
            description="获取逐小时降雨预报",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    },
                    "hours": {
                        "type": "integer",
                        "description": "预报小时数 (1-24)",
                        "default": 12,
                        "minimum": 1,
                        "maximum": 24
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_rainfall_by_coords",
            description="根据经纬度获取降雨数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "number",
                        "description": "纬度"
                    },
                    "lon": {
                        "type": "number",
                        "description": "经度"
                    }
                },
                "required": ["lat", "lon"]
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
    with ToolCallContext(SERVER_NAME, name, arguments, logger):
        try:
            if name == "get_current_rainfall":
                return await _handle_current_rainfall(arguments)
            elif name == "get_rainfall_forecast":
                return await _handle_rainfall_forecast(arguments)
            elif name == "get_hourly_rainfall":
                return await _handle_hourly_rainfall(arguments)
            elif name == "get_rainfall_by_coords":
                return await _handle_rainfall_by_coords(arguments)
            elif name == "check_api_status":
                return await _handle_check_api_status(arguments)
            else:
                raise ValueError(f"未知工具: {name}")
        except Exception as e:
            logger.error(f"工具 {name} 执行失败: {e}")
            error_dict = format_error_dict(e, SERVER_NAME, name, arguments)
            return [TextContent(
                type="text",
                text=fast_json_dumps(error_dict, ensure_ascii=False)
            )]


async def _handle_current_rainfall(args: Dict[str, Any]) -> List[TextContent]:
    """获取当前降雨数据"""
    city = args["city"]
    provider = "qweather"

    cache_key = f"current_{city}_{provider}"
    cached = _get_cached(cache_key)
    if cached:
        return [TextContent(type="text", text=fast_json_dumps(cached, ensure_ascii=False))]

    async with aiohttp.ClientSession() as session:
        result = await _fetch_qweather_current(session, city)

    _set_cached(cache_key, result)
    return [TextContent(type="text", text=fast_json_dumps(result, ensure_ascii=False, indent=2))]


async def _handle_rainfall_forecast(args: Dict[str, Any]) -> List[TextContent]:
    """获取降雨预报"""
    city = args["city"]
    days = args.get("days", 3)
    provider = "qweather"

    cache_key = f"forecast_{city}_{days}_{provider}"
    cached = _get_cached(cache_key)
    if cached:
        return [TextContent(type="text", text=fast_json_dumps(cached, ensure_ascii=False))]

    async with aiohttp.ClientSession() as session:
        result = await _fetch_qweather_forecast(session, city, days)

    _set_cached(cache_key, result)
    return [TextContent(type="text", text=fast_json_dumps(result, ensure_ascii=False, indent=2))]


async def _handle_hourly_rainfall(args: Dict[str, Any]) -> List[TextContent]:
    """获取逐小时降雨预报"""
    city = args["city"]
    hours = args.get("hours", 12)
    provider = "qweather"

    cache_key = f"hourly_{city}_{hours}_{provider}"
    cached = _get_cached(cache_key)
    if cached:
        return [TextContent(type="text", text=fast_json_dumps(cached, ensure_ascii=False))]

    async with aiohttp.ClientSession() as session:
        result = await _fetch_qweather_hourly(session, city, hours)

    _set_cached(cache_key, result)
    return [TextContent(type="text", text=fast_json_dumps(result, ensure_ascii=False, indent=2))]


async def _handle_rainfall_by_coords(args: Dict[str, Any]) -> List[TextContent]:
    """根据经纬度获取降雨数据"""
    lat = args["lat"]
    lon = args["lon"]
    provider = "qweather"

    cache_key = f"coords_{lat}_{lon}_{provider}"
    cached = _get_cached(cache_key)
    if cached:
        return [TextContent(type="text", text=fast_json_dumps(cached, ensure_ascii=False))]

    async with aiohttp.ClientSession() as session:
        result = await _fetch_qweather_by_coords(session, lat, lon)

    _set_cached(cache_key, result)
    return [TextContent(type="text", text=fast_json_dumps(result, ensure_ascii=False, indent=2))]


async def _handle_check_api_status(args: Dict[str, Any]) -> List[TextContent]:
    """检查 API 状态"""
    status = {
        "success": True,
        "providers": {},
        "timestamp": datetime.now().isoformat()
    }

    qw_key = _get_api_key("qweather")
    status["providers"]["qweather"] = {
        "available": bool(qw_key),
        "has_api_key": bool(qw_key)
    }

    if not qw_key:
        status["warning"] = "未配置 QWEATHER_API_KEY。请在 configs/.env.local 中配置"
        status["note"] = "和风天气免费注册: https://www.qweather.com/"

    return [TextContent(type="text", text=fast_json_dumps(status, ensure_ascii=False, indent=2))]


# ============ 和风天气 API 实现 ============

async def _fetch_qweather_current(session: aiohttp.ClientSession, city: str) -> Dict:
    """获取和风天气当前天气"""
    api_key = _get_api_key("qweather")
    if not api_key:
        raise ValueError("未配置 QWEATHER_API_KEY")

    # 获取城市ID（使用内置映射表）
    city_id = _get_city_id(city)
    if not city_id:
        raise ValueError(f"未找到城市: {city}。支持的城市: {list(CITY_ID_MAP.keys())}")

    url = f"{QWEATHER_BASE_URL}/weather/now"
    params = {
        "location": city_id,
        "key": api_key
    }

    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            error_text = await resp.text()
            raise RuntimeError(f"API 请求失败: {resp.status} - {error_text}")

        data = await resp.json()

    now = data.get("now", {})

    return {
        "success": True,
        "provider": "qweather",
        "city": city,
        "timestamp": datetime.now().isoformat(),
        "current": {
            "temperature": now.get("temp"),
            "humidity": now.get("humidity"),
            "pressure": now.get("pressure"),
            "weather": now.get("text"),
            "weather_code": now.get("icon"),
            "precipitation": now.get("precip"),  # 当前小时降水量(mm)
            "wind_speed": now.get("windSpeed"),
            "wind_direction": now.get("windDir")
        }
    }


async def _fetch_qweather_forecast(session: aiohttp.ClientSession, city: str, days: int) -> Dict:
    """获取和风天气预报"""
    api_key = _get_api_key("qweather")
    if not api_key:
        raise ValueError("未配置 QWEATHER_API_KEY")

    city_id = _get_city_id(city)
    if not city_id:
        raise ValueError(f"未找到城市: {city}。支持的城市: {list(CITY_ID_MAP.keys())}")

    url = f"{QWEATHER_BASE_URL}/weather/{days}d"
    params = {
        "location": city_id,
        "key": api_key
    }

    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            error_text = await resp.text()
            raise RuntimeError(f"API 请求失败: {resp.status} - {error_text}")

        data = await resp.json()

    daily = data.get("daily", [])
    forecasts = []
    for day in daily[:days]:
        forecasts.append({
            "date": day.get("fxDate"),
            "temp_max": day.get("tempMax"),
            "temp_min": day.get("tempMin"),
            "weather_day": day.get("textDay"),
            "weather_night": day.get("textNight"),
            "precipitation": day.get("precip"),  # 降水量(mm)
            "humidity": day.get("humidity"),
            "wind_speed": day.get("windSpeedDay")
        })

    return {
        "success": True,
        "provider": "qweather",
        "city": city,
        "timestamp": datetime.now().isoformat(),
        "forecast_days": days,
        "forecasts": forecasts
    }


async def _fetch_qweather_hourly(session: aiohttp.ClientSession, city: str, hours: int) -> Dict:
    """获取和风天气逐小时预报"""
    api_key = _get_api_key("qweather")
    if not api_key:
        raise ValueError("未配置 QWEATHER_API_KEY")

    city_id = _get_city_id(city)
    if not city_id:
        raise ValueError(f"未找到城市: {city}。支持的城市: {list(CITY_ID_MAP.keys())}")

    url = f"{QWEATHER_BASE_URL}/weather/24h"
    params = {
        "location": city_id,
        "key": api_key
    }

    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            error_text = await resp.text()
            raise RuntimeError(f"API 请求失败: {resp.status} - {error_text}")

        data = await resp.json()

    hourly = data.get("hourly", [])
    forecasts = []
    for hour in hourly[:hours]:
        forecasts.append({
            "datetime": hour.get("fxTime"),
            "temperature": hour.get("temp"),
            "weather": hour.get("text"),
            "precipitation": hour.get("precip"),
            "humidity": hour.get("humidity"),
            "wind_speed": hour.get("windSpeed")
        })

    return {
        "success": True,
        "provider": "qweather",
        "city": city,
        "timestamp": datetime.now().isoformat(),
        "forecast_hours": hours,
        "forecasts": forecasts
    }


async def _fetch_qweather_by_coords(session: aiohttp.ClientSession, lat: float, lon: float) -> Dict:
    """根据坐标获取和风天气"""
    api_key = _get_api_key("qweather")
    if not api_key:
        raise ValueError("未配置 QWEATHER_API_KEY")

    # 坐标转城市ID
    location = f"{lon},{lat}"

    url = f"{QWEATHER_BASE_URL}/weather/now"
    params = {
        "location": location,
        "key": api_key
    }

    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            error_text = await resp.text()
            raise RuntimeError(f"API 请求失败: {resp.status} - {error_text}")

        data = await resp.json()

    now = data.get("now", {})

    return {
        "success": True,
        "provider": "qweather",
        "timestamp": datetime.now().isoformat(),
        "coordinates": {"lat": lat, "lon": lon},
        "current": {
            "temperature": now.get("temp"),
            "humidity": now.get("humidity"),
            "weather": now.get("text"),
            "precipitation": now.get("precip"),
            "wind_speed": now.get("windSpeed")
        }
    }


async def _get_qweather_city_id(session: aiohttp.ClientSession, city_name: str) -> Optional[str]:
    """获取和风天气城市ID"""
    api_key = _get_api_key("qweather")
    if not api_key:
        return None

    # 使用缓存
    cache_key = f"cityid_{city_name}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    url = "https://geoapi.qweather.com/v2/city/lookup"
    params = {
        "location": city_name,
        "key": api_key,
        "number": 1
    }

    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            return None

        data = await resp.json()
        locations = data.get("location", [])
        if locations:
            city_id = locations[0].get("id")
            _set_cached(cache_key, city_id)
            return city_id

    return None


async def main():
    """启动 MCP Server（Windows 兼容版）"""
    logger.info(f"MCP Server [{SERVER_NAME}] 启动中...")
    
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    from mcp.server.stdio import stdio_server as mcp_stdio_server

    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
    
    logger.info(f"MCP Server [{SERVER_NAME}] 已关闭")


if __name__ == "__main__":
    asyncio.run(main())
