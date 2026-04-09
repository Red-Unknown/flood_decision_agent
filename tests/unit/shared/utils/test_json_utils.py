"""
JSON工具模块单元测试
"""

import json
import pytest
from datetime import datetime
from typing import Any

from src.flood_decision_agent.shared.utils.json_utils import (
    fast_json_dumps,
    fast_json_loads,
    fast_json_loads_bytes,
    JSONEncoder,
    benchmark_json_performance,
    get_json_backend,
    dumps,
    loads,
)


class TestFastJsonDumps:
    """测试fast_json_dumps函数"""

    def test_basic_serialization(self):
        """测试基本序列化"""
        data = {"key": "value", "number": 123}
        result = fast_json_dumps(data)
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_unicode_support(self):
        """测试Unicode支持"""
        data = {"name": "测试数据", "emoji": "🎉"}
        result = fast_json_dumps(data, ensure_ascii=False)
        assert "测试数据" in result
        assert "🎉" in result

    def test_indent_formatting(self):
        """测试缩进格式化"""
        data = {"key": "value"}
        result = fast_json_dumps(data, indent=2)
        assert "\n" in result
        assert "  " in result

    def test_sort_keys(self):
        """测试键排序"""
        data = {"z": 1, "a": 2, "m": 3}
        result = fast_json_dumps(data, sort_keys=True)
        # 排序后 'a' 应该在 'z' 之前
        assert result.index('"a"') < result.index('"z"')

    def test_nested_structure(self):
        """测试嵌套结构"""
        data = {
            "level1": {
                "level2": {
                    "level3": [1, 2, 3, {"deep": "value"}]
                }
            }
        }
        result = fast_json_dumps(data)
        restored = json.loads(result)
        assert restored == data

    def test_list_serialization(self):
        """测试列表序列化"""
        data = [1, 2, 3, "string", {"key": "value"}]
        result = fast_json_dumps(data)
        restored = json.loads(result)
        assert restored == data

    def test_empty_data(self):
        """测试空数据"""
        assert fast_json_dumps({}) == "{}"
        assert fast_json_dumps([]) == "[]"
        assert fast_json_dumps("") == '""'

    def test_custom_default(self):
        """测试自定义default函数"""
        class CustomObj:
            def __init__(self, value):
                self.value = value

        data = {"obj": CustomObj("test")}

        def custom_default(obj):
            if isinstance(obj, CustomObj):
                return {"custom_value": obj.value}
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        result = fast_json_dumps(data, default=custom_default)
        restored = json.loads(result)
        assert restored["obj"]["custom_value"] == "test"


class TestFastJsonLoads:
    """测试fast_json_loads函数"""

    def test_basic_deserialization(self):
        """测试基本反序列化"""
        json_str = '{"key": "value", "number": 123}'
        result = fast_json_loads(json_str)
        assert result == {"key": "value", "number": 123}

    def test_deserialize_from_bytes(self):
        """测试从字节反序列化"""
        json_bytes = b'{"key": "value"}'
        result = fast_json_loads(json_bytes)
        assert result == {"key": "value"}

    def test_nested_deserialization(self):
        """测试嵌套结构反序列化"""
        json_str = '{"outer": {"inner": [1, 2, 3]}}'
        result = fast_json_loads(json_str)
        assert result["outer"]["inner"] == [1, 2, 3]

    def test_list_deserialization(self):
        """测试列表反序列化"""
        json_str = '[1, 2, 3, "string", {"key": "value"}]'
        result = fast_json_loads(json_str)
        assert result == [1, 2, 3, "string", {"key": "value"}]


class TestFastJsonLoadsBytes:
    """测试fast_json_loads_bytes函数"""

    def test_bytes_deserialization(self):
        """测试字节反序列化"""
        json_bytes = b'{"key": "value"}'
        result = fast_json_loads_bytes(json_bytes)
        assert result == {"key": "value"}

    def test_unicode_bytes(self):
        """测试Unicode字节"""
        json_str = '{"name": "测试"}'
        json_bytes = json_str.encode("utf-8")
        result = fast_json_loads_bytes(json_bytes)
        assert result["name"] == "测试"


class TestJSONEncoder:
    """测试JSONEncoder类"""

    def test_basic_encoding(self):
        """测试基本编码"""
        encoder = JSONEncoder()
        data = {"key": "value"}
        result = encoder.encode(data)
        assert json.loads(result) == data

    def test_encoding_with_options(self):
        """测试带选项的编码"""
        encoder = JSONEncoder(indent=2, sort_keys=True)
        data = {"z": 1, "a": 2}
        result = encoder.encode(data)
        assert "\n" in result
        assert result.index('"a"') < result.index('"z"')

    def test_iterencode(self):
        """测试iterencode"""
        encoder = JSONEncoder()
        data = {"key": "value"}
        chunks = list(encoder.iterencode(data))
        assert len(chunks) == 1
        assert json.loads(chunks[0]) == data


class TestBenchmark:
    """测试性能对比功能"""

    def test_benchmark_returns_results(self):
        """测试性能对比返回结果"""
        data = {"items": [{"id": i} for i in range(100)]}
        results = benchmark_json_performance(data, iterations=10)

        assert "standard_json_ms" in results
        assert "orjson_ms" in results
        assert "speedup" in results
        assert isinstance(results["standard_json_ms"], float)

    def test_benchmark_with_small_iterations(self):
        """测试小迭代次数"""
        data = {"key": "value"}
        results = benchmark_json_performance(data, iterations=1)
        assert results["standard_json_ms"] >= 0


class TestGetJsonBackend:
    """测试get_json_backend函数"""

    def test_returns_valid_backend(self):
        """测试返回有效的后端名称"""
        backend = get_json_backend()
        assert backend in ["orjson", "standard"]


class TestAliases:
    """测试别名函数"""

    def test_dumps_alias(self):
        """测试dumps别名"""
        data = {"key": "value"}
        result = dumps(data)
        assert json.loads(result) == data

    def test_loads_alias(self):
        """测试loads别名"""
        json_str = '{"key": "value"}'
        result = loads(json_str)
        assert result == {"key": "value"}


class TestRoundTrip:
    """测试序列化-反序列化往返"""

    def test_complex_data_roundtrip(self):
        """测试复杂数据往返"""
        original = {
            "string": "value",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"a": 1, "b": 2},
        }

        json_str = fast_json_dumps(original)
        restored = fast_json_loads(json_str)
        assert restored == original

    def test_large_data_roundtrip(self):
        """测试大数据往返"""
        original = {
            "items": [
                {"id": i, "data": f"item_{i}", "nested": {"value": i * 2}}
                for i in range(1000)
            ]
        }

        json_str = fast_json_dumps(original)
        restored = fast_json_loads(json_str)
        assert restored == original


class TestEdgeCases:
    """测试边界情况"""

    def test_special_characters(self):
        """测试特殊字符"""
        data = {
            "quotes": 'He said "Hello"',
            "backslash": "path\\to\\file",
            "newline": "line1\nline2",
            "tab": "col1\tcol2",
        }
        json_str = fast_json_dumps(data)
        restored = fast_json_loads(json_str)
        assert restored == data

    def test_numeric_types(self):
        """测试数值类型"""
        data = {
            "int": 42,
            "float": 3.14159,
            "negative": -100,
            "zero": 0,
            "large": 1e20,
            "small": 1e-20,
        }
        json_str = fast_json_dumps(data)
        restored = fast_json_loads(json_str)
        assert restored["int"] == 42
        assert abs(restored["float"] - 3.14159) < 0.00001

    def test_boolean_and_null(self):
        """测试布尔值和null"""
        data = {"true": True, "false": False, "null": None}
        json_str = fast_json_dumps(data)
        restored = fast_json_loads(json_str)
        assert restored["true"] is True
        assert restored["false"] is False
        assert restored["null"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
