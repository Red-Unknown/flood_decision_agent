"""验证工具"""
from typing import Any, Type


def validate_required(value: Any, field_name: str) -> None:
    """验证必填字段"""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"{field_name} 是必填字段")


def validate_type(value: Any, expected_type: Type, field_name: str) -> None:
    """验证字段类型"""
    if not isinstance(value, expected_type):
        raise TypeError(f"{field_name} 必须是 {expected_type.__name__} 类型")
