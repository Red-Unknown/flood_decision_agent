"""MCP 工具完整测试脚本

测试所有 MCP 工具的功能，包括：
1. 简单工具（直接透传）
2. 复杂工具（带 LLM 解释）
3. 包装器功能验证

从环境变量获取真实 API_KEY 进行测试。
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# ============== 启动检查 ==============
def check_api_key():
    """检查 KIMI_API_KEY 环境变量"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("=" * 60)
        print("错误: 需要 KIMI_API_KEY 环境变量")
        print("=" * 60)
        print("\n请设置环境变量:")
        print("  Windows PowerShell: $env:KIMI_API_KEY=\"your-api-key\"")
        print("  Windows CMD: set KIMI_API_KEY=your-api-key")
        print("  Linux/Mac: export KIMI_API_KEY=your-api-key")
        print("\n" + "=" * 60)
        sys.exit(1)
    return api_key


# ============== 测试工具类 ==============
class TestResult:
    """测试结果记录"""
    def __init__(self, name: str):
        self.name = name
        self.success = False
        self.error = None
        self.duration = 0.0
        self.result_data = None


class MCPTester:
    """MCP 工具测试器"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.mcp_manager = None
        self.wrapper_factory = None
        self.llm_client = None
        
    async def setup(self):
        """初始化测试环境"""
        print("\n" + "=" * 60)
        print("初始化 MCP 测试环境...")
        print("=" * 60)
        
        # 导入 MCP 客户端
        from flood_decision_agent.mcp.clients import (
            MCPClientManager,
            MCPWrapperFactory,
            MCPWrappedClientManager,
        )
        from flood_decision_agent.infrastructure.llm.kimi_client import get_kimi_client
        
        # 初始化 LLM 客户端
        try:
            self.llm_client = get_kimi_client()
            print("✓ LLM 客户端初始化成功")
        except Exception as e:
            print(f"⚠ LLM 客户端初始化失败: {e}")
            self.llm_client = None
        
        # 初始化 MCP 管理器
        self.mcp_manager = MCPClientManager(auto_load_config=True)
        
        # 连接所有服务
        connected = await self.mcp_manager.connect_all()
        print(f"✓ MCP 服务连接完成: {connected} 个")
        
        # 初始化包装器工厂
        self.wrapper_factory = MCPWrapperFactory(self.mcp_manager, self.llm_client)
        print("✓ 包装器工厂初始化成功")
        
        # 列出所有可用工具
        tools = self.mcp_manager.list_all_tools()
        print(f"\n可用 MCP 工具 ({len(tools)} 个):")
        for tool in tools:
            print(f"  - {tool.name} ({tool.server_name})")
        
        return connected > 0
    
    async def teardown(self):
        """清理测试环境"""
        if self.mcp_manager:
            await self.mcp_manager.close_all()
            print("\n✓ MCP 连接已关闭")
    
    async def run_test(
        self,
        name: str,
        test_func,
        *args,
        **kwargs
    ) -> TestResult:
        """运行单个测试"""
        import time
        
        result = TestResult(name)
        print(f"\n{'='*60}")
        print(f"测试: {name}")
        print('='*60)
        
        start_time = time.time()
        try:
            result.result_data = await test_func(*args, **kwargs)
            result.success = True
            print(f"✓ 测试通过")
        except Exception as e:
            result.error = str(e)
            result.success = False
            print(f"✗ 测试失败: {e}")
        finally:
            result.duration = time.time() - start_time
            print(f"耗时: {result.duration:.2f}s")
        
        self.results.append(result)
        return result
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("测试摘要")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        
        print(f"\n总计: {total} 个测试")
        print(f"通过: {passed} 个")
        print(f"失败: {failed} 个")
        
        if failed > 0:
            print("\n失败的测试:")
            for r in self.results:
                if not r.success:
                    print(f"  - {r.name}: {r.error}")
        
        total_time = sum(r.duration for r in self.results)
        print(f"\n总耗时: {total_time:.2f}s")
        print("=" * 60)
        
        return failed == 0


# ============== 具体测试用例 ==============
async def test_simple_wrapper(tester: MCPTester) -> Dict[str, Any]:
    """测试简单包装器（直接透传）"""
    from flood_decision_agent.mcp.clients import SimpleClientWrapper
    
    # 创建简单包装器
    simple_wrapper = SimpleClientWrapper(tester.mcp_manager)
    
    # 测试调用（使用 filesystem 服务的 list_directory 工具）
    result = await simple_wrapper.execute(
        server_name="filesystem",
        tool_name="list_directory",
        arguments={"path": "."}
    )
    
    print(f"\n简单包装器结果:")
    print(f"  wrapped: {result.get('wrapped')}")
    print(f"  success: {result.get('success')}")
    print(f"  数据类型: {type(result.get('raw_data'))}")
    
    assert result.get('wrapped') == False, "简单包装器不应包装结果"
    assert result.get('success') == True, "调用应成功"
    
    return result


async def test_complex_wrapper_with_llm(tester: MCPTester) -> Dict[str, Any]:
    """测试复杂包装器（带 LLM 解释）"""
    from flood_decision_agent.mcp.clients import ComplexClientWrapper
    
    if not tester.llm_client:
        print("⚠ 跳过测试: LLM 客户端不可用")
        return {"skipped": True}
    
    # 创建复杂包装器
    complex_wrapper = ComplexClientWrapper(
        tester.mcp_manager,
        tester.llm_client
    )
    
    # 测试调用 hydrology 服务（复杂工具）
    result = await complex_wrapper.execute(
        server_name="hydrology",
        tool_name="run_rainfall_runoff",
        arguments={
            "rainfall": [10, 20, 30, 25, 15, 10, 5],
            "catchment_area": 50
        }
    )
    
    print(f"\n复杂包装器结果:")
    print(f"  wrapped: {result.get('wrapped')}")
    print(f"  success: {result.get('success')}")
    print(f"  has_explanation: {result.get('explanation') is not None}")
    print(f"  summary: {result.get('summary', 'N/A')[:100]}...")
    
    assert result.get('wrapped') == True, "复杂包装器应包装结果"
    assert result.get('success') == True, "调用应成功"
    assert result.get('explanation') is not None, "应有 LLM 解释"
    
    return result


async def test_wrapper_factory_auto_select(tester: MCPTester) -> Dict[str, Any]:
    """测试包装器工厂自动选择"""
    
    # 测试简单工具（自动选择 SimpleClientWrapper）
    result_simple = await tester.wrapper_factory.execute(
        server_name="filesystem",
        tool_name="list_directory",
        arguments={"path": "."}
    )
    
    print(f"\n工厂自动选择 - 简单工具:")
    print(f"  wrapped: {result_simple.get('wrapped')}")
    
    # 测试复杂工具（自动选择 ComplexClientWrapper）
    result_complex = await tester.wrapper_factory.execute(
        server_name="hydrology",
        tool_name="run_rainfall_runoff",
        arguments={
            "rainfall": [10, 20, 30],
            "catchment_area": 50
        }
    )
    
    print(f"\n工厂自动选择 - 复杂工具:")
    print(f"  wrapped: {result_complex.get('wrapped')}")
    print(f"  has_explanation: {result_complex.get('explanation') is not None}")
    
    return {
        "simple": result_simple,
        "complex": result_complex,
    }


async def test_prompt_manager(tester: MCPTester) -> Dict[str, Any]:
    """测试提示词管理器"""
    from flood_decision_agent.mcp.clients import PromptManager
    
    # 测试工具复杂度判断
    complex_tools = ["hipims", "hydrology", "flood_simulation", "dispatch"]
    simple_tools = ["data_hub", "data_query", "filesystem"]
    
    print("\n提示词管理器测试:")
    
    for tool in complex_tools:
        is_complex = PromptManager.is_complex_tool(tool)
        print(f"  {tool}: is_complex={is_complex}")
        assert is_complex, f"{tool} 应该是复杂工具"
    
    for tool in simple_tools:
        is_simple = PromptManager.is_simple_tool(tool)
        print(f"  {tool}: is_simple={is_simple}")
        assert is_simple, f"{tool} 应该是简单工具"
    
    # 测试提示词获取
    prompt = PromptManager.get_prompt("hipims")
    assert prompt is not None, "hipims 应该有提示词"
    assert "水利专家" in prompt, "提示词应包含专家角色"
    
    print(f"\n  hipims 提示词长度: {len(prompt)} 字符")
    
    return {"complex_tools": complex_tools, "simple_tools": simple_tools}


async def test_data_hub_server(tester: MCPTester) -> Dict[str, Any]:
    """测试 Data Hub 服务"""
    result = await tester.mcp_manager.call_tool(
        server_name="data_hub",
        tool_name="get_rainfall_data",
        arguments={"city": "北京", "provider": "auto"}
    )
    
    print(f"\nData Hub 结果:")
    print(f"  success: {result.get('success')}")
    print(f"  has_data: {'data' in result or 'rainfall' in result}")
    
    return result


async def test_hydrology_server(tester: MCPTester) -> Dict[str, Any]:
    """测试 Hydrology 服务"""
    result = await tester.mcp_manager.call_tool(
        server_name="hydrology",
        tool_name="run_rainfall_runoff",
        arguments={
            "rainfall": [10, 20, 30, 25, 15, 10, 5],
            "catchment_area": 50
        }
    )
    
    print(f"\nHydrology 结果:")
    print(f"  success: {result.get('success')}")
    if result.get('success'):
        data = result.get('data', {})
        print(f"  peak_discharge: {data.get('peak_discharge', 'N/A')}")
        print(f"  total_runoff: {data.get('total_runoff', 'N/A')}")
    
    return result


async def test_wrapped_client_manager(tester: MCPTester) -> Dict[str, Any]:
    """测试带包装器的客户端管理器"""
    from flood_decision_agent.mcp.clients import MCPWrappedClientManager
    
    # 创建带包装器的管理器
    wrapped_manager = MCPWrappedClientManager(
        mcp_manager=tester.mcp_manager,
        llm_client=tester.llm_client
    )
    
    # 测试带包装调用
    result_wrapped = await wrapped_manager.call_tool(
        server_name="hydrology",
        tool_name="run_reservoir_dispatch",
        arguments={
            "inflow": [100, 200, 350, 400, 300, 200, 150],
            "initial_level": 100.0,
            "target_level": 95.0,
            "max_outflow": 500.0
        },
        wrap_result=True
    )
    
    print(f"\n带包装调用结果:")
    print(f"  wrapped: {result_wrapped.get('wrapped')}")
    print(f"  has_explanation: {result_wrapped.get('explanation') is not None}")
    
    # 测试不带包装调用
    result_raw = await wrapped_manager.call_tool(
        server_name="filesystem",
        tool_name="list_directory",
        arguments={"path": "."},
        wrap_result=False
    )
    
    print(f"\n不带包装调用结果:")
    print(f"  type: {type(result_raw)}")
    
    return {
        "wrapped": result_wrapped,
        "raw": result_raw,
    }


# ============== 主程序 ==============
async def main():
    """运行所有测试"""
    print("=" * 60)
    print("MCP 工具完整测试")
    print("=" * 60)
    
    # 检查 API Key
    api_key = check_api_key()
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    # 创建测试器
    tester = MCPTester()
    
    try:
        # 初始化环境
        if not await tester.setup():
            print("\n✗ MCP 服务初始化失败，退出测试")
            return False
        
        # 运行测试
        await tester.run_test("提示词管理器", test_prompt_manager, tester)
        await tester.run_test("简单包装器", test_simple_wrapper, tester)
        await tester.run_test("复杂包装器(LLM)", test_complex_wrapper_with_llm, tester)
        await tester.run_test("包装器工厂自动选择", test_wrapper_factory_auto_select, tester)
        await tester.run_test("Data Hub 服务", test_data_hub_server, tester)
        await tester.run_test("Hydrology 服务", test_hydrology_server, tester)
        await tester.run_test("带包装器的客户端管理器", test_wrapped_client_manager, tester)
        
    finally:
        # 清理环境
        await tester.teardown()
    
    # 打印摘要
    success = tester.print_summary()
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
