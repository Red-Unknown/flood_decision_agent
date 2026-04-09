"""
高性能JSON序列化工具模块

提供基于orjson的高性能JSON序列化/反序列化功能，
当orjson不可用时自动回退到标准json模块。
"""

import json
import time
from typing import Any, Dict, List, Union, Optional
from functools import wraps

# 尝试导入orjson，如果不可用则使用标准json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


def fast_json_dumps(
    obj: Any,
    ensure_ascii: bool = False,
    indent: Optional[int] = None,
    sort_keys: bool = False,
    default: Optional[callable] = None,
) -> str:
    """
    高性能JSON序列化

    优先使用orjson进行序列化，如果orjson不可用则回退到标准json。
    orjson通常比标准json快5-10倍。

    Args:
        obj: 要序列化的对象
        ensure_ascii: 是否确保ASCII编码（orjson中对应NON_ASCII选项的反向）
        indent: 缩进空格数，None表示不格式化
        sort_keys: 是否按键排序
        default: 处理不可序列化对象的默认函数

    Returns:
        JSON字符串

    Example:
        >>> data = {"key": "value", "number": 123}
        >>> json_str = fast_json_dumps(data, indent=2)
        >>> print(json_str)
        {
          "key": "value",
          "number": 123
        }
    """
    if HAS_ORJSON:
        # 构建orjson选项
        option = 0
        if ensure_ascii:
            option |= orjson.OPT_NON_ASCII
        if indent is not None:
            option |= orjson.OPT_INDENT_2
        if sort_keys:
            option |= orjson.OPT_SORT_KEYS

        # 使用orjson进行序列化
        result = orjson.dumps(obj, option=option, default=default)
        return result.decode("utf-8")
    else:
        # 回退到标准json
        return json.dumps(
            obj,
            ensure_ascii=ensure_ascii,
            indent=indent,
            sort_keys=sort_keys,
            default=default,
        )


def fast_json_loads(s: Union[str, bytes]) -> Any:
    """
    高性能JSON反序列化

    优先使用orjson进行反序列化，如果orjson不可用则回退到标准json。

    Args:
        s: JSON字符串或字节

    Returns:
        反序列化后的Python对象

    Example:
        >>> json_str = '{"key": "value", "number": 123}'
        >>> data = fast_json_loads(json_str)
        >>> print(data["key"])
        value
    """
    if HAS_ORJSON:
        # orjson支持str和bytes输入
        return orjson.loads(s)
    else:
        return json.loads(s)


def fast_json_loads_bytes(s: bytes) -> Any:
    """
    从字节进行高性能JSON反序列化

    orjson在处理bytes时性能更好，此函数优先使用bytes输入。

    Args:
        s: JSON字节串

    Returns:
        反序列化后的Python对象
    """
    if HAS_ORJSON:
        return orjson.loads(s)
    else:
        return json.loads(s.decode("utf-8"))


class JSONEncoder:
    """
    高性能JSON编码器类

    提供与标准json.JSONEncoder类似的接口，但使用orjson实现。
    """

    def __init__(
        self,
        ensure_ascii: bool = False,
        indent: Optional[int] = None,
        sort_keys: bool = False,
        default: Optional[callable] = None,
    ):
        self.ensure_ascii = ensure_ascii
        self.indent = indent
        self.sort_keys = sort_keys
        self.default = default

    def encode(self, obj: Any) -> str:
        """编码对象为JSON字符串"""
        return fast_json_dumps(
            obj,
            ensure_ascii=self.ensure_ascii,
            indent=self.indent,
            sort_keys=self.sort_keys,
            default=self.default,
        )

    def iterencode(self, obj: Any):
        """
        迭代编码（为兼容性提供，实际不迭代）

        注意：orjson不支持真正的迭代编码，此方法一次性返回结果
        """
        yield self.encode(obj)


def benchmark_json_performance(
    data: Any, iterations: int = 1000
) -> Dict[str, float]:
    """
    对比orjson和标准json的性能

    Args:
        data: 要测试的数据
        iterations: 迭代次数

    Returns:
        包含性能对比结果的字典
    """
    results = {}

    # 测试标准json
    start = time.time()
    for _ in range(iterations):
        json_str = json.dumps(data, ensure_ascii=False)
        json.loads(json_str)
    std_time = time.time() - start
    results["standard_json_ms"] = std_time * 1000

    # 测试orjson（如果可用）
    if HAS_ORJSON:
        start = time.time()
        for _ in range(iterations):
            json_str = fast_json_dumps(data)
            fast_json_loads(json_str)
        fast_time = time.time() - start
        results["orjson_ms"] = fast_time * 1000
        results["speedup"] = std_time / fast_time if fast_time > 0 else float("inf")
    else:
        results["orjson_ms"] = None
        results["speedup"] = 1.0
        results["note"] = "orjson not available"

    return results


def get_json_backend() -> str:
    """
    获取当前使用的JSON后端

    Returns:
        "orjson" 或 "standard"
    """
    return "orjson" if HAS_ORJSON else "standard"


# 为兼容性提供别名
dumps = fast_json_dumps
loads = fast_json_loads


if __name__ == "__main__":
    # 运行性能测试
    print(f"JSON Backend: {get_json_backend()}")
    print("-" * 50)

    # 测试数据
    test_data = {
        "name": "测试数据",
        "value": 12345,
        "nested": {"key1": "value1", "key2": [1, 2, 3, 4, 5]},
        "items": [{"id": i, "data": f"item_{i}"} for i in range(100)],
    }

    # 运行性能对比
    results = benchmark_json_performance(test_data, iterations=1000)

    print(f"Standard JSON: {results['standard_json_ms']:.2f} ms")
    if results["orjson_ms"]:
        print(f"orjson: {results['orjson_ms']:.2f} ms")
        print(f"Speedup: {results['speedup']:.2f}x")
    else:
        print(f"Note: {results['note']}")

    # 测试序列化/反序列化正确性
    print("\n" + "-" * 50)
    print("Testing serialization correctness:")

    json_str = fast_json_dumps(test_data, indent=2)
    restored = fast_json_loads(json_str)

    if restored == test_data:
        print("[OK] Serialization/Deserialization correct")
    else:
        print("[ERR] Data mismatch!")

    # 测试大数据量
    print("\n" + "-" * 50)
    print("Testing large data serialization:")

    large_data = {"items": [{"id": i, "data": "x" * 100} for i in range(10000)]}

    start = time.time()
    large_json = fast_json_dumps(large_data)
    fast_json_loads(large_json)
    elapsed = (time.time() - start) * 1000

    print(f"Large data ({(len(large_json)/1024):.1f} KB) serialized in {elapsed:.2f} ms")
    print(f"[OK]" if elapsed < 100 else f"[WARN] Large data took {elapsed:.2f} ms")
