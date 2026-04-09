"""
超时控制工具模块单元测试
"""

import asyncio
import pytest
from unittest.mock import Mock, patch

from src.flood_decision_agent.shared.utils.timeout_utils import (
    TimeoutError,
    with_timeout,
    async_timeout,
    TimeoutManager,
    get_timeout,
    set_timeout,
    run_with_timeout,
    RetryWithTimeout,
    default_timeout_manager,
)


class TestTimeoutError:
    """测试TimeoutError异常"""

    def test_basic_error(self):
        """测试基本错误"""
        error = TimeoutError("Test timeout")
        assert str(error) == "Test timeout"
        assert error.timeout_seconds is None
        assert error.operation_name is None

    def test_error_with_details(self):
        """测试带详细信息的错误"""
        error = TimeoutError(
            message="Operation failed",
            timeout_seconds=30.0,
            operation_name="test_op"
        )
        assert "Operation failed" in str(error)
        assert "test_op" in str(error)
        assert "30" in str(error)
        assert error.timeout_seconds == 30.0
        assert error.operation_name == "test_op"


class TestWithTimeoutDecorator:
    """测试with_timeout装饰器"""

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """测试成功执行"""
        @with_timeout(5.0)
        async def fast_func():
            await asyncio.sleep(0.1)
            return "success"

        result = await fast_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_raises_error(self):
        """测试超时抛出错误"""
        @with_timeout(0.1, operation_name="slow_op")
        async def slow_func():
            await asyncio.sleep(1.0)
            return "completed"

        with pytest.raises(TimeoutError) as exc_info:
            await slow_func()

        assert "slow_op" in str(exc_info.value)
        assert exc_info.value.timeout_seconds == 0.1

    @pytest.mark.asyncio
    async def test_timeout_with_callback(self):
        """测试带回调的超时"""
        callback_called = False

        def on_timeout():
            nonlocal callback_called
            callback_called = True

        @with_timeout(0.1, on_timeout=on_timeout)
        async def slow_func():
            await asyncio.sleep(1.0)
            return "completed"

        with pytest.raises(TimeoutError):
            await slow_func()

        assert callback_called

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        """测试保留函数名称"""
        @with_timeout(5.0)
        async def my_function():
            return "result"

        assert my_function.__name__ == "my_function"


class TestAsyncTimeoutContextManager:
    """测试async_timeout上下文管理器"""

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """测试成功执行"""
        async with async_timeout(5.0, "test_op"):
            await asyncio.sleep(0.1)
            result = "success"

        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_raises_error(self):
        """测试超时抛出错误"""
        with pytest.raises(TimeoutError) as exc_info:
            async with async_timeout(0.1, "test_op"):
                await asyncio.sleep(1.0)

        assert "test_op" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_suppress_timeout(self):
        """测试抑制超时"""
        # 不应该抛出异常
        async with async_timeout(0.1, "test_op", suppress_timeout=True):
            await asyncio.sleep(1.0)

        # 如果执行到这里，说明超时被正确抑制
        assert True


class TestTimeoutManager:
    """测试TimeoutManager类"""

    def test_default_timeouts(self):
        """测试默认超时配置"""
        manager = TimeoutManager()

        assert manager.get_timeout("llm_chat") == 60.0
        assert manager.get_timeout("mcp_call") == 30.0
        assert manager.get_timeout("task_execute") == 300.0

    def test_custom_timeouts(self):
        """测试自定义超时配置"""
        custom = {"llm_chat": 90.0, "custom_op": 45.0}
        manager = TimeoutManager(custom_timeouts=custom)

        assert manager.get_timeout("llm_chat") == 90.0
        assert manager.get_timeout("custom_op") == 45.0
        assert manager.get_timeout("mcp_call") == 30.0  # 默认值

    def test_set_timeout(self):
        """测试设置超时"""
        manager = TimeoutManager()
        manager.set_timeout("new_op", 15.0)

        assert manager.get_timeout("new_op") == 15.0

    def test_unknown_operation_uses_default(self):
        """测试未知操作使用默认超时"""
        manager = TimeoutManager()

        assert manager.get_timeout("unknown_op") == 30.0

    @pytest.mark.asyncio
    async def test_decorator_for(self):
        """测试decorator_for方法"""
        manager = TimeoutManager()
        decorator = manager.decorator_for("llm_chat")

        @decorator
        async def test_func():
            await asyncio.sleep(0.1)
            return "success"

        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_context_for(self):
        """测试context_for方法"""
        manager = TimeoutManager()

        async with manager.context_for("llm_chat"):
            await asyncio.sleep(0.1)
            result = "success"

        assert result == "success"


class TestGlobalTimeoutFunctions:
    """测试全局超时函数"""

    def test_get_timeout(self):
        """测试get_timeout函数"""
        timeout = get_timeout("llm_chat")
        assert timeout == 60.0

    def test_set_timeout(self):
        """测试set_timeout函数"""
        original = get_timeout("test_op")

        set_timeout("test_op", 45.0)
        assert get_timeout("test_op") == 45.0

        # 恢复原始值
        set_timeout("test_op", original)


class TestRunWithTimeout:
    """测试run_with_timeout函数"""

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """测试成功执行"""
        async def coro():
            await asyncio.sleep(0.1)
            return "success"

        result = await run_with_timeout(coro(), 5.0, "test_op")
        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_raises_error(self):
        """测试超时抛出错误"""
        async def slow_coro():
            await asyncio.sleep(1.0)
            return "completed"

        with pytest.raises(TimeoutError) as exc_info:
            await run_with_timeout(slow_coro(), 0.1, "slow_op")

        assert "slow_op" in str(exc_info.value)


class TestRetryWithTimeout:
    """测试RetryWithTimeout类"""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        """测试第一次尝试成功"""
        retry = RetryWithTimeout(timeout_seconds=5.0, max_retries=3)

        async def success_func():
            return "success"

        result = await retry.execute(success_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_success_after_retries(self):
        """测试重试后成功"""
        retry = RetryWithTimeout(
            timeout_seconds=5.0,
            max_retries=3,
            retry_delay=0.1
        )

        call_count = 0

        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                await asyncio.sleep(10.0)  # 触发超时
            return "success"

        result = await retry.execute(flaky_func)
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_all_retries_fail(self):
        """测试所有重试都失败"""
        retry = RetryWithTimeout(
            timeout_seconds=0.1,
            max_retries=2,
            retry_delay=0.05,
            operation_name="flaky_op"
        )

        async def always_slow():
            await asyncio.sleep(1.0)
            return "success"

        with pytest.raises(TimeoutError) as exc_info:
            await retry.execute(always_slow)

        assert "flaky_op" in str(exc_info.value)
        assert "2 attempts" in str(exc_info.value)


class TestIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_decorator_with_manager(self):
        """测试装饰器与管理器集成"""
        manager = TimeoutManager()

        @manager.decorator_for("llm_chat")
        async def llm_call():
            await asyncio.sleep(0.1)
            return "llm_response"

        result = await llm_call()
        assert result == "llm_response"

    @pytest.mark.asyncio
    async def test_nested_timeouts(self):
        """测试嵌套超时"""
        @with_timeout(2.0, "outer")
        async def outer():
            async with async_timeout(1.0, "inner"):
                await asyncio.sleep(0.5)
                return "success"

        result = await outer()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_with_exception(self):
        """测试超时与异常处理"""
        @with_timeout(5.0)
        async def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await failing_func()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
