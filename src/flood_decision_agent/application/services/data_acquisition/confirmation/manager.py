"""数据确认交互流程模块 - ConfirmationManager"""

import time
import uuid
from typing import Any, Dict, List, Optional, Callable

from .models import (
    ConfirmationStatus,
    DataFieldStatus,
    DataFieldDisplay,
    ConfirmationView,
    ConfirmationAction,
    ConfirmationResult,
    FieldModification,
    ConfirmationSession,
)


class ConfirmationManager:
    """数据确认管理器
    
    负责管理数据确认交互流程，包括：
    - 创建确认视图
    - 处理用户确认/修改
    - 管理待确认会话
    - 字段级别的更新
    """

    def __init__(self):
        """初始化确认管理器"""
        self._sessions: Dict[str, ConfirmationSession] = {}
        self._default_actions = [
            ConfirmationAction(
                action_id="confirm",
                label="确认",
                action_type="confirm",
                primary=True
            ),
            ConfirmationAction(
                action_id="reject",
                label="拒绝",
                action_type="reject",
                primary=False
            ),
            ConfirmationAction(
                action_id="modify",
                label="修改",
                action_type="modify",
                primary=False
            ),
        ]
        self._validators: Dict[str, Callable[[Any], tuple[bool, str]]] = {}

    def register_validator(self, field_name: str, validator: Callable[[Any], tuple[bool, str]]) -> None:
        """注册字段验证器
        
        Args:
            field_name: 字段名称
            validator: 验证函数，返回 (是否有效, 错误信息)
        """
        self._validators[field_name] = validator

    def create_confirmation_view(
        self,
        parsed_data: Dict[str, Any],
        schema: Optional[Any] = None,
        title: str = "数据确认",
        summary: str = "",
        actions: Optional[List[ConfirmationAction]] = None
    ) -> ConfirmationView:
        """创建确认视图
        
        根据解析结果生成确认视图，自动识别缺失项和异常项。
        
        Args:
            parsed_data: 解析后的数据字典
            schema: 数据模式（可选，用于验证）
            title: 确认视图标题
            summary: 数据摘要说明
            actions: 自定义操作列表（可选）
            
        Returns:
            ConfirmationView: 确认视图对象
        """
        confirmation_id = str(uuid.uuid4())
        current_time = time.time()
        
        fields = self._create_field_displays(parsed_data, schema)
        
        view = ConfirmationView(
            confirmation_id=confirmation_id,
            title=title,
            fields=fields,
            summary=summary or self._generate_summary(fields),
            actions=actions or self._default_actions.copy(),
            status=ConfirmationStatus.PENDING,
            created_at=current_time
        )
        
        session = ConfirmationSession(
            confirmation_id=confirmation_id,
            view=view,
            schema=schema
        )
        self._sessions[confirmation_id] = session
        
        return view

    def _create_field_displays(
        self,
        parsed_data: Dict[str, Any],
        schema: Optional[Any] = None
    ) -> List[DataFieldDisplay]:
        """创建字段展示列表
        
        根据数据自动识别状态：
        - 缺失项（None 或空值）-> status=MISSING，标红
        - 异常项（验证失败）-> status=WARNING，标黄
        - 正常项 -> status=VALID
        
        Args:
            parsed_data: 解析后的数据
            schema: 数据模式
            
        Returns:
            List[DataFieldDisplay]: 字段展示列表
        """
        fields = []
        
        required_fields = self._extract_required_fields(schema)
        
        for field_name, value in parsed_data.items():
            status = DataFieldStatus.VALID
            message = ""
            
            if value is None or value == "":
                status = DataFieldStatus.MISSING
                message = "数据缺失"
                if field_name in required_fields:
                    message = "必填项缺失"
            else:
                is_valid, error_msg = self._validate_field(field_name, value)
                if not is_valid:
                    status = DataFieldStatus.WARNING
                    message = error_msg or "数据异常"
            
            fields.append(DataFieldDisplay(
                name=field_name,
                value=value,
                status=status,
                message=message,
                editable=True
            ))
        
        for field_name in required_fields:
            if field_name not in parsed_data:
                fields.append(DataFieldDisplay(
                    name=field_name,
                    value=None,
                    status=DataFieldStatus.MISSING,
                    message="必填项缺失",
                    editable=True
                ))
        
        return fields

    def _extract_required_fields(self, schema: Optional[Any]) -> set:
        """从模式中提取必填字段"""
        required_fields = set()
        if schema is None:
            return required_fields
        
        if isinstance(schema, dict):
            if "required" in schema:
                required_fields.update(schema["required"])
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    if isinstance(prop_schema, dict) and prop_schema.get("required"):
                        required_fields.add(prop_name)
        
        return required_fields

    def _validate_field(self, field_name: str, value: Any) -> tuple[bool, str]:
        """验证字段值
        
        Args:
            field_name: 字段名称
            value: 字段值
            
        Returns:
            tuple[bool, str]: (是否有效, 错误信息)
        """
        if field_name in self._validators:
            return self._validators[field_name](value)
        return True, ""

    def _generate_summary(self, fields: List[DataFieldDisplay]) -> str:
        """生成数据摘要"""
        total = len(fields)
        missing = sum(1 for f in fields if f.status == DataFieldStatus.MISSING)
        warning = sum(1 for f in fields if f.status == DataFieldStatus.WARNING)
        invalid = sum(1 for f in fields if f.status == DataFieldStatus.INVALID)
        
        if missing == 0 and warning == 0 and invalid == 0:
            return f"共 {total} 个字段，数据完整"
        
        parts = []
        if missing > 0:
            parts.append(f"{missing} 个缺失")
        if warning > 0:
            parts.append(f"{warning} 个异常")
        if invalid > 0:
            parts.append(f"{invalid} 个无效")
        
        return f"共 {total} 个字段，{', '.join(parts)}"

    def process_confirmation(
        self,
        confirmation_id: str,
        user_response: Dict[str, Any]
    ) -> ConfirmationResult:
        """处理用户确认
        
        Args:
            confirmation_id: 确认会话ID
            user_response: 用户响应数据
                - action: 操作类型（confirm/reject/modify）
                - notes: 用户备注（可选）
                - modified_fields: 修改的字段（可选）
                
        Returns:
            ConfirmationResult: 确认结果
        """
        session = self._sessions.get(confirmation_id)
        if not session:
            raise ValueError(f"确认会话不存在: {confirmation_id}")
        
        action = user_response.get("action", "confirm")
        notes = user_response.get("notes", "")
        modified_fields = user_response.get("modified_fields", {})
        
        original_data = self._extract_data_from_fields(session.view.fields)
        
        if action == "reject":
            result = ConfirmationResult(
                confirmation_id=confirmation_id,
                status=ConfirmationStatus.REJECTED,
                original_data=original_data,
                user_notes=notes,
                confirmed_at=time.time()
            )
        elif action == "modify" or modified_fields:
            modified_data = original_data.copy()
            modified_data.update(modified_fields)
            
            result = ConfirmationResult(
                confirmation_id=confirmation_id,
                status=ConfirmationStatus.MODIFIED,
                original_data=original_data,
                modified_data=modified_data,
                user_notes=notes,
                confirmed_at=time.time()
            )
            
            for field_name, new_value in modified_fields.items():
                old_value = original_data.get(field_name)
                if old_value != new_value:
                    session.modifications.append(FieldModification(
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        modified_at=time.time()
                    ))
        else:
            result = ConfirmationResult(
                confirmation_id=confirmation_id,
                status=ConfirmationStatus.CONFIRMED,
                original_data=original_data,
                user_notes=notes,
                confirmed_at=time.time()
            )
        
        session.result = result
        session.view.status = result.status
        
        return result

    def _extract_data_from_fields(self, fields: List[DataFieldDisplay]) -> Dict[str, Any]:
        """从字段列表中提取数据"""
        return {f.name: f.value for f in fields}

    def get_pending_confirmations(self) -> List[ConfirmationView]:
        """获取所有待确认的视图
        
        Returns:
            List[ConfirmationView]: 待确认视图列表
        """
        return [
            session.view
            for session in self._sessions.values()
            if session.view.status == ConfirmationStatus.PENDING
        ]

    def get_confirmation_view(self, confirmation_id: str) -> Optional[ConfirmationView]:
        """获取指定确认视图
        
        Args:
            confirmation_id: 确认会话ID
            
        Returns:
            Optional[ConfirmationView]: 确认视图或None
        """
        session = self._sessions.get(confirmation_id)
        return session.view if session else None

    def get_confirmation_result(self, confirmation_id: str) -> Optional[ConfirmationResult]:
        """获取确认结果
        
        Args:
            confirmation_id: 确认会话ID
            
        Returns:
            Optional[ConfirmationResult]: 确认结果或None
        """
        session = self._sessions.get(confirmation_id)
        return session.result if session else None

    def update_field(
        self,
        confirmation_id: str,
        field_name: str,
        new_value: Any
    ) -> bool:
        """更新字段值
        
        Args:
            confirmation_id: 确认会话ID
            field_name: 字段名称
            new_value: 新值
            
        Returns:
            bool: 是否更新成功
        """
        session = self._sessions.get(confirmation_id)
        if not session:
            return False
        
        if session.view.status != ConfirmationStatus.PENDING:
            return False
        
        for field in session.view.fields:
            if field.name == field_name:
                if not field.editable:
                    return False
                
                old_value = field.value
                field.value = new_value
                
                is_valid, message = self._validate_field(field_name, new_value)
                if new_value is None or new_value == "":
                    field.status = DataFieldStatus.MISSING
                    field.message = "数据缺失"
                elif not is_valid:
                    field.status = DataFieldStatus.WARNING
                    field.message = message or "数据异常"
                else:
                    field.status = DataFieldStatus.VALID
                    field.message = ""
                
                session.modifications.append(FieldModification(
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    modified_at=time.time()
                ))
                
                session.view.summary = self._generate_summary(session.view.fields)
                
                return True
        
        return False

    def batch_update_fields(
        self,
        confirmation_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, bool]:
        """批量更新字段
        
        Args:
            confirmation_id: 确认会话ID
            updates: 字段更新字典 {field_name: new_value}
            
        Returns:
            Dict[str, bool]: 各字段更新结果
        """
        results = {}
        for field_name, new_value in updates.items():
            results[field_name] = self.update_field(confirmation_id, field_name, new_value)
        return results

    def remove_confirmation(self, confirmation_id: str) -> bool:
        """移除确认会话
        
        Args:
            confirmation_id: 确认会话ID
            
        Returns:
            bool: 是否移除成功
        """
        if confirmation_id in self._sessions:
            del self._sessions[confirmation_id]
            return True
        return False

    def clear_completed_confirmations(self) -> int:
        """清理已完成的确认会话
        
        Returns:
            int: 清理的会话数量
        """
        completed_statuses = {
            ConfirmationStatus.CONFIRMED,
            ConfirmationStatus.REJECTED,
            ConfirmationStatus.MODIFIED
        }
        
        to_remove = [
            cid for cid, session in self._sessions.items()
            if session.view.status in completed_statuses
        ]
        
        for cid in to_remove:
            del self._sessions[cid]
        
        return len(to_remove)

    def get_session_modifications(self, confirmation_id: str) -> List[FieldModification]:
        """获取会话的修改记录
        
        Args:
            confirmation_id: 确认会话ID
            
        Returns:
            List[FieldModification]: 修改记录列表
        """
        session = self._sessions.get(confirmation_id)
        return session.modifications.copy() if session else []

    def to_visualization_format(self, view: ConfirmationView) -> Dict[str, Any]:
        """转换为可视化确认的数据结构
        
        将确认视图转换为前端可视化组件可用的格式。
        
        Args:
            view: 确认视图
            
        Returns:
            Dict[str, Any]: 可视化数据结构
        """
        field_groups = self._group_fields_by_status(view.fields)
        
        return {
            "meta": {
                "confirmation_id": view.confirmation_id,
                "title": view.title,
                "summary": view.summary,
                "status": view.status.value,
                "created_at": view.created_at
            },
            "groups": [
                {
                    "group_id": "missing",
                    "label": "缺失项",
                    "level": "error",
                    "color": "#ff4d4f",
                    "fields": [
                        {
                            "name": f.name,
                            "value": f.value,
                            "message": f.message,
                            "editable": f.editable
                        }
                        for f in field_groups.get(DataFieldStatus.MISSING, [])
                    ]
                },
                {
                    "group_id": "warning",
                    "label": "异常项",
                    "level": "warning",
                    "color": "#faad14",
                    "fields": [
                        {
                            "name": f.name,
                            "value": f.value,
                            "message": f.message,
                            "editable": f.editable
                        }
                        for f in field_groups.get(DataFieldStatus.WARNING, [])
                    ]
                },
                {
                    "group_id": "invalid",
                    "label": "无效项",
                    "level": "error",
                    "color": "#ff4d4f",
                    "fields": [
                        {
                            "name": f.name,
                            "value": f.value,
                            "message": f.message,
                            "editable": f.editable
                        }
                        for f in field_groups.get(DataFieldStatus.INVALID, [])
                    ]
                },
                {
                    "group_id": "valid",
                    "label": "正常项",
                    "level": "success",
                    "color": "#52c41a",
                    "fields": [
                        {
                            "name": f.name,
                            "value": f.value,
                            "message": f.message,
                            "editable": f.editable
                        }
                        for f in field_groups.get(DataFieldStatus.VALID, [])
                    ]
                }
            ],
            "actions": [
                {
                    "id": a.action_id,
                    "label": a.label,
                    "type": a.action_type,
                    "primary": a.primary,
                    "variant": "primary" if a.primary else "default"
                }
                for a in view.actions
            ],
            "stats": {
                "total": len(view.fields),
                "missing": len(field_groups.get(DataFieldStatus.MISSING, [])),
                "warning": len(field_groups.get(DataFieldStatus.WARNING, [])),
                "invalid": len(field_groups.get(DataFieldStatus.INVALID, [])),
                "valid": len(field_groups.get(DataFieldStatus.VALID, []))
            }
        }

    def _group_fields_by_status(
        self,
        fields: List[DataFieldDisplay]
    ) -> Dict[DataFieldStatus, List[DataFieldDisplay]]:
        """按状态分组字段"""
        groups: Dict[DataFieldStatus, List[DataFieldDisplay]] = {
            DataFieldStatus.VALID: [],
            DataFieldStatus.MISSING: [],
            DataFieldStatus.INVALID: [],
            DataFieldStatus.WARNING: []
        }
        
        for field in fields:
            groups[field.status].append(field)
        
        return groups
