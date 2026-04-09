"""Data Hub MCP Server

数据中枢服务 - 提供统一的数据获取、聚合和管理功能
支持：和风天气

环境变量:
    QWEATHER_API_KEY: 和风天气 API Key
    KIMI_API_KEY: Kimi API Key（用于启动检查）
"""

import asyncio
import os
import platform
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from urllib.parse import urlencode

import aiohttp
from mcp.server import Server
from mcp.types import TextContent, Tool

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
from flood_decision_agent.infrastructure.config_loader import get_api_key

# 设置环境变量（Windows 兼容）
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# 创建 MCP Server
server = Server("flood-agent-data-hub")

# 和风天气配置
QWEATHER_BASE_URL = "https://m92k5pcp5g.re.qweatherapi.com/v7"

# 缓存配置
CACHE_TIMEOUT = 300  # 5分钟缓存


# ============== 数据模型定义 ==============

class DataSourceType(str, Enum):
    """数据源类型"""
    QWEATHER = "qweather"
    SIMULATED = "simulated"


class DataType(str, Enum):
    """数据类型"""
    RAINFALL = "rainfall"
    HYDROLOGICAL = "hydrological"
    METEOROLOGICAL = "meteorological"


@dataclass
class DataSourceStatus:
    """数据源状态"""
    name: str
    available: bool
    has_api_key: bool
    last_check: str
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class UnifiedDataResponse:
    """统一数据返回格式"""
    success: bool
    data_type: str
    source: str
    timestamp: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AggregatedData:
    """聚合数据结果"""
    success: bool
    query_id: str
    timestamp: str
    data_type: str
    sources_used: List[str]
    sources_failed: List[str]
    aggregated_data: Dict[str, Any]
    confidence_score: float  # 0-1，基于成功数据源比例


# ============== 缓存管理器 ==============

class DataCache:
    """数据缓存管理器"""
    
    def __init__(self, timeout: int = CACHE_TIMEOUT):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._timeout = timeout
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key in self._cache:
            timestamp = self._timestamps.get(key, 0)
            if datetime.now().timestamp() - timestamp < self._timeout:
                return self._cache[key]
            # 过期清理
            self.delete(key)
        return None
    
    def set(self, key: str, data: Any):
        """设置缓存数据"""
        self._cache[key] = data
        self._timestamps[key] = datetime.now().timestamp()
    
    def delete(self, key: str):
        """删除缓存"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        now = datetime.now().timestamp()
        valid_count = sum(
            1 for key, ts in self._timestamps.items()
            if now - ts < self._timeout
        )
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_count,
            "expired_entries": len(self._cache) - valid_count,
            "timeout_seconds": self._timeout
        }


# 全局缓存实例
_data_cache = DataCache()


# ============== 数据源管理器 ==============

class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self):
        self._status: Dict[str, DataSourceStatus] = {}
        self._last_check: Optional[datetime] = None
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """获取 API Key"""
        if provider == "qweather":
            return get_api_key("QWEATHER_API_KEY", required=False)
        return None
    
    async def check_source_status(
        self, 
        session: aiohttp.ClientSession, 
        provider: str
    ) -> DataSourceStatus:
        """检查数据源状态"""
        api_key = self.get_api_key(provider)
        has_key = bool(api_key)
        
        if not has_key:
            return DataSourceStatus(
                name=provider,
                available=False,
                has_api_key=False,
                last_check=datetime.now().isoformat(),
                error_message="未配置 API Key"
            )
        
        start_time = datetime.now()
        try:
            if provider == "qweather":
                url = f"{QWEATHER_BASE_URL}/weather/now"
                params = {"location": "101010100", "key": api_key}
                async with session.get(url, params=params, timeout=10) as resp:
                    available = resp.status == 200
                    error_msg = None if available else f"HTTP {resp.status}"
            else:
                available = False
                error_msg = "未知的数据源"
            
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            
        except Exception as e:
            available = False
            error_msg = str(e)
            latency = None
        
        status = DataSourceStatus(
            name=provider,
            available=available,
            has_api_key=has_key,
            last_check=datetime.now().isoformat(),
            latency_ms=latency,
            error_message=error_msg
        )
        self._status[provider] = status
        return status
    
    async def check_all_status(self) -> Dict[str, DataSourceStatus]:
        """检查所有数据源状态"""
        async with aiohttp.ClientSession() as session:
            providers = ["qweather"]
            tasks = [self.check_source_status(session, p) for p in providers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for provider, result in zip(providers, results):
                if isinstance(result, Exception):
                    self._status[provider] = DataSourceStatus(
                        name=provider,
                        available=False,
                        has_api_key=bool(self.get_api_key(provider)),
                        last_check=datetime.now().isoformat(),
                        error_message=str(result)
                    )
        
        self._last_check = datetime.now()
        return self._status
    
    def get_available_sources(self) -> List[str]:
        """获取可用的数据源列表"""
        return [
            name for name, status in self._status.items()
            if status.available
        ]


# 全局数据源管理器
_source_manager = DataSourceManager()


# ============== 城市ID映射 ==============

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
}


def _get_city_id(city_name: str) -> Optional[str]:
    """获取城市ID"""
    if city_name in CITY_ID_MAP:
        return CITY_ID_MAP[city_name]
    if city_name.endswith("市"):
        city_name = city_name[:-1]
        if city_name in CITY_ID_MAP:
            return CITY_ID_MAP[city_name]
    return None


# ============== 数据获取器 ==============

class RainfallDataFetcher:
    """降雨数据获取器"""
    
    @staticmethod
    async def fetch_openweather(
        session: aiohttp.ClientSession,
        city: str,
        api_key: str
    ) -> UnifiedDataResponse:
        """从 OpenWeatherMap 获取降雨数据"""
        url = f"{OPENWEATHER_BASE_URL}/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return UnifiedDataResponse(
                    success=False,
                    data_type="rainfall",
                    source="openweather",
                    timestamp=datetime.now().isoformat(),
                    data={},
                    error=f"API 请求失败: {resp.status} - {error_text}"
                )
            
            data = await resp.json()
        
        rain_data = data.get("rain", {})
        weather = data.get("weather", [{}])[0]
        
        return UnifiedDataResponse(
            success=True,
            data_type="rainfall",
            source="openweather",
            timestamp=datetime.now().isoformat(),
            data={
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "coordinates": {
                    "lat": data.get("coord", {}).get("lat"),
                    "lon": data.get("coord", {}).get("lon")
                },
                "current": {
                    "temperature": data.get("main", {}).get("temp"),
                    "humidity": data.get("main", {}).get("humidity"),
                    "pressure": data.get("main", {}).get("pressure"),
                    "weather": weather.get("description"),
                    "weather_code": weather.get("id"),
                    "rain_1h": rain_data.get("1h", 0),
                    "rain_3h": rain_data.get("3h", 0),
                }
            },
            metadata={
                "provider": "openweather",
                "api_version": "2.5"
            }
        )
    
    @staticmethod
    async def fetch_qweather(
        session: aiohttp.ClientSession,
        city: str,
        api_key: str
    ) -> UnifiedDataResponse:
        """从和风天气获取降雨数据"""
        city_id = _get_city_id(city)
        if not city_id:
            return UnifiedDataResponse(
                success=False,
                data_type="rainfall",
                source="qweather",
                timestamp=datetime.now().isoformat(),
                data={},
                error=f"未找到城市: {city}"
            )
        
        url = f"{QWEATHER_BASE_URL}/weather/now"
        params = {"location": city_id, "key": api_key}
        
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return UnifiedDataResponse(
                    success=False,
                    data_type="rainfall",
                    source="qweather",
                    timestamp=datetime.now().isoformat(),
                    data={},
                    error=f"API 请求失败: {resp.status} - {error_text}"
                )
            
            data = await resp.json()
        
        now = data.get("now", {})
        
        return UnifiedDataResponse(
            success=True,
            data_type="rainfall",
            source="qweather",
            timestamp=datetime.now().isoformat(),
            data={
                "city": city,
                "current": {
                    "temperature": now.get("temp"),
                    "humidity": now.get("humidity"),
                    "pressure": now.get("pressure"),
                    "weather": now.get("text"),
                    "weather_code": now.get("icon"),
                    "precipitation": now.get("precip"),
                    "wind_speed": now.get("windSpeed"),
                    "wind_direction": now.get("windDir")
                }
            },
            metadata={
                "provider": "qweather",
                "city_id": city_id
            }
        )


class HydrologicalDataFetcher:
    """水文数据获取器（模拟/预留）"""
    
    @staticmethod
    async def fetch_simulated(
        station_id: str,
        data_type: str = "water_level"
    ) -> UnifiedDataResponse:
        """获取模拟水文数据"""
        # 生成模拟数据
        import random
        
        base_values = {
            "water_level": 85.0,
            "flow_rate": 1200.0,
            "reservoir_storage": 5000000.0
        }
        
        base = base_values.get(data_type, 100.0)
        current_value = base + random.uniform(-5, 5)
        
        # 生成历史数据点
        history = []
        for i in range(24):
            history.append({
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "value": base + random.uniform(-10, 10)
            })
        
        return UnifiedDataResponse(
            success=True,
            data_type="hydrological",
            source="simulated",
            timestamp=datetime.now().isoformat(),
            data={
                "station_id": station_id,
                "data_type": data_type,
                "current_value": round(current_value, 2),
                "unit": "m" if data_type == "water_level" else "m³/s" if data_type == "flow_rate" else "m³",
                "history": history,
                "trend": "stable"
            },
            metadata={
                "data_source": "simulated",
                "note": "此为模拟数据，用于测试和演示"
            }
        )


# ============== 数据聚合器 ==============

class DataAggregator:
    """数据聚合器"""
    
    @staticmethod
    async def aggregate_rainfall_data(
        city: str,
        sources: Optional[List[str]] = None
    ) -> AggregatedData:
        """聚合多数据源降雨数据"""
        query_id = f"RAI_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(city) % 10000:04d}"
        
        if sources is None:
            sources = ["openweather", "qweather"]
        
        results: List[UnifiedDataResponse] = []
        sources_used = []
        sources_failed = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source in sources:
                api_key = _source_manager.get_api_key(source)
                if not api_key:
                    sources_failed.append(f"{source}: 未配置 API Key")
                    continue
                
                if source == "openweather":
                    task = RainfallDataFetcher.fetch_openweather(session, city, api_key)
                elif source == "qweather":
                    task = RainfallDataFetcher.fetch_qweather(session, city, api_key)
                else:
                    sources_failed.append(f"{source}: 未知数据源")
                    continue
                
                tasks.append((source, task))
            
            # 并行执行所有请求
            for source, task in tasks:
                try:
                    result = await task
                    results.append(result)
                    if result.success:
                        sources_used.append(source)
                    else:
                        sources_failed.append(f"{source}: {result.error}")
                except Exception as e:
                    sources_failed.append(f"{source}: {str(e)}")
        
        # 聚合数据
        aggregated = DataAggregator._merge_rainfall_data(results)
        
        # 计算置信度
        total_sources = len(sources_used) + len([s for s in sources_failed if ":" in s])
        confidence = len(sources_used) / max(total_sources, 1)
        
        return AggregatedData(
            success=len(sources_used) > 0,
            query_id=query_id,
            timestamp=datetime.now().isoformat(),
            data_type="rainfall",
            sources_used=sources_used,
            sources_failed=sources_failed,
            aggregated_data=aggregated,
            confidence_score=round(confidence, 2)
        )
    
    @staticmethod
    def _merge_rainfall_data(results: List[UnifiedDataResponse]) -> Dict[str, Any]:
        """合并降雨数据"""
        merged = {
            "city": None,
            "temperature": {},
            "humidity": {},
            "precipitation": {},
            "weather": {},
            "sources": []
        }
        
        temps = []
        humidities = []
        precipitations = []
        
        for result in results:
            if not result.success:
                continue
            
            merged["sources"].append(result.source)
            data = result.data
            
            if merged["city"] is None:
                merged["city"] = data.get("city") or data.get("location")
            
            current = data.get("current", {})
            
            # 温度
            temp = current.get("temperature")
            if temp is not None:
                temps.append(float(temp))
                merged["temperature"][result.source] = temp
            
            # 湿度
            humidity = current.get("humidity")
            if humidity is not None:
                humidities.append(float(humidity))
                merged["humidity"][result.source] = humidity
            
            # 降水量
            precip = current.get("precipitation") or current.get("rain_1h", 0)
            if precip is not None:
                precipitations.append(float(precip))
                merged["precipitation"][result.source] = precip
            
            # 天气描述
            weather = current.get("weather")
            if weather:
                merged["weather"][result.source] = weather
        
        # 计算平均值
        if temps:
            merged["temperature_avg"] = round(sum(temps) / len(temps), 1)
        if humidities:
            merged["humidity_avg"] = round(sum(humidities) / len(humidities), 1)
        if precipitations:
            merged["precipitation_avg"] = round(sum(precipitations) / len(precipitations), 2)
            merged["precipitation_max"] = max(precipitations)
        
        return merged


# ============== MCP 工具定义 ==============

@server.list_tools()
async def list_tools() -> List[Tool]:
    """定义可用工具"""
    return [
        Tool(
            name="get_rainfall_data",
            description="获取降雨数据（支持多数据源）",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称（中文）"
                    },
                    "provider": {
                        "type": "string",
                        "description": "数据源",
                        "enum": ["openweather", "qweather", "auto"],
                        "default": "auto"
                    },
                    "use_cache": {
                        "type": "boolean",
                        "description": "是否使用缓存",
                        "default": True
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_hydrological_data",
            description="获取水文数据（水位、流量等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "station_id": {
                        "type": "string",
                        "description": "测站ID"
                    },
                    "data_type": {
                        "type": "string",
                        "description": "数据类型",
                        "enum": ["water_level", "flow_rate", "reservoir_storage"],
                        "default": "water_level"
                    },
                    "hours": {
                        "type": "integer",
                        "description": "历史数据小时数",
                        "default": 24,
                        "minimum": 1,
                        "maximum": 168
                    }
                },
                "required": ["station_id"]
            }
        ),
        Tool(
            name="aggregate_data_sources",
            description="聚合多数据源获取综合数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_type": {
                        "type": "string",
                        "description": "数据类型",
                        "enum": ["rainfall", "hydrological"],
                        "default": "rainfall"
                    },
                    "city": {
                        "type": "string",
                        "description": "城市名称（降雨数据需要）"
                    },
                    "sources": {
                        "type": "array",
                        "description": "数据源列表",
                        "items": {"type": "string"},
                        "default": ["openweather", "qweather"]
                    }
                },
                "required": ["data_type"]
            }
        ),
        Tool(
            name="check_data_sources_status",
            description="检查所有数据源的状态和可用性",
            inputSchema={
                "type": "object",
                "properties": {
                    "check_connectivity": {
                        "type": "boolean",
                        "description": "是否检查网络连通性",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="get_cache_stats",
            description="获取数据缓存统计信息",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="clear_cache",
            description="清空数据缓存",
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
        if name == "get_rainfall_data":
            return await _handle_get_rainfall_data(arguments)
        elif name == "get_hydrological_data":
            return await _handle_get_hydrological_data(arguments)
        elif name == "aggregate_data_sources":
            return await _handle_aggregate_data_sources(arguments)
        elif name == "check_data_sources_status":
            return await _handle_check_data_sources_status(arguments)
        elif name == "get_cache_stats":
            return await _handle_get_cache_stats(arguments)
        elif name == "clear_cache":
            return await _handle_clear_cache(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
    except Exception as e:
        return [TextContent(
            type="text",
            text=_json_dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            })
        )]


def _json_dumps(obj: Any, indent: Optional[int] = None) -> str:
    """JSON 序列化辅助函数"""
    import json
    return json.dumps(obj, ensure_ascii=False, indent=indent, default=str)


# ============== 工具处理函数 ==============

async def _handle_get_rainfall_data(args: Dict[str, Any]) -> List[TextContent]:
    """处理获取降雨数据请求"""
    city = args["city"]
    provider = args.get("provider", "auto")
    use_cache = args.get("use_cache", True)
    
    # 自动选择 provider
    if provider == "auto":
        if _source_manager.get_api_key("openweather"):
            provider = "openweather"
        else:
            provider = "qweather"
    
    # 检查缓存
    cache_key = f"rainfall_{city}_{provider}"
    if use_cache:
        cached = _data_cache.get(cache_key)
        if cached:
            cached["from_cache"] = True
            return [TextContent(type="text", text=_json_dumps(cached, indent=2))]
    
    # 获取 API Key
    api_key = _source_manager.get_api_key(provider)
    if not api_key:
        return [TextContent(
            type="text",
            text=_json_dumps({
                "success": False,
                "error": f"未配置 {provider} 的 API Key",
                "timestamp": datetime.now().isoformat()
            })
        )]
    
    # 获取数据
    async with aiohttp.ClientSession() as session:
        if provider == "openweather":
            result = await RainfallDataFetcher.fetch_openweather(session, city, api_key)
        elif provider == "qweather":
            result = await RainfallDataFetcher.fetch_qweather(session, city, api_key)
        else:
            return [TextContent(
                type="text",
                text=_json_dumps({
                    "success": False,
                    "error": f"不支持的 provider: {provider}",
                    "timestamp": datetime.now().isoformat()
                })
            )]
    
    # 缓存结果
    result_dict = result.to_dict()
    if result.success and use_cache:
        _data_cache.set(cache_key, result_dict)
    
    return [TextContent(type="text", text=_json_dumps(result_dict, indent=2))]


async def _handle_get_hydrological_data(args: Dict[str, Any]) -> List[TextContent]:
    """处理获取水文数据请求"""
    station_id = args["station_id"]
    data_type = args.get("data_type", "water_level")
    hours = args.get("hours", 24)
    
    # 目前使用模拟数据
    result = await HydrologicalDataFetcher.fetch_simulated(station_id, data_type)
    
    # 裁剪历史数据
    result_dict = result.to_dict()
    if "data" in result_dict and "history" in result_dict["data"]:
        result_dict["data"]["history"] = result_dict["data"]["history"][:hours]
    
    return [TextContent(type="text", text=_json_dumps(result_dict, indent=2))]


async def _handle_aggregate_data_sources(args: Dict[str, Any]) -> List[TextContent]:
    """处理聚合数据源请求"""
    data_type = args.get("data_type", "rainfall")
    sources = args.get("sources", ["openweather", "qweather"])
    
    if data_type == "rainfall":
        city = args.get("city")
        if not city:
            return [TextContent(
                type="text",
                text=_json_dumps({
                    "success": False,
                    "error": "降雨数据聚合需要提供 city 参数",
                    "timestamp": datetime.now().isoformat()
                })
            )]
        
        result = await DataAggregator.aggregate_rainfall_data(city, sources)
        return [TextContent(
            type="text",
            text=_json_dumps({
                "success": result.success,
                "query_id": result.query_id,
                "timestamp": result.timestamp,
                "data_type": result.data_type,
                "sources_used": result.sources_used,
                "sources_failed": result.sources_failed,
                "confidence_score": result.confidence_score,
                "data": result.aggregated_data
            }, indent=2)
        )]
    else:
        return [TextContent(
            type="text",
            text=_json_dumps({
                "success": False,
                "error": f"暂不支持的数据类型聚合: {data_type}",
                "timestamp": datetime.now().isoformat()
            })
        )]


async def _handle_check_data_sources_status(args: Dict[str, Any]) -> List[TextContent]:
    """处理检查数据源状态请求"""
    check_connectivity = args.get("check_connectivity", True)
    
    if check_connectivity:
        statuses = await _source_manager.check_all_status()
    else:
        statuses = _source_manager._status
    
    status_list = []
    for name, status in statuses.items():
        status_list.append({
            "name": status.name,
            "available": status.available,
            "has_api_key": status.has_api_key,
            "last_check": status.last_check,
            "latency_ms": status.latency_ms,
            "error_message": status.error_message
        })
    
    # 检查环境变量配置
    env_status = {
        "QWEATHER_API_KEY": bool(get_api_key("QWEATHER_API_KEY", required=False)),
        "KIMI_API_KEY": bool(get_api_key("KIMI_API_KEY", required=False))
    }
    
    return [TextContent(
        type="text",
        text=_json_dumps({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "sources": status_list,
            "environment_variables": env_status,
            "cache_stats": _data_cache.get_stats()
        }, indent=2)
    )]


async def _handle_get_cache_stats(args: Dict[str, Any]) -> List[TextContent]:
    """处理获取缓存统计请求"""
    stats = _data_cache.get_stats()
    return [TextContent(
        type="text",
        text=_json_dumps({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "cache_stats": stats
        }, indent=2)
    )]


async def _handle_clear_cache(args: Dict[str, Any]) -> List[TextContent]:
    """处理清空缓存请求"""
    _data_cache.clear()
    return [TextContent(
        type="text",
        text=_json_dumps({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "message": "缓存已清空"
        }, indent=2)
    )]


# ============== 启动检查 ==============

def _check_environment():
    """检查环境变量配置"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("需要kimi_api_key")
        exit(1)


# ============== 主函数 ==============

async def main():
    """启动 MCP Server（Windows 兼容版）"""
    # 检查环境变量
    _check_environment()
    
    # Windows 兼容设置
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 局部导入 stdio_server
    from mcp.server.stdio import stdio_server as mcp_stdio_server
    
    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
