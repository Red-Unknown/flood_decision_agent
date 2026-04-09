"""澄清管理器实现

实现渐进式澄清机制的核心管理器，负责数据依赖检查、默认值提供、
暂停/恢复机制的状态管理等功能。
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import uuid
import logging

from .models import (
    ClarificationStatus,
    DataRequestType,
    PendingDataRequest,
    ClarificationSession,
    DefaultValueSuggestion,
)

logger = logging.getLogger(__name__)


class DefaultValueProvider:
    """默认值提供者接口
    
    用于根据上下文为数据项提供默认值建议。
    可由外部实现并注入到 ClarificationManager 中。
    """

    def get_suggestions(
        self, data_key: str, context: Dict[str, Any]
    ) -> List[DefaultValueSuggestion]:
        """获取默认值建议
        
        Args:
            data_key: 数据键名
            context: 上下文信息
            
        Returns:
            默认值建议列表
        """
        raise NotImplementedError("Subclasses must implement this method")


class DataAcquisitionService:
    """数据获取服务接口
    
    用于检查数据依赖和执行数据获取操作。
    可由外部实现并注入到 ClarificationManager 中。
    """

    def check_dependencies(self, task_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查数据依赖
        
        Args:
            task_context: 任务上下文
            
        Returns:
            依赖项列表，每项包含 data_key, description, is_required 等信息
        """
        raise NotImplementedError("Subclasses must implement this method")

    def get_data_schema(self, data_key: str) -> Optional[Dict[str, Any]]:
        """获取数据模式定义
        
        Args:
            data_key: 数据键名
            
        Returns:
            数据模式定义，包含类型、约束等信息
        """
        raise NotImplementedError("Subclasses must implement this method")


class ClarificationManager:
    """澄清管理器
    
    管理渐进式澄清流程，包括：
    - 数据依赖检查
    - 按需请求数据
    - 默认值建议提供
    - 使用默认值解决请求
    - 标记假设值
    - 暂停/恢复机制
    
    Attributes:
        data_acquisition_service: 数据获取服务
        default_value_provider: 默认值提供者
        sessions: 会话缓存，key 为 session_id
        _execution_paused: 执行暂停状态映射
        _execution_callbacks: 执行恢复回调映射
    """

    def __init__(
        self,
        data_acquisition_service: DataAcquisitionService,
        default_value_provider: Optional[DefaultValueProvider] = None,
    ):
        """初始化澄清管理器
        
        Args:
            data_acquisition_service: 数据获取服务实例
            default_value_provider: 默认值提供者实例（可选）
        """
        self.data_acquisition_service = data_acquisition_service
        self.default_value_provider = default_value_provider
        self.sessions: Dict[str, ClarificationSession] = {}
        self._execution_paused: Dict[str, bool] = {}
        self._execution_callbacks: Dict[str, List[Callable]] = {}

    def check_data_dependencies(
        self, task_context: Dict[str, Any]
    ) -> List[PendingDataRequest]:
        """检查任务执行所需的数据依赖
        
        分析任务上下文，识别所有缺失的数据依赖，并创建对应的数据请求。
        
        Args:
            task_context: 任务上下文，包含 task_id、当前可用数据等信息
            
        Returns:
            待请求数据列表
        """
        task_id = task_context.get("task_id", str(uuid.uuid4()))
        logger.info(f"Checking data dependencies for task: {task_id}")

        dependencies = self.data_acquisition_service.check_dependencies(task_context)
        pending_requests: List[PendingDataRequest] = []

        for dep in dependencies:
            data_key = dep.get("data_key", "")
            is_required = dep.get("is_required", True)
            has_default = dep.get("has_default", False)

            if is_required:
                request_type = DataRequestType.required
            elif has_default:
                request_type = DataRequestType.optional_with_default
            else:
                request_type = DataRequestType.optional_no_default

            request = PendingDataRequest(
                data_key=data_key,
                description=dep.get("description", f"需要提供数据: {data_key}"),
                request_type=request_type,
            )

            if request_type == DataRequestType.optional_with_default:
                suggestions = self.provide_default_suggestions(
                    data_key, task_context
                )
                request.suggested_defaults = suggestions

            pending_requests.append(request)
            logger.debug(f"Created pending request for {data_key}: {request_type.value}")

        logger.info(f"Found {len(pending_requests)} data dependencies for task {task_id}")
        return pending_requests

    def create_session(
        self, task_id: str, pending_requests: List[PendingDataRequest]
    ) -> ClarificationSession:
        """创建新的澄清会话
        
        Args:
            task_id: 任务ID
            pending_requests: 待处理的请求列表
            
        Returns:
            创建的澄清会话
        """
        session = ClarificationSession(
            task_id=task_id,
            pending_requests=pending_requests,
            status=ClarificationStatus.pending,
        )
        self.sessions[session.session_id] = session
        self._execution_paused[session.session_id] = False
        self._execution_callbacks[session.session_id] = []

        logger.info(f"Created clarification session {session.session_id} for task {task_id}")
        return session

    def request_data_incrementally(
        self, session_id: str, data_key: str
    ) -> Optional[PendingDataRequest]:
        """按需请求单个数据
        
        在渐进式澄清流程中，按需请求特定数据项。
        
        Args:
            session_id: 会话ID
            data_key: 数据键名
            
        Returns:
            创建的数据请求，如果会话不存在返回 None
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None

        schema = self.data_acquisition_service.get_data_schema(data_key)
        description = schema.get("description", f"需要提供数据: {data_key}") if schema else f"需要提供数据: {data_key}"

        request = PendingDataRequest(
            data_key=data_key,
            description=description,
            request_type=DataRequestType.required,
        )

        session.add_request(request)
        session.update_status(ClarificationStatus.waiting_for_user)

        logger.info(f"Added incremental request for {data_key} in session {session_id}")
        return request

    def provide_default_suggestions(
        self, data_key: str, context: Dict[str, Any]
    ) -> List[DefaultValueSuggestion]:
        """根据上下文提供默认值建议
        
        利用默认值提供者生成针对特定数据项的默认值建议。
        
        Args:
            data_key: 数据键名
            context: 上下文信息
            
        Returns:
            默认值建议列表
        """
        if self.default_value_provider is None:
            logger.debug(f"No default value provider configured for {data_key}")
            return []

        try:
            suggestions = self.default_value_provider.get_suggestions(data_key, context)
            logger.info(f"Got {len(suggestions)} default suggestions for {data_key}")
            return suggestions
        except Exception as e:
            logger.error(f"Error getting default suggestions for {data_key}: {e}")
            return []

    def resolve_with_default(
        self, session_id: str, request_id: str, default_value: DefaultValueSuggestion
    ) -> bool:
        """使用默认值解决数据请求
        
        使用系统提供的默认值来解决特定的数据请求。
        
        Args:
            session_id: 会话ID
            request_id: 请求ID
            default_value: 要使用的默认值建议
            
        Returns:
            是否成功解决
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False

        request = session.get_request(request_id)
        if not request:
            logger.error(f"Request not found: {request_id} in session {session_id}")
            return False

        if request.is_resolved():
            logger.warning(f"Request {request_id} is already resolved")
            return False

        request.resolve(default_value.value, "default")
        logger.info(f"Resolved request {request_id} with default value from {default_value.source}")

        self._check_and_update_session_status(session)
        return True

    def resolve_with_user_input(
        self, session_id: str, request_id: str, value: Any
    ) -> bool:
        """使用用户输入解决数据请求
        
        Args:
            session_id: 会话ID
            request_id: 请求ID
            value: 用户提供的值
            
        Returns:
            是否成功解决
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False

        request = session.get_request(request_id)
        if not request:
            logger.error(f"Request not found: {request_id} in session {session_id}")
            return False

        if request.is_resolved():
            logger.warning(f"Request {request_id} is already resolved")
            return False

        request.resolve(value, "user_input")
        logger.info(f"Resolved request {request_id} with user input")

        self._check_and_update_session_status(session)
        return True

    def mark_as_assumed(
        self, session_id: str, request_id: str, assumed_value: Any
    ) -> bool:
        """标记数据为假设值
        
        当无法获取确切数据时，使用假设值继续执行，并标记该数据为假设。
        
        Args:
            session_id: 会话ID
            request_id: 请求ID
            assumed_value: 假设的值
            
        Returns:
            是否成功标记
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False

        request = session.get_request(request_id)
        if not request:
            logger.error(f"Request not found: {request_id} in session {session_id}")
            return False

        if request.is_resolved():
            logger.warning(f"Request {request_id} is already resolved")
            return False

        request.resolve(assumed_value, "assumed")
        if "assumed_values" not in session.metadata:
            session.metadata["assumed_values"] = []
        session.metadata["assumed_values"].append({
            "request_id": request_id,
            "data_key": request.data_key,
            "assumed_value": assumed_value,
            "timestamp": datetime.now().isoformat(),
        })

        logger.info(f"Marked request {request_id} as assumed with value: {assumed_value}")

        self._check_and_update_session_status(session)
        return True

    def skip_request(
        self, session_id: str, request_id: str
    ) -> bool:
        """跳过特定数据请求
        
        对于可选数据，用户可以选择跳过不提供。
        
        Args:
            session_id: 会话ID
            request_id: 请求ID
            
        Returns:
            是否成功跳过
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False

        request = session.get_request(request_id)
        if not request:
            logger.error(f"Request not found: {request_id} in session {session_id}")
            return False

        if request.request_type == DataRequestType.required:
            logger.error(f"Cannot skip required request: {request_id}")
            return False

        if request.is_resolved():
            logger.warning(f"Request {request_id} is already resolved")
            return False

        request.resolve(None, "skipped")
        logger.info(f"Skipped optional request {request_id}")

        self._check_and_update_session_status(session)
        return True

    def pause_execution(self, session_id: str) -> bool:
        """暂停执行
        
        当需要等待用户输入时，暂停任务执行。
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功暂停
        """
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return False

        self._execution_paused[session_id] = True
        session = self.sessions[session_id]
        session.update_status(ClarificationStatus.waiting_for_user)

        logger.info(f"Execution paused for session {session_id}")
        return True

    def resume_execution(self, session_id: str) -> bool:
        """恢复执行
        
        当用户提供了所需数据后，恢复任务执行。
        触发所有注册的恢复回调。
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功恢复
        """
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return False

        session = self.sessions[session_id]

        if not self.can_resume(session_id):
            logger.warning(f"Cannot resume session {session_id}: unresolved required requests exist")
            return False

        self._execution_paused[session_id] = False

        if session.is_complete():
            session.update_status(ClarificationStatus.resolved)
        else:
            session.update_status(ClarificationStatus.pending)

        callbacks = self._execution_callbacks.get(session_id, [])
        for callback in callbacks:
            try:
                callback(session_id)
            except Exception as e:
                logger.error(f"Error in resume callback for session {session_id}: {e}")

        self._execution_callbacks[session_id] = []

        logger.info(f"Execution resumed for session {session_id}")
        return True

    def can_resume(self, session_id: str) -> bool:
        """检查是否可以恢复执行
        
        检查是否所有必需的请求都已解决。
        
        Args:
            session_id: 会话ID
            
        Returns:
            如果可以恢复返回 True
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        for request in session.get_unresolved_requests():
            if request.request_type == DataRequestType.required:
                return False

        return True

    def is_paused(self, session_id: str) -> bool:
        """检查会话是否处于暂停状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            如果暂停返回 True
        """
        return self._execution_paused.get(session_id, False)

    def on_resume(self, session_id: str, callback: Callable[[str], None]) -> bool:
        """注册恢复回调
        
        当执行恢复时，注册的回调函数将被调用。
        
        Args:
            session_id: 会话ID
            callback: 回调函数，接收 session_id 参数
            
        Returns:
            是否成功注册
        """
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return False

        if session_id not in self._execution_callbacks:
            self._execution_callbacks[session_id] = []

        self._execution_callbacks[session_id].append(callback)
        return True

    def get_session_status(self, session_id: str) -> Optional[ClarificationSession]:
        """获取会话状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            澄清会话对象，未找到返回 None
        """
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> List[ClarificationSession]:
        """获取所有会话
        
        Returns:
            所有澄清会话列表
        """
        return list(self.sessions.values())

    def cleanup_session(self, session_id: str) -> bool:
        """清理会话
        
        删除已完成的会话，释放资源。
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功清理
        """
        if session_id not in self.sessions:
            return False

        del self.sessions[session_id]
        self._execution_paused.pop(session_id, None)
        self._execution_callbacks.pop(session_id, None)

        logger.info(f"Cleaned up session {session_id}")
        return True

    def _check_and_update_session_status(self, session: ClarificationSession) -> None:
        """检查并更新会话状态
        
        当请求被解决时，检查会话是否已完成。
        
        Args:
            session: 澄清会话
        """
        if session.is_complete():
            session.update_status(ClarificationStatus.resolved)
            logger.info(f"Session {session.session_id} is now complete")

            if self.can_resume(session.session_id):
                self.resume_execution(session.session_id)
