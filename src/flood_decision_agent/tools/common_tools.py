"""常用工具库 - Agent可自由选用的基础工具"""

from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.tools.registry import ToolMetadata, ToolRegistry, get_tool_registry


class CommonTools:
    """常用工具集合"""

    @staticmethod
    def register_all(registry: Optional[ToolRegistry] = None):
        """注册所有常用工具到注册中心
        
        Args:
            registry: 指定的注册中心，为None时使用全局注册中心
        """
        target_registry = registry or get_tool_registry()
        CommonTools._register_data_query_tools(target_registry)
        CommonTools._register_compute_tools(target_registry)
        CommonTools._register_format_tools(target_registry)
        CommonTools._register_log_tools(target_registry)
        return target_registry

    @staticmethod
    def _register_data_query_tools(registry: ToolRegistry):
        """注册数据查询类工具"""

        def get_current_time(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """获取当前时间"""
            now = datetime.now()
            return {
                "current_time": now.isoformat(),
                "timestamp": time.time(),
                "date": now.date().isoformat(),
            }

        registry.register(
            "get_current_time",
            get_current_time,
            ToolMetadata(
                name="get_current_time",
                description="获取当前系统时间",
                task_types={"data_query", "time"},
                priority=10,
                output_keys={"current_time", "timestamp"}
            )
        )

        def query_data_pool(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """从数据池查询数据"""
            key = config.get("key")
            default = config.get("default")
            value = data_pool.get(key, default)
            return {
                "data": value,
                "found": value is not None,
                "key": key,
            }

        registry.register(
            "query_data_pool",
            query_data_pool,
            ToolMetadata(
                name="query_data_pool",
                description="查询共享数据池中的数据",
                task_types={"data_query"},
                priority=20,
                config_schema={
                    "required": ["key"],
                    "properties": {
                        "key": {"type": "string"},
                        "default": {"type": "any"}
                    }
                },
                required_keys=set(),
                output_keys={"data", "found"}
            )
        )

        def list_data_pool_keys(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """列出数据池中的所有key"""
            keys = list(data_pool._data.keys()) if hasattr(data_pool, '_data') else []
            return {
                "keys": keys,
                "count": len(keys),
            }

        registry.register(
            "list_data_pool_keys",
            list_data_pool_keys,
            ToolMetadata(
                name="list_data_pool_keys",
                description="列出数据池中所有可用的key",
                task_types={"data_query"},
                priority=30,
                output_keys={"keys", "count"}
            )
        )

    @staticmethod
    def _register_compute_tools(registry: ToolRegistry):
        """注册计算类工具"""

        def simple_calculator(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """简单计算器"""
            op = config.get("operation")
            a = float(config.get("a", 0))
            b = float(config.get("b", 0))

            if op == "add":
                result = a + b
            elif op == "subtract":
                result = a - b
            elif op == "multiply":
                result = a * b
            elif op == "divide":
                result = a / b if b != 0 else float('inf')
            else:
                raise ValueError(f"不支持的操作: {op}")

            return {
                "result": result,
                "operation": op,
                "a": a,
                "b": b,
            }

        registry.register(
            "simple_calculator",
            simple_calculator,
            ToolMetadata(
                name="simple_calculator",
                description="简单计算器，支持加减乘除",
                task_types={"compute", "math"},
                priority=10,
                config_schema={
                    "required": ["operation", "a", "b"],
                    "properties": {
                        "operation": {"enum": ["add", "subtract", "multiply", "divide"]},
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    }
                },
                output_keys={"result", "operation"}
            )
        )

        def dataframe_stats(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """计算DataFrame统计信息"""
            data_key = config.get("data_key")
            df = data_pool.get(data_key)

            if df is None:
                return {"stats": None, "error": f"数据 {data_key} 不存在"}

            if not isinstance(df, pd.DataFrame):
                return {"stats": None, "error": f"数据 {data_key} 不是DataFrame"}

            columns = config.get("columns", df.columns.tolist())
            stats = df[columns].describe().to_dict()

            return {
                "stats": stats,
                "count": len(df),
                "columns": columns,
            }

        registry.register(
            "dataframe_stats",
            dataframe_stats,
            ToolMetadata(
                name="dataframe_stats",
                description="计算DataFrame的基本统计信息",
                task_types={"compute", "statistics"},
                priority=20,
                config_schema={
                    "required": ["data_key"],
                    "properties": {
                        "data_key": {"type": "string"},
                        "columns": {"type": "array", "items": {"type": "string"}}
                    }
                },
                output_keys={"stats", "count", "columns"}
            )
        )

    @staticmethod
    def _register_format_tools(registry: ToolRegistry):
        """注册格式转换类工具"""

        def to_json(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """转换为JSON"""
            data_key = config.get("data_key")
            indent = config.get("indent", 2)
            data = data_pool.get(data_key)

            try:
                # 处理DataFrame
                if isinstance(data, pd.DataFrame):
                    json_str = data.to_json(orient='records', indent=indent, force_ascii=False)
                else:
                    json_str = json.dumps(data, indent=indent, ensure_ascii=False, default=str)

                return {
                    "json_string": json_str,
                    "success": True,
                    "data_key": data_key,
                }
            except Exception as e:
                return {
                    "json_string": None,
                    "success": False,
                    "error": str(e),
                }

        registry.register(
            "to_json",
            to_json,
            ToolMetadata(
                name="to_json",
                description="将数据转换为JSON字符串",
                task_types={"format", "convert"},
                priority=10,
                config_schema={
                    "required": ["data_key"],
                    "properties": {
                        "data_key": {"type": "string"},
                        "indent": {"type": "integer", "default": 2}
                    }
                },
                output_keys={"json_string", "success"}
            )
        )

        def format_timestamp(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """格式化时间戳"""
            timestamp = config.get("timestamp")
            fmt = config.get("format", "%Y-%m-%d %H:%M:%S")

            try:
                dt = datetime.fromtimestamp(timestamp)
                formatted = dt.strftime(fmt)
                return {
                    "formatted_time": formatted,
                    "timestamp": timestamp,
                    "format": fmt,
                }
            except Exception as e:
                return {
                    "formatted_time": None,
                    "error": str(e),
                }

        registry.register(
            "format_timestamp",
            format_timestamp,
            ToolMetadata(
                name="format_timestamp",
                description="将时间戳格式化为可读字符串",
                task_types={"format", "time"},
                priority=20,
                config_schema={
                    "required": ["timestamp"],
                    "properties": {
                        "timestamp": {"type": "number"},
                        "format": {"type": "string", "default": "%Y-%m-%d %H:%M:%S"}
                    }
                },
                output_keys={"formatted_time", "timestamp"}
            )
        )

    @staticmethod
    def _register_log_tools(registry: ToolRegistry):
        """注册日志类工具"""

        def log_message(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """记录日志"""
            level = config.get("level", "info")
            message = config.get("message", "")
            context = config.get("context", {})

            # 这里可以接入实际的日志系统
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level.upper(),
                "message": message,
                "context": context,
            }

            return {
                "logged": True,
                "timestamp": log_entry["timestamp"],
                "log_entry": log_entry,
            }

        registry.register(
            "log_message",
            log_message,
            ToolMetadata(
                name="log_message",
                description="记录日志消息",
                task_types={"log", "debug"},
                priority=10,
                config_schema={
                    "required": ["level", "message"],
                    "properties": {
                        "level": {"enum": ["debug", "info", "warning", "error"]},
                        "message": {"type": "string"},
                        "context": {"type": "object"}
                    }
                },
                output_keys={"logged", "timestamp"}
            )
        )

        def create_execution_report(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """创建执行报告"""
            title = config.get("title", "执行报告")
            metrics = config.get("metrics", {})
            results = config.get("results", {})

            report = {
                "report_id": f"rpt_{int(time.time())}",
                "title": title,
                "generated_at": datetime.now().isoformat(),
                "metrics": metrics,
                "results": results,
                "summary": {
                    "total_metrics": len(metrics),
                    "total_results": len(results),
                }
            }

            return {
                "report": report,
                "report_id": report["report_id"],
            }

        registry.register(
            "create_execution_report",
            create_execution_report,
            ToolMetadata(
                name="create_execution_report",
                description="创建执行报告",
                task_types={"log", "report"},
                priority=30,
                config_schema={
                    "properties": {
                        "title": {"type": "string", "default": "执行报告"},
                        "metrics": {"type": "object"},
                        "results": {"type": "object"}
                    }
                },
                output_keys={"report", "report_id"}
            )
        )
