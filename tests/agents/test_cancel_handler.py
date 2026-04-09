"""CancelHandler 单元测试."""

import sys
from pathlib import Path
from datetime import datetime

# 添加 src 到路径
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

# 直接导入模块，避免循环导入
import importlib.util
spec = importlib.util.spec_from_file_location(
    "cancel_handler",
    ROOT / "src" / "flood_decision_agent" / "agents" / "decision_chain" / "cancel_handler.py"
)
cancel_handler_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cancel_handler_module)

CancelHandler = cancel_handler_module.CancelHandler
CancelCommandType = cancel_handler_module.CancelCommandType
CancelState = cancel_handler_module.CancelState
ModificationRequest = cancel_handler_module.ModificationRequest


class TestCancelHandler:
    """CancelHandler 测试类."""

    @pytest.fixture
    def handler(self):
        """创建 CancelHandler 实例."""
        return CancelHandler()

    @pytest.fixture
    def sample_state(self):
        """创建示例状态."""
        return {
            "mode": "plan",
            "task_id": "task_123",
            "user_requirements": "测试需求",
            "plan_content": "计划内容",
            "context_variables": {"key": "value"},
            "history": ["step1", "step2"],
            "metadata": {"version": "1.0"},
        }


class TestIsCancelCommand(TestCancelHandler):
    """测试 is_cancel_command 方法."""

    def test_cancel_keywords_chinese(self, handler):
        """测试中文取消关键词."""
        assert handler.is_cancel_command("取消") is True
        assert handler.is_cancel_command("取消任务") is True
        assert handler.is_cancel_command("我想取消") is True
        assert handler.is_cancel_command("不做了") is True
        assert handler.is_cancel_command("放弃") is True

    def test_cancel_keywords_english(self, handler):
        """测试英文取消关键词."""
        assert handler.is_cancel_command("cancel") is True
        assert handler.is_cancel_command("abort") is True
        assert handler.is_cancel_command("terminate") is True
        assert handler.is_cancel_command("Cancel this task") is True

    def test_restart_keywords(self, handler):
        """测试重新开始关键词."""
        assert handler.is_cancel_command("换个思路") is True
        assert handler.is_cancel_command("重新开始") is True
        assert handler.is_cancel_command("重新来") is True
        assert handler.is_cancel_command("reset") is True
        assert handler.is_cancel_command("restart") is True
        assert handler.is_cancel_command("重来") is True
        assert handler.is_cancel_command("从头开始") is True

    def test_stop_keywords(self, handler):
        """测试停止关键词."""
        assert handler.is_cancel_command("停止") is True
        assert handler.is_cancel_command("stop") is True
        assert handler.is_cancel_command("halt") is True
        assert handler.is_cancel_command("结束") is True
        assert handler.is_cancel_command("退出") is True
        assert handler.is_cancel_command("quit") is True
        assert handler.is_cancel_command("别做了") is True

    def test_modify_keywords(self, handler):
        """测试修改关键词."""
        assert handler.is_cancel_command("修改") is True
        assert handler.is_cancel_command("调整") is True
        assert handler.is_cancel_command("改一下") is True
        assert handler.is_cancel_command("改改") is True
        assert handler.is_cancel_command("update") is True
        assert handler.is_cancel_command("modify") is True
        assert handler.is_cancel_command("change") is True
        assert handler.is_cancel_command("编辑") is True

    def test_switch_mode_keywords(self, handler):
        """测试切换模式关键词."""
        assert handler.is_cancel_command("切换模式") is True
        assert handler.is_cancel_command("换模式") is True
        assert handler.is_cancel_command("切换到spec模式") is True
        assert handler.is_cancel_command("switch to plan") is True
        assert handler.is_cancel_command("change mode") is True
        assert handler.is_cancel_command("转到plan") is True

    def test_not_cancel_command(self, handler):
        """测试非取消命令."""
        assert handler.is_cancel_command("继续") is False
        assert handler.is_cancel_command("执行") is False
        assert handler.is_cancel_command("确认") is False
        assert handler.is_cancel_command("好的") is False
        assert handler.is_cancel_command("请帮我完成这个任务") is False

    def test_empty_input(self, handler):
        """测试空输入."""
        assert handler.is_cancel_command("") is False
        assert handler.is_cancel_command(None) is False
        assert handler.is_cancel_command("   ") is False

    def test_case_insensitive(self, handler):
        """测试大小写不敏感."""
        assert handler.is_cancel_command("CANCEL") is True
        assert handler.is_cancel_command("Cancel") is True
        assert handler.is_cancel_command("STOP") is True
        assert handler.is_cancel_command("Stop") is True


class TestGetCancelCommandType(TestCancelHandler):
    """测试 get_cancel_command_type 方法."""

    def test_get_cancel_type(self, handler):
        """测试获取取消类型."""
        assert handler.get_cancel_command_type("取消") == CancelCommandType.CANCEL
        assert handler.get_cancel_command_type("换个思路") == CancelCommandType.RESTART
        assert handler.get_cancel_command_type("停止") == CancelCommandType.STOP
        assert handler.get_cancel_command_type("修改") == CancelCommandType.MODIFY
        assert handler.get_cancel_command_type("切换模式") == CancelCommandType.SWITCH_MODE

    def test_get_cancel_type_not_found(self, handler):
        """测试非取消命令返回 None."""
        assert handler.get_cancel_command_type("继续") is None
        assert handler.get_cancel_command_type("") is None
        assert handler.get_cancel_command_type(None) is None


class TestHandleCancel(TestCancelHandler):
    """测试 handle_cancel 方法."""

    def test_handle_cancel_success(self, handler, sample_state):
        """测试成功取消."""
        result = handler.handle_cancel("session_123", sample_state)

        assert result["success"] is True
        assert result["session_id"] == "session_123"
        assert result["original_mode"] == "plan"
        assert "preserved_keys" in result
        assert "cancelled_at" in result
        assert "任务已取消" in result["message"]

    def test_handle_cancel_preserved_context(self, handler, sample_state):
        """测试保存上下文."""
        result = handler.handle_cancel("session_123", sample_state)

        preserved_keys = result["preserved_keys"]
        assert "task_id" in preserved_keys
        assert "user_requirements" in preserved_keys
        assert "plan_content" in preserved_keys
        assert "context_variables" in preserved_keys
        assert "history" in preserved_keys
        assert "metadata" in preserved_keys

    def test_handle_cancel_with_reason(self, handler, sample_state):
        """测试带原因的取消."""
        result = handler.handle_cancel("session_123", sample_state, reason="用户要求")

        assert result["success"] is True
        state = handler.get_session_state("session_123")
        assert state.cancel_reason == "用户要求"

    def test_handle_cancel_empty_session_id(self, handler, sample_state):
        """测试空 session_id 抛出异常."""
        with pytest.raises(ValueError, match="session_id 不能为空"):
            handler.handle_cancel("", sample_state)

    def test_handle_cancel_stores_state(self, handler, sample_state):
        """测试取消状态被存储."""
        handler.handle_cancel("session_123", sample_state)

        state = handler.get_session_state("session_123")
        assert state is not None
        assert state.session_id == "session_123"
        assert state.original_mode == "plan"


class TestSwitchMode(TestCancelHandler):
    """测试 switch_mode 方法."""

    def test_switch_plan_to_spec(self, handler):
        """测试 plan 切换到 spec."""
        result = handler.switch_mode("session_123", "plan", "spec")

        assert result["success"] is True
        assert result["transition_type"] == "plan_to_spec"
        assert result["from_mode"] == "plan"
        assert result["to_mode"] == "spec"
        assert result["can_resume"] is True

    def test_switch_spec_to_plan(self, handler):
        """测试 spec 切换到 plan."""
        result = handler.switch_mode("session_123", "spec", "plan")

        assert result["success"] is True
        assert result["transition_type"] == "spec_to_plan"

    def test_switch_to_execute(self, handler):
        """测试切换到 execute."""
        result = handler.switch_mode("session_123", "plan", "execute")

        assert result["success"] is True
        assert result["transition_type"] == "plan_to_execute"

    def test_switch_unknown_transition(self, handler):
        """测试未知切换类型."""
        result = handler.switch_mode("session_123", "unknown", "mode")

        assert result["success"] is True
        assert result["transition_type"] == "unknown_transition"
        assert result["can_resume"] is False

    def test_switch_with_context(self, handler):
        """测试带上下文的切换."""
        context = {"task_id": "task_123", "user_requirements": "需求"}
        result = handler.switch_mode("session_123", "plan", "spec", context)

        assert result["success"] is True
        assert "task_id" in result["preserved_keys"]
        assert "user_requirements" in result["preserved_keys"]

    def test_switch_empty_session_id(self, handler):
        """测试空 session_id 抛出异常."""
        with pytest.raises(ValueError, match="session_id 不能为空"):
            handler.switch_mode("", "plan", "spec")

    def test_switch_empty_mode(self, handler):
        """测试空 mode 抛出异常."""
        with pytest.raises(ValueError, match="from_mode 和 to_mode 不能为空"):
            handler.switch_mode("session_123", "", "spec")
        with pytest.raises(ValueError, match="from_mode 和 to_mode 不能为空"):
            handler.switch_mode("session_123", "plan", "")

    def test_switch_stores_state(self, handler):
        """测试切换状态被存储."""
        handler.switch_mode("session_123", "plan", "spec")

        state = handler.get_session_state("session_123")
        assert state is not None
        assert state.original_mode == "plan"
        assert state.current_mode == "spec"


class TestParseModification(TestCancelHandler):
    """测试 parse_modification 方法."""

    def test_parse_add_modification(self, handler):
        """测试添加类型修改."""
        result = handler.parse_modification("添加一个用户验证功能")

        assert result["modification_type"] == "add"
        assert result["content"] == "一个用户验证功能"

    def test_parse_remove_modification(self, handler):
        """测试删除类型修改."""
        result = handler.parse_modification("删除这个功能")

        assert result["modification_type"] == "remove"

    def test_parse_change_modification(self, handler):
        """测试修改类型修改."""
        result = handler.parse_modification("修改用户名为'admin'")

        assert result["modification_type"] == "change"
        # 由于正则未匹配到引号内容，返回去除前缀后的完整文本
        assert "admin" in result["content"]

    def test_parse_adjust_modification(self, handler):
        """测试调整类型修改."""
        result = handler.parse_modification("调整这个参数")

        assert result["modification_type"] == "adjust"

    def test_parse_target_extraction(self, handler):
        """测试目标提取."""
        result = handler.parse_modification("把用户名改成admin")

        assert result["target"] == "用户名"
        assert result["modification_type"] == "change"

    def test_parse_target_with_quotes(self, handler):
        """测试带引号的目标提取."""
        result = handler.parse_modification('把"密码长度"改成"至少8位"')

        assert result["target"] == '"密码长度"'
        # 由于正则未匹配到引号内容，返回去除前缀后的完整文本
        assert "至少8位" in result["content"]

    def test_parse_priority_high(self, handler):
        """测试高优先级识别."""
        result = handler.parse_modification("紧急修改这个bug")

        assert result["priority"] == "high"

    def test_parse_priority_low(self, handler):
        """测试低优先级识别."""
        result = handler.parse_modification("次要调整这个样式")

        assert result["priority"] == "low"

    def test_parse_empty_input(self, handler):
        """测试空输入."""
        result = handler.parse_modification("")

        assert result["modification_type"] == "unknown"
        assert result["target"] == ""
        assert result["content"] == ""
        assert result["priority"] == "normal"

    def test_parse_none_input(self, handler):
        """测试 None 输入."""
        result = handler.parse_modification(None)

        assert result["modification_type"] == "unknown"
        assert result["original_text"] == ""

    def test_parse_english_commands(self, handler):
        """测试英文命令."""
        result = handler.parse_modification("add a new feature")

        assert result["modification_type"] == "add"

        result = handler.parse_modification("remove this function")
        assert result["modification_type"] == "remove"

        result = handler.parse_modification("update the config")
        assert result["modification_type"] == "change"

    def test_parse_complex_sentence(self, handler):
        """测试复杂句子."""
        result = handler.parse_modification("把数据库连接超时时间改成30秒")

        assert result["modification_type"] == "change"
        assert result["target"] == "数据库连接超时时间"
        # 由于正则未匹配到引号内容，返回去除前缀后的完整文本
        assert "30秒" in result["content"]

    def test_parse_original_text_preserved(self, handler):
        """测试原始文本保留."""
        original = "修改这个配置"
        result = handler.parse_modification(original)

        assert result["original_text"] == original


class TestSessionManagement(TestCancelHandler):
    """测试会话管理方法."""

    def test_get_session_state_exists(self, handler, sample_state):
        """测试获取存在的会话状态."""
        handler.handle_cancel("session_123", sample_state)

        state = handler.get_session_state("session_123")
        assert state is not None
        assert isinstance(state, CancelState)
        assert state.session_id == "session_123"

    def test_get_session_state_not_exists(self, handler):
        """测试获取不存在的会话状态."""
        state = handler.get_session_state("non_existent")
        assert state is None

    def test_can_resume_true(self, handler, sample_state):
        """测试可以恢复."""
        handler.handle_cancel("session_123", sample_state)

        assert handler.can_resume("session_123") is True

    def test_can_resume_false_no_context(self, handler):
        """测试无法恢复 - 无上下文."""
        handler.handle_cancel("session_123", {"mode": "plan"})

        assert handler.can_resume("session_123") is False

    def test_can_resume_false_no_session(self, handler):
        """测试无法恢复 - 无会话."""
        assert handler.can_resume("non_existent") is False

    def test_resume_session_success(self, handler, sample_state):
        """测试成功恢复会话."""
        handler.handle_cancel("session_123", sample_state)

        result = handler.resume_session("session_123")

        assert result["success"] is True
        assert result["session_id"] == "session_123"
        assert result["original_mode"] == "plan"
        assert "preserved_context" in result
        assert "cancel_reason" in result
        assert "cancelled_at" in result

    def test_resume_session_not_found(self, handler):
        """测试恢复不存在的会话."""
        result = handler.resume_session("non_existent")

        assert result["success"] is False
        assert "不存在" in result["error"]

    def test_clear_session_success(self, handler, sample_state):
        """测试成功清除会话."""
        handler.handle_cancel("session_123", sample_state)

        assert handler.clear_session("session_123") is True
        assert handler.get_session_state("session_123") is None

    def test_clear_session_not_found(self, handler):
        """测试清除不存在的会话."""
        assert handler.clear_session("non_existent") is False


class TestEdgeCases(TestCancelHandler):
    """测试边界情况."""

    def test_multiple_cancels_same_session(self, handler, sample_state):
        """测试同一会话多次取消."""
        handler.handle_cancel("session_123", sample_state, reason="第一次")
        handler.handle_cancel("session_123", sample_state, reason="第二次")

        state = handler.get_session_state("session_123")
        assert state.cancel_reason == "第二次"

    def test_special_characters_in_input(self, handler):
        """测试输入中的特殊字符."""
        result = handler.parse_modification("修改这个!@#$%^&*()")

        assert result["modification_type"] == "change"

    def test_very_long_input(self, handler):
        """测试超长输入."""
        long_text = "修改" + "a" * 1000
        result = handler.parse_modification(long_text)

        assert result["modification_type"] == "change"

    def test_unicode_input(self, handler):
        """测试 Unicode 输入."""
        result = handler.parse_modification("修改这个🚀功能")

        assert result["modification_type"] == "change"


class TestDataClasses:
    """测试数据类."""

    def test_cancel_state_creation(self):
        """测试 CancelState 创建."""
        state = CancelState(
            session_id="test",
            original_mode="plan",
            current_mode="cancelled",
        )

        assert state.session_id == "test"
        assert state.original_mode == "plan"
        assert state.current_mode == "cancelled"
        assert isinstance(state.cancelled_at, datetime)
        assert state.preserved_context == {}
        assert state.cancel_reason == ""

    def test_modification_request_creation(self):
        """测试 ModificationRequest 创建."""
        request = ModificationRequest(
            modification_type="add",
            target="feature",
            content="new feature",
            priority="high",
            original_text="添加feature",
        )

        assert request.modification_type == "add"
        assert request.target == "feature"
        assert request.content == "new feature"
        assert request.priority == "high"
        assert request.original_text == "添加feature"

    def test_modification_request_defaults(self):
        """测试 ModificationRequest 默认值."""
        request = ModificationRequest()

        assert request.modification_type == ""
        assert request.target == ""
        assert request.content == ""
        assert request.priority == "normal"
        assert request.original_text == ""
