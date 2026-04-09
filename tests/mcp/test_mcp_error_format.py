"""MCP 错误格式测试

测试标准化错误格式的功能：
- 错误格式生成
- 字段完整性
- 敏感信息清理
- 错误类型识别
"""

import json
import platform
import pytest
from datetime import datetime

if platform.system() == "Windows":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class TestMCPError:
    """测试 MCPError 数据类"""

    def test_from_exception(self):
        """测试从异常创建 MCPError"""
        from src.flood_decision_agent.mcp.log.error_formatter import MCPError

        exc = ValueError("Test error")
        error = MCPError.from_exception(exc, "rainfall", "get_current_rainfall", {"extra_info": "test"})

        assert error.success is False
        assert error.error == "Test error"
        assert error.error_type == "ValueError"
        assert error.server_name == "rainfall"
        assert error.tool_name == "get_current_rainfall"
        assert error.details["extra_info"] == "test"
        assert error.timestamp

    def test_to_dict(self):
        """测试转换为字典"""
        from src.flood_decision_agent.mcp.log.error_formatter import MCPError

        error = MCPError(
            success=False,
            error="Test error",
            error_type="ValueError",
            timestamp=datetime.now().isoformat(),
            server_name="test_server",
            tool_name="test_tool",
            details={"key": "value"}
        )

        result = error.to_dict()

        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["error_type"] == "ValueError"
        assert result["server_name"] == "test_server"
        assert result["tool_name"] == "test_tool"
        assert result["details"]["key"] == "value"


class TestFormatError:
    """测试错误格式化函数"""

    def test_basic_format(self):
        """测试基本错误格式"""
        from src.flood_decision_agent.mcp.log.error_formatter import format_error

        exc = RuntimeError("API request failed")
        result = format_error(exc, "rainfall", "get_current_rainfall")

        assert result["success"] is False
        assert result["error"] == "API request failed"
        assert result["error_type"] == "RuntimeError"
        assert result["server_name"] == "rainfall"
        assert result["tool_name"] == "get_current_rainfall"
        assert result["timestamp"]
        assert "details" not in result

    def test_with_arguments(self):
        """测试包含参数"""
        from src.flood_decision_agent.mcp.log.error_formatter import format_error

        exc = ValueError("Invalid city")
        args = {"city": "UnknownCity", "provider": "qweather"}
        result = format_error(exc, "rainfall", "get_current_rainfall", arguments=args)

        assert result["details"]["arguments"]["city"] == "UnknownCity"
        assert result["details"]["arguments"]["provider"] == "qweather"

    def test_sensitive_data_redaction(self):
        """测试敏感数据清理"""
        from src.flood_decision_agent.mcp.log.error_formatter import format_error

        exc = RuntimeError("Auth failed")
        args = {
            "city": "Beijing",
            "api_key": "secret_key_12345",
            "password": "my_password",
            "token": "Bearer token123",
            "nested": {
                "secret": "nested_secret"
            }
        }
        result = format_error(exc, "rainfall", "test_tool", arguments=args)

        assert result["details"]["arguments"]["city"] == "Beijing"
        assert result["details"]["arguments"]["api_key"] == "***REDACTED***"
        assert result["details"]["arguments"]["password"] == "***REDACTED***"
        assert result["details"]["arguments"]["token"] == "***REDACTED***"
        assert result["details"]["arguments"]["nested"]["secret"] == "***REDACTED***"

    def test_with_traceback(self):
        """测试包含堆栈跟踪"""
        from src.flood_decision_agent.mcp.log.error_formatter import format_error

        try:
            raise ValueError("Test traceback")
        except ValueError as e:
            result = format_error(e, "test", "test_tool", include_traceback=True)

        assert "traceback" in result["details"]
        assert "ValueError" in result["details"]["traceback"]
        assert "Test traceback" in result["details"]["traceback"]


class TestErrorResponse:
    """测试错误响应生成"""

    def test_create_error_response(self):
        """测试创建错误响应 JSON"""
        from src.flood_decision_agent.mcp.log.error_formatter import create_error_response

        exc = RuntimeError("Network error")
        response = create_error_response(exc, "rainfall", "get_current_rainfall", {"city": "Beijing"})

        result = json.loads(response)

        assert result["success"] is False
        assert result["error"] == "Network error"
        assert result["error_type"] == "RuntimeError"
        assert result["server_name"] == "rainfall"
        assert result["tool_name"] == "get_current_rainfall"


class TestMCPErrorBuilder:
    """测试错误构建器"""

    def test_basic_builder(self):
        """测试基本构建"""
        from src.flood_decision_agent.mcp.log.error_formatter import MCPErrorBuilder

        builder = MCPErrorBuilder("rainfall", "get_current_rainfall")
        builder.with_exception(ValueError("Test error"))
        result = builder.build()

        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["error_type"] == "ValueError"

    def test_builder_with_details(self):
        """测试带详情的构建"""
        from src.flood_decision_agent.mcp.log.error_formatter import MCPErrorBuilder

        builder = MCPErrorBuilder("rainfall", "get_current_rainfall")
        builder.with_exception(RuntimeError("API failed"))
        builder.with_details(retry_count=3, last_retry="2024-01-01")
        result = builder.build()

        assert result["details"]["retry_count"] == 3
        assert result["details"]["last_retry"] == "2024-01-01"

    def test_builder_with_arguments(self):
        """测试带参数的构建"""
        from src.flood_decision_agent.mcp.log.error_formatter import MCPErrorBuilder

        builder = MCPErrorBuilder("rainfall", "get_current_rainfall")
        builder.with_exception(ValueError("Invalid input"))
        builder.with_arguments({"city": "Beijing", "api_key": "secret"})
        result = builder.build()

        assert result["details"]["arguments"]["city"] == "Beijing"
        assert result["details"]["arguments"]["api_key"] == "***REDACTED***"

    def test_builder_json(self):
        """测试构建 JSON"""
        from src.flood_decision_agent.mcp.log.error_formatter import MCPErrorBuilder

        builder = MCPErrorBuilder("rainfall", "test_tool")
        builder.with_exception(TypeError("Type error"))
        json_str = builder.build_json()

        result = json.loads(json_str)
        assert result["success"] is False
        assert result["error_type"] == "TypeError"


class TestErrorFormatCompliance:
    """测试错误格式合规性"""

    REQUIRED_FIELDS = ["success", "error", "error_type", "timestamp", "server_name", "tool_name"]

    @pytest.mark.parametrize("error_type", [
        ValueError("Value error"),
        TypeError("Type error"),
        RuntimeError("Runtime error"),
        KeyError("Key not found"),
        ConnectionError("Connection failed"),
        TimeoutError("Request timeout"),
    ])
    def test_all_error_types(self, error_type):
        """测试所有错误类型"""
        from src.flood_decision_agent.mcp.log.error_formatter import format_error

        result = format_error(error_type, "test_server", "test_tool")

        for field in self.REQUIRED_FIELDS:
            assert field in result, f"Missing field: {field}"

        assert result["success"] is False
        assert result["error"]
        assert result["error_type"] == type(error_type).__name__
        assert result["server_name"] == "test_server"
        assert result["tool_name"] == "test_tool"

    def test_timestamp_format(self):
        """测试时间戳格式"""
        from src.flood_decision_agent.mcp.log.error_formatter import format_error

        exc = ValueError("Test")
        before = datetime.now().isoformat()
        result = format_error(exc, "server", "tool")
        after = datetime.now().isoformat()

        assert before <= result["timestamp"] <= after

    def test_client_can_parse_error(self):
        """测试客户端可以解析错误"""
        from src.flood_decision_agent.mcp.log.error_formatter import format_error

        exc = RuntimeError("Service unavailable")
        result = format_error(exc, "rainfall", "get_current_rainfall")

        json_str = json.dumps(result)
        parsed = json.loads(json_str)

        assert parsed["success"] is False
        assert "error" in parsed
        assert parsed["error_type"] in ["RuntimeError", "ValueError", "ConnectionError", "TimeoutError"]


class TestErrorFormatIntegration:
    """集成测试 - 验证 MCP Server 错误响应"""

    def test_rainfall_server_error_format(self):
        """测试 rainfall_server 错误格式"""
        from src.flood_decision_agent.mcp.log.error_formatter import format_error

        exc = ValueError("未找到城市: 不存在的城市")
        result = format_error(exc, "rainfall", "get_current_rainfall", {"city": "不存在的城市"})

        assert result["success"] is False
        assert "不存在的城市" in result["error"]
        assert result["server_name"] == "rainfall"
        assert result["tool_name"] == "get_current_rainfall"
        assert result["details"]["arguments"]["city"] == "不存在的城市"

    def test_hydrology_server_error_format(self):
        """测试 hydrology_server 错误格式"""
        from src.flood_decision_agent.mcp.log.error_formatter import format_error

        exc = RuntimeError("模型运行失败")
        result = format_error(exc, "hydrology", "run_rainfall_runoff", {"basin_id": " basin001"})

        assert result["success"] is False
        assert result["server_name"] == "hydrology"
        assert result["tool_name"] == "run_rainfall_runoff"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
