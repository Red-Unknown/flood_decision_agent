from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class DataEntry:
    """数据条目，包含元数据
    
    用于 SharedDataPool 中存储每个数据项的完整信息。
    
    Attributes:
        value: 数据值
        source: 来源标识 (user_input/tool_output/experience/user_provided)
        timestamp: 时间戳
        version: 版本号
        metadata: 额外元数据
    """

    value: Any
    source: str = "unknown"
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


class SharedDataPool:
    """增强的共享数据池
    
    支持命名空间、来源追踪、历史记录等功能。
    保持向后兼容，原有简单接口仍然可用。
    
    Attributes:
        _store: 内部数据存储
        _history: 数据变更历史
        _session_id: 会话ID
    """

    def __init__(self):
        self._store: Dict[str, DataEntry] = {}
        self._history: List[Dict[str, Any]] = []
        self._session_id: str = str(uuid.uuid4())

    def put(
        self,
        key: str,
        value: Any,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """存储数据，带来源追踪"""
        if key in self._store:
            old_entry = self._store[key]
            new_version = old_entry.version + 1
            self._history.append({
                "key": key,
                "old_value": old_entry.value,
                "new_value": value,
                "timestamp": datetime.now(),
                "version": new_version,
            })
            new_entry = DataEntry(
                value=value,
                source=source,
                version=new_version,
                metadata=metadata or {},
            )
        else:
            new_entry = DataEntry(
                value=value,
                source=source,
                version=1,
                metadata=metadata or {},
            )
        self._store[key] = new_entry

    def set(
        self,
        key: str,
        value: Any,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """别名方法，兼容旧接口"""
        self.put(key, value, source, metadata)

    def get(self, key: str, default: Any = None) -> Any:
        """获取数据值"""
        entry = self._store.get(key)
        return entry.value if entry else default

    def get_entry(self, key: str) -> Optional[DataEntry]:
        """获取完整数据条目（含元数据）"""
        return self._store.get(key)

    def has(self, key: str) -> bool:
        """检查key是否存在"""
        return key in self._store

    def delete(self, key: str) -> bool:
        """删除数据"""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def put_with_namespace(
        self,
        namespace: str,
        key: str,
        value: Any,
        source: str = "unknown",
    ) -> None:
        """带命名空间存储，避免key冲突"""
        full_key = f"{namespace}:{key}"
        self.put(full_key, value, source)

    def get_with_namespace(
        self,
        namespace: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """带命名空间获取"""
        full_key = f"{namespace}:{key}"
        return self.get(full_key, default)

    def put_batch(
        self,
        data_dict: Dict[str, Any],
        source: str = "unknown",
    ) -> None:
        """批量存储数据"""
        for key, value in data_dict.items():
            self.put(key, value, source)

    def get_batch(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取数据"""
        return {key: self.get(key) for key in keys if self.has(key)}

    def find_by_prefix(self, prefix: str) -> Dict[str, Any]:
        """按前缀查找数据"""
        return {
            key: entry.value
            for key, entry in self._store.items()
            if key.startswith(prefix)
        }

    def find_by_source(self, source: str) -> Dict[str, Any]:
        """按来源查找数据"""
        return {
            key: entry.value
            for key, entry in self._store.items()
            if entry.source == source
        }

    def set_context(self, context_key: str, context_value: Any) -> None:
        """设置上下文数据（特殊命名空间）"""
        self.put_with_namespace("context", context_key, context_value, "context")

    def get_context(self, context_key: str, default: Any = None) -> Any:
        """获取上下文数据"""
        return self.get_with_namespace("context", context_key, default)

    def put_tool_output(
        self,
        tool_name: str,
        output_key: str,
        value: Any,
        source: str = "tool_output",
    ) -> None:
        """存储工具输出"""
        full_key = f"tool:{tool_name}:{output_key}"
        self.put(full_key, value, source)

    def get_tool_output(
        self,
        tool_name: str,
        output_key: str,
        default: Any = None,
    ) -> Any:
        """获取工具输出"""
        full_key = f"tool:{tool_name}:{output_key}"
        return self.get(full_key, default)

    def snapshot(self) -> Dict[str, Any]:
        """获取数据快照（仅值）"""
        return {key: entry.value for key, entry in self._store.items()}

    def snapshot_with_metadata(self) -> Dict[str, Dict[str, Any]]:
        """获取带元数据的快照"""
        return {
            key: {
                "value": entry.value,
                "source": entry.source,
                "timestamp": entry.timestamp.isoformat(),
                "version": entry.version,
                "metadata": entry.metadata,
            }
            for key, entry in self._store.items()
        }

    def get_history(self, key: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取历史记录"""
        if key:
            return [h for h in self._history if h["key"] == key]
        return self._history.copy()

    @property
    def session_id(self) -> str:
        """获取会话ID"""
        return self._session_id

    def clear(self) -> None:
        """清空数据池（保留会话ID）"""
        self._store.clear()
        self._history.clear()

    @property
    def _data(self) -> Dict[str, Any]:
        """内部数据字典（用于工具访问，向后兼容）"""
        return {key: entry.value for key, entry in self._store.items()}

    def get_source(self, key: str) -> Optional[str]:
        """获取数据来源"""
        entry = self._store.get(key)
        return entry.source if entry else None

    def get_version(self, key: str) -> Optional[int]:
        """获取数据版本"""
        entry = self._store.get(key)
        return entry.version if entry else None

    def get_timestamp(self, key: str) -> Optional[datetime]:
        """获取数据时间戳"""
        entry = self._store.get(key)
        return entry.timestamp if entry else None
