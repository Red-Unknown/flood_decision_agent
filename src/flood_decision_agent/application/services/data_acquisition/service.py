"""数据获取服务核心实现"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import (
    DataAcquisitionRecord,
    DataConfidenceLevel,
    DataRequest,
    DataResponse,
    DataSource,
)


class DataAcquisitionService:
    """数据获取服务

    负责管理数据的请求、获取、存储和追溯。
    支持多种数据来源和置信度级别，提供完整的数据血缘追踪能力。

    Attributes:
        _llm_client: 可选的LLM客户端，用于智能数据提取
        _records: 数据获取记录存储
        _data_cache: 数据缓存
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """初始化数据获取服务

        Args:
            llm_client: 可选的LLM客户端，用于智能数据提取和解析
        """
        self._llm_client = llm_client
        self._records: Dict[str, DataAcquisitionRecord] = {}
        self._data_cache: Dict[str, DataResponse] = {}
        self._key_to_record_ids: Dict[str, List[str]] = {}

    def request_data(self, request: DataRequest) -> DataResponse:
        """请求数据

        根据数据请求获取对应的数据。优先从缓存获取，
        如果数据不存在则根据策略尝试获取。

        Args:
            request: 数据请求对象

        Returns:
            DataResponse: 数据响应对象

        Raises:
            ValueError: 当必需数据无法获取时
        """
        # 检查缓存
        if request.data_key in self._data_cache:
            return self._data_cache[request.data_key]

        # 尝试使用默认值
        if request.default_value is not None and not request.required:
            response = DataResponse(
                value=request.default_value,
                source=DataSource.USER_INPUT,
                confidence=DataConfidenceLevel.ASSUMED,
                acquisition_path="default_value",
            )
            self._create_record(request, response)
            return response

        # 如果数据是必需的但没有获取途径，抛出异常
        if request.required:
            raise ValueError(
                f"必需数据 '{request.data_key}' 无法获取: {request.description}"
            )

        # 非必需数据返回空响应
        response = DataResponse(
            value=None,
            source=DataSource.USER_INPUT,
            confidence=DataConfidenceLevel.ASSUMED,
            acquisition_path="not_acquired",
        )
        return response

    def acquire_data(
        self,
        data_key: str,
        value: Any,
        source: DataSource,
        confidence: DataConfidenceLevel,
        acquisition_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_records: Optional[List[str]] = None,
    ) -> DataResponse:
        """主动获取数据

        用于外部系统主动提供数据时使用。

        Args:
            data_key: 数据标识符
            value: 数据值
            source: 数据来源
            confidence: 数据置信度
            acquisition_path: 获取路径描述
            metadata: 额外元数据
            parent_records: 父记录ID列表

        Returns:
            DataResponse: 数据响应对象
        """
        response = DataResponse(
            value=value,
            source=source,
            confidence=confidence,
            acquisition_path=acquisition_path,
            metadata=metadata,
        )

        # 创建请求对象（用于记录）
        request = DataRequest(
            data_key=data_key,
            description=f"Acquired via {acquisition_path}",
            required=True,
        )

        self._create_record(request, response, parent_records)
        self._data_cache[data_key] = response

        return response

    def get_data_history(self, data_key: str) -> List[DataAcquisitionRecord]:
        """获取数据历史记录

        返回指定数据的所有获取记录，按时间倒序排列。

        Args:
            data_key: 数据标识符

        Returns:
            List[DataAcquisitionRecord]: 数据获取记录列表
        """
        record_ids = self._key_to_record_ids.get(data_key, [])
        records = [self._records[rid] for rid in record_ids if rid in self._records]
        return sorted(records, key=lambda r: r.created_at, reverse=True)

    def get_data_lineage(self, data_key: str) -> Dict[str, Any]:
        """获取数据血缘/溯源信息

        构建指定数据的完整血缘树，包括所有依赖关系。

        Args:
            data_key: 数据标识符

        Returns:
            Dict: 包含血缘信息的字典
        """
        history = self.get_data_history(data_key)

        if not history:
            return {
                "data_key": data_key,
                "exists": False,
                "lineage": [],
            }

        latest_record = history[0]
        lineage_tree = self._build_lineage_tree(latest_record.record_id)

        return {
            "data_key": data_key,
            "exists": True,
            "current_value": latest_record.response.value,
            "current_confidence": latest_record.response.confidence.value,
            "current_source": latest_record.response.source.value,
            "acquisition_count": len(history),
            "first_acquired": history[-1].created_at if history else None,
            "last_acquired": latest_record.created_at,
            "lineage": lineage_tree,
        }

    def invalidate_cache(self, data_key: str) -> bool:
        """使指定数据的缓存失效

        Args:
            data_key: 数据标识符

        Returns:
            bool: 是否成功清除缓存
        """
        if data_key in self._data_cache:
            del self._data_cache[data_key]
            return True
        return False

    def clear_all_cache(self) -> None:
        """清除所有数据缓存"""
        self._data_cache.clear()

    def get_record_by_id(self, record_id: str) -> Optional[DataAcquisitionRecord]:
        """通过ID获取记录

        Args:
            record_id: 记录唯一标识

        Returns:
            Optional[DataAcquisitionRecord]: 数据获取记录或None
        """
        return self._records.get(record_id)

    def _create_record(
        self,
        request: DataRequest,
        response: DataResponse,
        parent_records: Optional[List[str]] = None,
    ) -> DataAcquisitionRecord:
        """创建数据获取记录

        Args:
            request: 数据请求
            response: 数据响应
            parent_records: 父记录ID列表

        Returns:
            DataAcquisitionRecord: 创建的记录
        """
        record_id = str(uuid.uuid4())
        record = DataAcquisitionRecord(
            record_id=record_id,
            data_key=request.data_key,
            request=request,
            response=response,
            parent_records=parent_records or [],
        )

        self._records[record_id] = record

        # 更新key到记录的映射
        if request.data_key not in self._key_to_record_ids:
            self._key_to_record_ids[request.data_key] = []
        self._key_to_record_ids[request.data_key].append(record_id)

        return record

    def _build_lineage_tree(self, record_id: str) -> Dict[str, Any]:
        """构建血缘树

        递归构建指定记录的血缘树。

        Args:
            record_id: 记录ID

        Returns:
            Dict: 血缘树节点
        """
        record = self._records.get(record_id)
        if not record:
            return {"record_id": record_id, "exists": False}

        children = []
        for parent_id in record.parent_records:
            children.append(self._build_lineage_tree(parent_id))

        return {
            "record_id": record_id,
            "exists": True,
            "data_key": record.data_key,
            "source": record.response.source.value,
            "confidence": record.response.confidence.value,
            "acquisition_path": record.response.acquisition_path,
            "timestamp": record.created_at.isoformat(),
            "parents": children,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """获取服务统计信息

        Returns:
            Dict: 统计信息字典
        """
        return {
            "total_records": len(self._records),
            "cached_data_count": len(self._data_cache),
            "unique_data_keys": len(self._key_to_record_ids),
            "records_per_key": {
                key: len(ids) for key, ids in self._key_to_record_ids.items()
            },
        }
