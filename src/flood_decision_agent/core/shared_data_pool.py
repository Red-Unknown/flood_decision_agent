from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SharedDataPool:
    _store: dict[str, Any] = field(default_factory=dict)

    def put(self, key: str, value: Any) -> None:
        """存储数据（别名：set）"""
        self._store[key] = value

    def set(self, key: str, value: Any) -> None:
        """存储数据（与put相同，提供兼容性）"""
        self._store[key] = value

    def has(self, key: str) -> bool:
        """检查key是否存在"""
        return key in self._store

    def get(self, key: str, default: Any = None) -> Any:
        """获取数据，支持默认值"""
        return self._store.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        """获取数据快照"""
        return dict(self._store)

    @property
    def _data(self) -> dict[str, Any]:
        """内部数据字典（用于工具访问）"""
        return self._store
