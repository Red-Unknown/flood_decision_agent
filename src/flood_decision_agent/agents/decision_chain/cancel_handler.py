"""取消处理模块.

支持用户中断 Plan/Spec 模式任务，处理取消命令和模式切换。
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CancelCommandType(Enum):
    """取消命令类型."""

    CANCEL = "cancel"
    RESTART = "restart"
    STOP = "stop"
    MODIFY = "modify"
    SWITCH_MODE = "switch_mode"


class ModeType(Enum):
    """模式类型."""

    PLAN = "plan"
    SPEC = "spec"
    EXECUTE = "execute"
    CHAT = "chat"


@dataclass
class CancelState:
    """取消状态数据类."""

    session_id: str
    original_mode: str
    current_mode: str
    cancelled_at: datetime = field(default_factory=datetime.now)
    preserved_context: dict = field(default_factory=dict)
    cancel_reason: str = ""
    modification_request: dict = field(default_factory=dict)


@dataclass
class ModificationRequest:
    """修改请求数据类."""

    modification_type: str = ""  # add, remove, change, adjust
    target: str = ""  # 修改目标
    content: str = ""  # 修改内容
    priority: str = "normal"  # high, normal, low
    original_text: str = ""  # 原始输入


class CancelHandler:
    """取消处理器.

    处理用户在 Plan/Spec 模式下的取消命令，支持模式切换和修改指令解析。
    """

    # 取消命令关键词映射
    CANCEL_KEYWORDS: dict[CancelCommandType, list[str]] = {
        CancelCommandType.CANCEL: [
            "取消",
            "cancel",
            "abort",
            "terminate",
            "不做了",
            "放弃",
        ],
        CancelCommandType.RESTART: [
            "换个思路",
            "重新开始",
            "重新来",
            "reset",
            "restart",
            "重来",
            "从头开始",
        ],
        CancelCommandType.STOP: [
            "停止",
            "stop",
            "halt",
            "结束",
            "退出",
            "quit",
            "别做了",
        ],
        CancelCommandType.MODIFY: [
            "修改",
            "调整",
            "改一下",
            "改改",
            "update",
            "modify",
            "change",
            "编辑",
        ],
        CancelCommandType.SWITCH_MODE: [
            "切换模式",
            "换模式",
            "切换到",
            "switch to",
            "change mode",
            "转到",
        ],
    }

    # 模式切换映射
    MODE_TRANSITIONS: dict[tuple[str, str], str] = {
        ("plan", "spec"): "plan_to_spec",
        ("spec", "plan"): "spec_to_plan",
        ("plan", "execute"): "plan_to_execute",
        ("spec", "execute"): "spec_to_execute",
        ("execute", "plan"): "execute_to_plan",
        ("execute", "spec"): "execute_to_spec",
        ("chat", "plan"): "chat_to_plan",
        ("chat", "spec"): "chat_to_spec",
    }

    def __init__(self):
        """初始化取消处理器."""
        self._session_states: dict[str, CancelState] = {}
        self._cancel_history: list[CancelState] = []

    def is_cancel_command(self, user_input: str) -> bool:
        """识别是否为取消命令.

        Args:
            user_input: 用户输入文本

        Returns:
            是否为取消命令
        """
        if not user_input or not isinstance(user_input, str):
            return False

        normalized_input = user_input.strip().lower()

        for cmd_type, keywords in self.CANCEL_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in normalized_input:
                    return True

        return False

    def get_cancel_command_type(self, user_input: str) -> CancelCommandType | None:
        """获取取消命令的具体类型.

        Args:
            user_input: 用户输入文本

        Returns:
            取消命令类型，如果不是取消命令则返回 None
        """
        if not user_input or not isinstance(user_input, str):
            return None

        normalized_input = user_input.strip().lower()

        for cmd_type, keywords in self.CANCEL_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in normalized_input:
                    return cmd_type

        return None

    def handle_cancel(
        self,
        session_id: str,
        current_state: dict[str, Any],
        reason: str = "",
    ) -> dict[str, Any]:
        """处理取消操作，保存当前状态.

        Args:
            session_id: 会话ID
            current_state: 当前状态字典
            reason: 取消原因

        Returns:
            包含取消结果和保存状态的字典
        """
        if not session_id:
            raise ValueError("session_id 不能为空")

        original_mode = current_state.get("mode", "unknown")

        cancel_state = CancelState(
            session_id=session_id,
            original_mode=original_mode,
            current_mode="cancelled",
            cancelled_at=datetime.now(),
            preserved_context=self._extract_preserved_context(current_state),
            cancel_reason=reason,
        )

        self._session_states[session_id] = cancel_state
        self._cancel_history.append(cancel_state)

        return {
            "success": True,
            "session_id": session_id,
            "cancelled_at": cancel_state.cancelled_at.isoformat(),
            "original_mode": original_mode,
            "preserved_keys": list(cancel_state.preserved_context.keys()),
            "message": f"任务已取消，模式 '{original_mode}' 的状态已保存",
        }

    def switch_mode(
        self,
        session_id: str,
        from_mode: str,
        to_mode: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """处理模式切换.

        Args:
            session_id: 会话ID
            from_mode: 源模式
            to_mode: 目标模式
            context: 切换时的上下文

        Returns:
            模式切换结果
        """
        if not session_id:
            raise ValueError("session_id 不能为空")

        if not from_mode or not to_mode:
            raise ValueError("from_mode 和 to_mode 不能为空")

        transition_key = (from_mode.lower(), to_mode.lower())
        transition_type = self.MODE_TRANSITIONS.get(
            transition_key, "unknown_transition"
        )

        preserved_context = self._extract_preserved_context(context or {})

        cancel_state = CancelState(
            session_id=session_id,
            original_mode=from_mode,
            current_mode=to_mode,
            cancelled_at=datetime.now(),
            preserved_context=preserved_context,
            cancel_reason=f"模式切换: {from_mode} -> {to_mode}",
        )

        self._session_states[session_id] = cancel_state

        return {
            "success": True,
            "session_id": session_id,
            "transition_type": transition_type,
            "from_mode": from_mode,
            "to_mode": to_mode,
            "preserved_keys": list(preserved_context.keys()),
            "message": f"已从 '{from_mode}' 切换到 '{to_mode}'",
            "can_resume": transition_type != "unknown_transition",
        }

    def parse_modification(self, user_input: str) -> dict[str, Any]:
        """解析自然语言修改指令.

        Args:
            user_input: 用户输入的修改指令

        Returns:
            解析后的修改请求字典
        """
        if not user_input or not isinstance(user_input, str):
            return {
                "modification_type": "unknown",
                "target": "",
                "content": "",
                "priority": "normal",
                "original_text": user_input or "",
            }

        modification = ModificationRequest(original_text=user_input)

        normalized_input = user_input.strip()

        # 识别修改类型
        if self._match_pattern(normalized_input, [r"添加", r"增加", r"加上", r"insert", r"add"]):
            modification.modification_type = "add"
        elif self._match_pattern(normalized_input, [r"删除", r"移除", r"去掉", r"delete", r"remove"]):
            modification.modification_type = "remove"
        elif self._match_pattern(normalized_input, [r"修改", r"更改", r"改成", r"change", r"update"]):
            modification.modification_type = "change"
        elif self._match_pattern(normalized_input, [r"调整", r"优化", r"改进", r"adjust", r"optimize"]):
            modification.modification_type = "adjust"
        else:
            modification.modification_type = "unknown"

        # 识别优先级
        if self._match_pattern(normalized_input, [r"紧急", r"重要", r"优先", r"urgent", r"high"]):
            modification.priority = "high"
        elif self._match_pattern(normalized_input, [r"次要", r"低优先级", r"low", r"minor"]):
            modification.priority = "low"

        # 提取目标（"把..."、"将..."、"对..."等结构）
        target_patterns = [
            r"[把将]([^，,。！!]+)[改删增调]",
            r"对([^，,。！!]+)[进]?行",
            r"([^，,。！!]+)[需要]?[改删增调]",
            r"关于([^，,。！!]+)",
        ]

        for pattern in target_patterns:
            match = re.search(pattern, normalized_input)
            if match:
                modification.target = match.group(1).strip()
                break

        # 提取修改内容（"改为..."、"改成..."、"添加..."等结构）
        content_patterns = [
            r"[改更]为[""']([^""']+)[""']?",
            r"[改更]成[""']([^""']+)[""']?",
            r"添加[""']([^""']+)[""']?",
            r"增加[""']([^""']+)[""']?",
            r"[""']([^""']+)[""']?[这个]?[改更]",
        ]

        for pattern in content_patterns:
            match = re.search(pattern, normalized_input)
            if match:
                modification.content = match.group(1).strip()
                break

        # 如果没有匹配到内容，取整句作为内容
        if not modification.content:
            # 移除常见的修改动词前缀
            content = re.sub(r"^(修改|调整|添加|删除|更改|优化|改进|把|将|对)\s*", "", normalized_input)
            modification.content = content

        return {
            "modification_type": modification.modification_type,
            "target": modification.target,
            "content": modification.content,
            "priority": modification.priority,
            "original_text": modification.original_text,
        }

    def get_session_state(self, session_id: str) -> CancelState | None:
        """获取会话的取消状态.

        Args:
            session_id: 会话ID

        Returns:
            取消状态，如果不存在则返回 None
        """
        return self._session_states.get(session_id)

    def can_resume(self, session_id: str) -> bool:
        """检查会话是否可以恢复.

        Args:
            session_id: 会话ID

        Returns:
            是否可以恢复
        """
        state = self._session_states.get(session_id)
        if not state:
            return False
        return bool(state.preserved_context)

    def resume_session(self, session_id: str) -> dict[str, Any]:
        """恢复会话.

        Args:
            session_id: 会话ID

        Returns:
            恢复结果
        """
        state = self._session_states.get(session_id)
        if not state:
            return {
                "success": False,
                "error": f"会话 '{session_id}' 不存在或已过期",
            }

        return {
            "success": True,
            "session_id": session_id,
            "original_mode": state.original_mode,
            "preserved_context": state.preserved_context,
            "cancel_reason": state.cancel_reason,
            "cancelled_at": state.cancelled_at.isoformat(),
        }

    def clear_session(self, session_id: str) -> bool:
        """清除会话状态.

        Args:
            session_id: 会话ID

        Returns:
            是否成功清除
        """
        if session_id in self._session_states:
            del self._session_states[session_id]
            return True
        return False

    def _extract_preserved_context(self, state: dict[str, Any]) -> dict[str, Any]:
        """提取需要保存的上下文.

        Args:
            state: 当前状态

        Returns:
            需要保存的上下文
        """
        preserved_keys = [
            "task_id",
            "user_requirements",
            "plan_content",
            "spec_content",
            "context_variables",
            "history",
            "metadata",
        ]

        preserved = {}
        for key in preserved_keys:
            if key in state:
                preserved[key] = state[key]

        return preserved

    def _match_pattern(self, text: str, patterns: list[str]) -> bool:
        """检查文本是否匹配任一模式.

        Args:
            text: 待检查文本
            patterns: 正则模式列表

        Returns:
            是否匹配
        """
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
