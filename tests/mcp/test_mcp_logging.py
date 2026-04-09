"""MCP 日志系统测试

测试 MCP 日志基础设施的功能：
- 日志记录器创建
- 日志轮转
- 日志分级
- 上下文管理器
"""

import asyncio
import os
import platform
import sys
import time
from pathlib import Path
from datetime import date

import pytest


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class TestMCPLoggerFactory:
    """测试日志记录器工厂"""

    def test_initialize(self):
        """测试日志系统初始化"""
        from src.flood_decision_agent.mcp.log.logger import MCPLoggerFactory
        
        test_log_dir = Path("logs/test_mcp")
        
        MCPLoggerFactory.initialize(log_dir=str(test_log_dir), max_size=1024*1024, retention_days=3)
        
        assert MCPLoggerFactory._initialized
        assert MCPLoggerFactory._log_dir == test_log_dir
        assert MCPLoggerFactory._max_size == 1024*1024
        assert MCPLoggerFactory._retention_days == 3
        
    def test_get_logger(self):
        """测试获取日志记录器"""
        from src.flood_decision_agent.mcp.log.logger import get_mcp_logger, MCPLoggerFactory
        
        test_log_dir = Path("logs/test_mcp")
        MCPLoggerFactory.initialize(log_dir=str(test_log_dir), max_size=1024*1024, retention_days=3)
        
        logger1 = get_mcp_logger("test_server")
        logger2 = get_mcp_logger("test_server")
        
        assert logger1 is logger2
        
        server_log_dir = test_log_dir / "test_server"
        assert server_log_dir.exists()
        
    def test_multiple_servers(self):
        """测试多个服务器日志记录器"""
        from src.flood_decision_agent.mcp.log.logger import get_mcp_logger, MCPLoggerFactory
        
        test_log_dir = Path("logs/test_multiple")
        MCPLoggerFactory.initialize(log_dir=str(test_log_dir))
        
        logger1 = get_mcp_logger("server1")
        logger2 = get_mcp_logger("server2")
        logger3 = get_mcp_logger("server3")
        
        assert logger1 is not logger2
        assert logger2 is not logger3
        
        assert (test_log_dir / "server1").exists()
        assert (test_log_dir / "server2").exists()
        assert (test_log_dir / "server3").exists()


class TestToolCallContext:
    """测试工具调用上下文管理器"""

    def test_successful_call(self):
        """测试成功调用"""
        from src.flood_decision_agent.mcp.log import get_mcp_logger, ToolCallContext
        from src.flood_decision_agent.mcp.log.logger import MCPLoggerFactory
        
        test_log_dir = Path("logs/test_context")
        MCPLoggerFactory.initialize(log_dir=str(test_log_dir))
        
        logger = get_mcp_logger("test_context_server")
        
        with ToolCallContext("test_context_server", "test_tool", {"arg1": "value1"}, logger):
            time.sleep(0.01)

    def test_failed_call(self):
        """测试失败调用"""
        from src.flood_decision_agent.mcp.log import get_mcp_logger, ToolCallContext
        from src.flood_decision_agent.mcp.log.logger import MCPLoggerFactory
        
        test_log_dir = Path("logs/test_context_error")
        MCPLoggerFactory.initialize(log_dir=str(test_log_dir))
        
        logger = get_mcp_logger("test_error_server")
        
        with pytest.raises(ValueError):
            with ToolCallContext("test_error_server", "failing_tool", {}, logger):
                raise ValueError("Test error")

    def test_context_duration(self):
        """测试上下文持续时间"""
        from src.flood_decision_agent.mcp.log import get_mcp_logger, ToolCallContext
        from src.flood_decision_agent.mcp.log.logger import MCPLoggerFactory
        
        test_log_dir = Path("logs/test_duration")
        MCPLoggerFactory.initialize(log_dir=str(test_log_dir))
        
        logger = get_mcp_logger("test_duration_server")
        
        with ToolCallContext("test_duration_server", "test_tool", {}, logger) as ctx:
            time.sleep(0.05)
        
        assert ctx.duration_ms >= 50
        assert ctx.success


class TestLogFormatters:
    """测试日志格式化器"""

    def test_format_tool_call_start(self):
        """测试工具调用开始格式化"""
        from src.flood_decision_agent.mcp.log.formatters import format_tool_call_start
        
        msg = format_tool_call_start("test_server", "test_tool", {"arg1": "value1"})
        
        assert "test_server" in msg
        assert "test_tool" in msg
        assert "arg1" in msg
        assert "value1" in msg

    def test_format_tool_call_end(self):
        """测试工具调用结束格式化"""
        from src.flood_decision_agent.mcp.log.formatters import format_tool_call_end
        
        msg = format_tool_call_end("test_server", "test_tool", 123.45, True)
        
        assert "test_server" in msg
        assert "test_tool" in msg
        assert "123.45" in msg
        assert "成功" in msg
        
        msg_fail = format_tool_call_end("test_server", "test_tool", 123.45, False)
        
        assert "失败" in msg_fail

    def test_format_api_request(self):
        """测试 API 请求格式化"""
        from src.flood_decision_agent.mcp.log.formatters import format_api_request
        
        msg = format_api_request("qweather", "https://api.example.com", {"key": "value"})
        
        assert "qweather" in msg
        assert "api.example.com" in msg

    def test_format_error(self):
        """测试错误格式化"""
        from src.flood_decision_agent.mcp.log.formatters import format_error
        
        error = ValueError("Test error message")
        msg = format_error(error, "test_server", "test_tool", {"context": "test"})
        
        assert "test_server" in msg
        assert "test_tool" in msg
        assert "ValueError" in msg
        assert "Test error message" in msg


class TestLogHandlers:
    """测试日志处理器"""

    def test_rotation_handler_creation(self):
        """测试轮转处理器创建"""
        from src.flood_decision_agent.mcp.log.handlers import LogRotationHandler
        
        test_log_dir = Path("logs/test_rotation")
        handler = LogRotationHandler(test_log_dir, max_size_mb=1, retention_days=7)
        
        assert handler.log_dir == test_log_dir
        assert handler.max_size_bytes == 1024 * 1024
        assert handler.retention_days == 7

    def test_log_filter(self):
        """测试日志过滤器"""
        import importlib
        import sys
        
        if 'src.flood_decision_agent.mcp.log.handlers' in sys.modules:
            importlib.reload(sys.modules['src.flood_decision_agent.mcp.log.handlers'])
        
        from src.flood_decision_agent.mcp.log.handlers import LogFilter
        
        filter1 = LogFilter(min_level="INFO", include_servers=["server1", "server2"])
        
        result1 = filter1.should_log("INFO", "server1")
        result2 = filter1.should_log("WARNING", "server1")
        result3 = filter1.should_log("DEBUG", "server1")
        result4 = filter1.should_log("INFO", "server3")
        
        assert result1 == True, f"Test 1 failed: {result1}"
        assert result2 == True, f"Test 2 failed: {result2}"
        assert result3 == False, f"Test 3 failed: {result3}"
        assert result4 == False, f"Test 4 failed: {result4}"
        
        filter2 = LogFilter(min_level="WARNING", exclude_servers=["server1"])
        
        result5 = filter2.should_log("INFO", "server1")
        result6 = filter2.should_log("WARNING", "server2")
        
        assert result5 == False, f"Test 5 failed (server1 excluded): {result5}"
        assert result6 == True, f"Test 6 failed (server2 allowed): {result6}"


class TestLogIntegration:
    """集成测试"""

    def test_log_file_creation(self):
        """测试日志文件创建"""
        from src.flood_decision_agent.mcp.log.logger import get_mcp_logger, MCPLoggerFactory
        
        test_log_dir = Path("logs/test_integration")
        MCPLoggerFactory.initialize(log_dir=str(test_log_dir))
        
        logger = get_mcp_logger("integration_test")
        
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        time.sleep(0.1)
        
        log_file = test_log_dir / "integration_test" / f"mcp-integration_test-{date.today().isoformat()}.log"
        
        assert log_file.exists()

    def test_log_with_arguments_sanitization(self):
        """测试日志参数清理"""
        from src.flood_decision_agent.mcp.log import get_mcp_logger
        from src.flood_decision_agent.mcp.log.logger import MCPLoggerFactory
        
        test_log_dir = Path("logs/test_sanitize")
        MCPLoggerFactory.initialize(log_dir=str(test_log_dir))
        
        logger = get_mcp_logger("sanitize_test")
        
        safe_args = {"city": "Beijing", "api_key": "secret123"}
        
        logger.info(f"Calling tool with args: {safe_args}")
        
        from src.flood_decision_agent.mcp.log.error_formatter import _sanitize_arguments
        
        sanitized = _sanitize_arguments(safe_args)
        
        assert sanitized["city"] == "Beijing"
        assert sanitized["api_key"] == "***REDACTED***"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
