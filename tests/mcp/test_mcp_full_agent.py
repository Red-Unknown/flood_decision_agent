"""完整的 UnitTaskAgent MCP 服务测试

模拟真实的 Agent 工作流程，测试所有 MCP Server：
1. Filesystem Server - 文件读写
2. Hydrology Server - 水利模型
3. Document Server - 文档处理

测试流程：
1. 创建决策规划文档 (docx)
2. 转换为 markdown
3. 运行水利模型计算
4. 保存结果到文件
"""

import asyncio
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flood_decision_agent.mcp.clients.base import MCPClientManager
from flood_decision_agent.mcp.adapters.tool_adapter import MCPToolAdapter
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.infra.logging import setup_logging

setup_logging()


class MockUnitTaskAgent:
    """模拟 UnitTaskExecutionAgent 使用 MCP 工具"""
    
    def __init__(self, agent_id: str = "MockUnitTaskAgent"):
        self.agent_id = agent_id
        self.mcp_manager = MCPClientManager()
        self.tool_adapter = MCPToolAdapter(self.mcp_manager)
        self.data_pool = SharedDataPool()
        
    async def initialize(self):
        """初始化 - 注册所有 MCP Server"""
        print(f"\n[{self.agent_id}] 初始化 MCP 连接...")
        
        # 注册 Filesystem Server
        self.mcp_manager.register_server(
            name="filesystem",
            command="python",
            args=["-m", "flood_decision_agent.mcp.servers.filesystem_server"]
        )
        
        # 注册 Hydrology Server
        self.mcp_manager.register_server(
            name="hydrology",
            command="python",
            args=["-m", "flood_decision_agent.mcp.servers.hydrology_server"]
        )
        
        # 注册 Document Server
        self.mcp_manager.register_server(
            name="document",
            command="python",
            args=["-m", "flood_decision_agent.mcp.servers.document_server"]
        )
        
        # 连接所有 Server
        connected = await self.mcp_manager.connect_all()
        print(f"[{self.agent_id}] 已连接 {connected} 个 MCP Server")
        
        return connected
    
    async def execute_task(self, task_type: str, params: dict) -> dict:
        """执行任务（模拟 UnitTaskExecutionAgent 的执行方式）"""
        print(f"\n[{self.agent_id}] 执行任务: {task_type}")
        
        # 使用 ToolAdapter 执行（兼容旧接口）
        result = await self.tool_adapter.execute(
            tool_name=task_type,
            data_pool=self.data_pool,
            config=params
        )
        
        # 保存结果到数据池
        if result.get("success"):
            self.data_pool.set(f"result_{task_type}", result)
        
        return result
    
    async def run_full_workflow(self):
        """运行完整工作流程"""
        print("\n" + "=" * 70)
        print("开始完整工作流程测试")
        print("=" * 70)
        
        workflow_results = {}
        
        # ========== 步骤 1: 创建决策规划文档 ==========
        print("\n[步骤 1] 创建决策规划文档 (docx)...")
        result1 = await self.execute_task(
            "create_sample_docx",
            {
                "filename": "flood_decision_plan.docx",
                "title": "洪水调度决策规划方案"
            }
        )
        workflow_results["create_docx"] = result1
        
        if result1.get("success"):
            print(f"  ✓ 文档创建成功: {result1.get('filepath')}")
        else:
            print(f"  ✗ 文档创建失败: {result1.get('error')}")
            return workflow_results
        
        # ========== 步骤 2: 转换为 Markdown ==========
        print("\n[步骤 2] 转换 docx 为 Markdown...")
        result2 = await self.execute_task(
            "docx_to_markdown",
            {
                "input_file": "flood_decision_plan.docx",
                "output_file": "flood_decision_plan.md",
                "include_metadata": True
            }
        )
        workflow_results["convert_md"] = result2
        
        if result2.get("success"):
            print(f"  ✓ 转换成功: {result2.get('output_file')}")
            print(f"  段落数: {result2.get('paragraphs')}")
            print(f"  表格数: {result2.get('tables')}")
        else:
            print(f"  ✗ 转换失败: {result2.get('error')}")
        
        # ========== 步骤 3: 运行降雨径流模型 ==========
        print("\n[步骤 3] 运行降雨径流模型...")
        result3 = await self.execute_task(
            "run_rainfall_runoff",
            {
                "rainfall": [10, 25, 50, 80, 60, 30, 15, 5],
                "timestamps": ["2024-01-01T00:00", "2024-01-01T01:00", 
                              "2024-01-01T02:00", "2024-01-01T03:00",
                              "2024-01-01T04:00", "2024-01-01T05:00",
                              "2024-01-01T06:00", "2024-01-01T07:00"],
                "catchment_area": 150,
                "station_id": "TEST_001"
            }
        )
        workflow_results["rainfall_runoff"] = result3
        
        if result3.get("success"):
            outputs = result3.get("outputs", {})
            print(f"  ✓ 模型运行成功")
            print(f"  总径流量: {outputs.get('total_runoff', 0):.2f} m³")
            print(f"  洪峰流量: {outputs.get('peak_discharge', 0):.2f} m³/s")
            
            # 保存到数据池供后续使用
            self.data_pool.set("runoff_result", outputs)
        else:
            print(f"  ✗ 模型运行失败: {result3.get('error')}")
        
        # ========== 步骤 4: 运行洪水演进模型 ==========
        print("\n[步骤 4] 运行洪水演进模型...")
        
        # 使用上一步的径流结果作为入流
        discharge = result3.get("outputs", {}).get("discharge", [100, 200, 400, 600, 500, 300, 200, 100])
        
        result4 = await self.execute_task(
            "run_flood_routing",
            {
                "inflow": discharge,
                "k": 3.5,
                "x": 0.25,
                "reach_length": 15.0
            }
        )
        workflow_results["flood_routing"] = result4
        
        if result4.get("success"):
            outputs = result4.get("outputs", {})
            print(f"  ✓ 演进模型运行成功")
            print(f"  洪峰削减: {outputs.get('peak_attenuation', 0):.2f} m³/s")
        else:
            print(f"  ✗ 演进模型运行失败: {result4.get('error')}")
        
        # ========== 步骤 5: 生成水库调度方案 ==========
        print("\n[步骤 5] 生成水库调度方案...")
        
        # 使用演进后的出流作为入库流量
        outflow = result4.get("outputs", {}).get("outflow", [80, 150, 300, 450, 400, 250, 150, 80])
        
        result5 = await self.execute_task(
            "calculate_dispatch_plan",
            {
                "forecast_inflow": outflow,
                "current_state": {
                    "water_level": 105.5,
                    "storage": 5000000
                },
                "constraints": {
                    "max_level": 110.0,
                    "min_level": 95.0,
                    "max_outflow": 800.0,
                    "target_level": 100.0
                }
            }
        )
        workflow_results["dispatch_plan"] = result5
        
        if result5.get("success"):
            plan = result5.get("plan", {})
            print(f"  ✓ 调度方案生成成功")
            print(f"  方案ID: {plan.get('plan_id')}")
            print(f"  时间步长: {plan.get('time_steps')}")
            print(f"  总泄量: {plan.get('total_release', 0):.2f} m³")
        else:
            print(f"  ✗ 调度方案生成失败: {result5.get('error')}")
        
        # ========== 步骤 6: 保存规划文件 ==========
        print("\n[步骤 6] 保存完整规划到文件...")
        
        # 构建完整的规划内容
        plan_content = f"""# 洪水调度决策规划方案

## 执行摘要

- **生成时间**: {datetime.now().isoformat()}
- **Agent ID**: {self.agent_id}
- **数据源**: MCP 分布式服务

## 降雨径流分析

- 总径流量: {result3.get('outputs', {}).get('total_runoff', 0):.2f} m³
- 洪峰流量: {result3.get('outputs', {}).get('peak_discharge', 0):.2f} m³/s
- 流域面积: 150 km²

## 洪水演进结果

- 洪峰削减: {result4.get('outputs', {}).get('peak_attenuation', 0):.2f} m³/s
- 演进河段长度: 15.0 km

## 水库调度方案

- 方案ID: {result5.get('plan', {}).get('plan_id', 'N/A')}
- 总泄量: {result5.get('plan', {}).get('total_release', 0):.2f} m³
- 预测末水位: {result5.get('plan', {}).get('expected_final_level', 0):.2f} m

## 数据来源

- 文档处理: Document MCP Server
- 水文计算: Hydrology MCP Server
- 文件存储: Filesystem MCP Server
"""
        
        result6 = await self.execute_task(
            "write_planning_markdown",
            {
                "plan_name": "洪水调度完整规划",
                "content": plan_content,
                "metadata": {
                    "agent_id": self.agent_id,
                    "workflow_steps": 6,
                    "mcp_servers": ["document", "hydrology", "filesystem"]
                }
            }
        )
        workflow_results["save_plan"] = result6
        
        if result6.get("success"):
            print(f"  ✓ 规划保存成功")
            print(f"  文件路径: {result6.get('filepath')}")
        else:
            print(f"  ✗ 规划保存失败: {result6.get('error')}")
        
        # ========== 步骤 7: 列出所有规划文件 ==========
        print("\n[步骤 7] 列出所有生成的文件...")
        result7 = await self.execute_task(
            "list_plans",
            {"limit": 10}
        )
        workflow_results["list_files"] = result7
        
        if result7.get("success"):
            plans = result7.get("plans", [])
            print(f"  ✓ 找到 {len(plans)} 个规划文件:")
            for plan in plans:
                print(f"    - {plan.get('filename')} ({plan.get('size')} bytes)")
        
        return workflow_results
    
    async def close(self):
        """关闭连接"""
        print(f"\n[{self.agent_id}] 关闭 MCP 连接...")
        await self.mcp_manager.close_all()
        print(f"[{self.agent_id}] 连接已关闭")


async def test_individual_servers():
    """单独测试每个 MCP Server"""
    print("\n" + "=" * 70)
    print("单独测试每个 MCP Server")
    print("=" * 70)
    
    manager = MCPClientManager()
    
    # 测试 1: Filesystem Server
    print("\n[测试 1] Filesystem Server")
    manager.register_server(
        name="filesystem",
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.filesystem_server"]
    )
    
    connected = await manager.connect_all()
    if connected > 0:
        print("  ✓ 连接成功")
        
        # 测试写入 JSON
        result = await manager.call_tool(
            "filesystem",
            "write_data_json",
            {
                "filename": "test_data",
                "data": {"test": True, "value": 123}
            }
        )
        print(f"  ✓ write_data_json: {'成功' if result.get('success') else '失败'}")
        
        # 测试列出规划
        result = await manager.call_tool(
            "filesystem",
            "list_plans",
            {"limit": 5}
        )
        print(f"  ✓ list_plans: 找到 {result.get('count', 0)} 个文件")
    else:
        print("  ✗ 连接失败")
    
    await manager.close_all()
    manager.clients.clear()
    
    # 测试 2: Hydrology Server
    print("\n[测试 2] Hydrology Server")
    manager.register_server(
        name="hydrology",
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.hydrology_server"]
    )
    
    connected = await manager.connect_all()
    if connected > 0:
        print("  ✓ 连接成功")
        
        # 测试列出模型
        result = await manager.call_tool(
            "hydrology",
            "list_hydrology_models",
            {}
        )
        models = result.get("models", [])
        print(f"  ✓ list_hydrology_models: 找到 {len(models)} 个模型")
        for model in models:
            print(f"    - {model.get('name')}: {model.get('description')}")
        
        # 测试运行降雨径流模型
        result = await manager.call_tool(
            "hydrology",
            "run_rainfall_runoff",
            {
                "rainfall": [5, 10, 20, 30, 25, 15, 10, 5],
                "catchment_area": 100
            }
        )
        if result.get("success"):
            outputs = result.get("outputs", {})
            print(f"  ✓ run_rainfall_runoff: 成功")
            print(f"    洪峰流量: {outputs.get('peak_discharge', 0):.2f} m³/s")
        else:
            print(f"  ✗ run_rainfall_runoff: {result.get('error')}")
    else:
        print("  ✗ 连接失败")
    
    await manager.close_all()
    manager.clients.clear()
    
    # 测试 3: Document Server
    print("\n[测试 3] Document Server")
    manager.register_server(
        name="document",
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.document_server"]
    )
    
    connected = await manager.connect_all()
    if connected > 0:
        print("  ✓ 连接成功")
        
        # 测试创建示例文档
        result = await manager.call_tool(
            "document",
            "create_sample_docx",
            {"filename": "test_sample.docx", "title": "测试文档"}
        )
        if result.get("success"):
            print(f"  ✓ create_sample_docx: 成功")
            print(f"    文件: {result.get('filepath')}")
            
            # 测试转换为 markdown
            result2 = await manager.call_tool(
                "document",
                "docx_to_markdown",
                {"input_file": "test_sample.docx"}
            )
            if result2.get("success"):
                print(f"  ✓ docx_to_markdown: 成功")
                print(f"    输出: {result2.get('output_file')}")
            else:
                print(f"  ✗ docx_to_markdown: {result2.get('error')}")
        else:
            print(f"  ✗ create_sample_docx: {result.get('error')}")
    else:
        print("  ✗ 连接失败")
    
    await manager.close_all()


async def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("UnitTaskAgent MCP 完整测试")
    print("=" * 70)
    
    # 第一部分: 单独测试每个 Server
    await test_individual_servers()
    
    # 第二部分: 模拟完整 Agent 工作流程
    print("\n" + "=" * 70)
    print("模拟 UnitTaskAgent 完整工作流程")
    print("=" * 70)
    
    agent = MockUnitTaskAgent(agent_id="TestUnitTaskAgent")
    
    try:
        # 初始化
        connected = await agent.initialize()
        
        if connected >= 3:
            # 运行完整工作流程
            results = await agent.run_full_workflow()
            
            # 统计结果
            success_count = sum(1 for r in results.values() if r.get("success"))
            total_count = len(results)
            
            print("\n" + "=" * 70)
            print(f"测试完成: {success_count}/{total_count} 个任务成功")
            print("=" * 70)
        else:
            print(f"\n连接数量不足 ({connected}/3)，跳过完整工作流程测试")
    
    finally:
        # 关闭连接
        await agent.close()
    
    print("\n生成的文件位置:")
    print("  - ./data/        - 输入数据文件")
    print("  - ./plans/       - 输出规划文件")


if __name__ == "__main__":
    asyncio.run(main())