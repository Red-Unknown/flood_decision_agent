"""MCP服务器启动和复杂Pipeline任务测试脚本

启动MCP服务器并测试Plan/Spec模式的复杂任务。
"""

import asyncio
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flood_decision_agent.app.real_pipeline import RealPipeline
from flood_decision_agent.agents.decision_chain.mode_detector import ModeDetector
from flood_decision_agent.infra.logging import setup_logging

# 配置日志
setup_logging()


class MCPServerManager:
    """MCP服务器管理器"""

    def __init__(self):
        self.processes = {}
        self.project_root = Path(__file__).parent.parent.parent

    def start_server(self, name, module_path):
        """启动单个MCP服务器"""
        print(f"  启动 {name} 服务器...")

        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"

        try:
            process = subprocess.Popen(
                [sys.executable, "-m", module_path],
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes[name] = process
            time.sleep(1)  # 等待服务器启动

            # 检查进程是否还在运行
            if process.poll() is None:
                print(f"    ✓ {name} 服务器已启动 (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate(timeout=1)
                print(f"    ✗ {name} 服务器启动失败")
                if stderr:
                    print(f"      错误: {stderr[:200]}")
                return False

        except Exception as e:
            print(f"    ✗ {name} 服务器启动异常: {e}")
            return False

    def start_all(self):
        """启动所有MCP服务器"""
        print("\n" + "=" * 70)
        print("启动MCP服务器")
        print("=" * 70)

        servers = [
            ("filesystem", "flood_decision_agent.mcp.servers.filesystem_server"),
            ("hydrology", "flood_decision_agent.mcp.servers.hydrology_server"),
            ("document", "flood_decision_agent.mcp.servers.document_server"),
        ]

        started = 0
        for name, module in servers:
            if self.start_server(name, module):
                started += 1

        print(f"\n✓ 成功启动 {started}/{len(servers)} 个MCP服务器")
        return started

    def stop_all(self):
        """停止所有MCP服务器"""
        print("\n" + "=" * 70)
        print("停止MCP服务器")
        print("=" * 70)

        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=3)
                print(f"  ✓ {name} 服务器已停止")
            except:
                try:
                    process.kill()
                    print(f"  ✓ {name} 服务器已强制停止")
                except:
                    print(f"  ✗ {name} 服务器停止失败")

        self.processes.clear()


def test_mode_detection():
    """测试模式检测"""
    print("\n" + "=" * 70)
    print("测试模式检测")
    print("=" * 70)

    detector = ModeDetector()

    test_cases = [
        ("北京今天天气怎么样？", "简单查询"),
        ("分析未来3天的降雨情况并给出调度建议", "中等复杂度"),
        ("""请帮我完成以下复杂的水利调度分析任务：
1. 收集过去30天的降雨数据
2. 分析流域土壤饱和度
3. 预测未来7天的来水情况
4. 考虑下游生态流量需求
5. 制定多目标优化调度方案
6. 评估不同方案的风险和收益
7. 生成详细的调度报告""", "复杂任务"),
    ]

    for user_input, description in test_cases:
        print(f"\n测试: {description}")
        print(f"输入: {user_input[:50]}...")

        mode = detector.detect(user_input)
        print(f"检测模式: {mode}")

        # 显示详细分析
        metrics = detector._calculate_metrics(user_input)
        print(f"  字符数: {metrics.char_count}")
        print(f"  句子数: {metrics.sentence_count}")
        print(f"  技术术语数: {metrics.technical_term_count}")


def test_plan_mode_with_mcp():
    """测试Plan模式（带MCP集成）"""
    print("\n" + "=" * 70)
    print("测试Plan模式（带MCP集成）")
    print("=" * 70)

    pipeline = RealPipeline()

    user_input = """请帮我制定一个水库调度计划：
1. 获取未来3天的降雨预报
2. 计算入库流量
3. 考虑下游防洪安全
4. 制定泄洪方案"""

    print(f"\n用户输入: {user_input}")

    start_time = time.time()
    result = pipeline.run(user_input)
    elapsed = time.time() - start_time

    print(f"\n执行结果:")
    print(f"  成功: {result.success}")
    print(f"  执行时间: {elapsed:.2f} 秒")
    print(f"  决策链节点数: {len(result.decision_chain)}")
    print(f"  执行结果数: {len(result.execution_results)}")

    if result.decision_chain:
        print(f"\n决策链节点:")
        for i, node in enumerate(result.decision_chain):
            print(f"  {i+1}. {node.get('node_id')} ({node.get('task_type')})")

    if result.execution_results:
        print(f"\n执行详情:")
        for res in result.execution_results:
            status_icon = "✓" if res['status'] == 'success' else "✗"
            print(f"  {status_icon} {res['node_id']}: {res['status']}")
            if 'result' in res and isinstance(res['result'], dict):
                output = res['result'].get('output', {})
                if output:
                    print(f"      输出: {str(output)[:100]}...")

    return result


def test_spec_mode_with_mcp():
    """测试Spec模式（带MCP集成）"""
    print("\n" + "=" * 70)
    print("测试Spec模式（带MCP集成）")
    print("=" * 70)

    pipeline = RealPipeline()

    user_input = """请完成以下专业水利调度分析任务：

【任务背景】
某流域近期连续降雨，土壤饱和度较高，需要制定科学的洪水调度方案。

【具体要求】
1. 数据收集阶段：
   - 收集过去7天的逐小时降雨数据
   - 获取当前土壤饱和度数据
   - 查询水库当前水位和库容

2. 水文分析阶段：
   - 使用单位线法计算径流
   - 预测未来72小时的入库流量过程
   - 分析不同降雨情景下的洪水规模

3. 调度决策阶段：
   - 考虑下游防洪标准（50年一遇）
   - 评估水库大坝安全
   - 兼顾下游生态流量需求（不小于10m³/s）
   - 优化发电效益

4. 方案输出阶段：
   - 生成3套调度方案（保守/适中/激进）
   - 每套方案包含详细的泄洪过程
   - 风险评估和应急预案
   - 完整的决策报告

【约束条件】
- 最大泄流量不超过5000m³/s
- 水位控制不超过汛限水位2m
- 调度周期为72小时"""

    print(f"\n用户输入: {user_input[:200]}...")

    start_time = time.time()
    result = pipeline.run(user_input)
    elapsed = time.time() - start_time

    print(f"\n执行结果:")
    print(f"  成功: {result.success}")
    print(f"  执行时间: {elapsed:.2f} 秒")
    print(f"  决策链节点数: {len(result.decision_chain)}")
    print(f"  执行结果数: {len(result.execution_results)}")

    if result.decision_chain:
        print(f"\n决策链节点:")
        for i, node in enumerate(result.decision_chain):
            node_id = node.get('node_id', 'unknown')
            task_type = node.get('task_type', 'unknown')
            print(f"  {i+1}. {node_id} ({task_type})")

    if result.execution_results:
        print(f"\n执行详情:")
        for res in result.execution_results:
            status_icon = "✓" if res['status'] == 'success' else "✗"
            node_id = res.get('node_id', 'unknown')
            status = res.get('status', 'unknown')
            print(f"  {status_icon} {node_id}: {status}")

            # 显示工具调用信息
            if 'result' in res and isinstance(res['result'], dict):
                output = res['result'].get('output', {})
                if output:
                    output_str = str(output)
                    print(f"      输出: {output_str[:150]}...")

                # 检查是否有MCP工具调用
                tool_calls = res['result'].get('tool_calls', [])
                if tool_calls:
                    print(f"      工具调用:")
                    for call in tool_calls:
                        tool_name = call.get('tool', 'unknown')
                        print(f"        - {tool_name}")

    return result


async def test_mcp_tools_directly():
    """直接测试MCP工具"""
    print("\n" + "=" * 70)
    print("直接测试MCP工具")
    print("=" * 70)

    from flood_decision_agent.mcp.clients.base import MCPClientManager
    from flood_decision_agent.core.shared_data_pool import SharedDataPool

    # 创建客户端管理器
    manager = MCPClientManager()

    # 从配置加载
    print("\n[1/3] 加载MCP配置...")
    manager.load_from_config("configs/mcp/servers.yaml")

    # 连接服务器
    print("\n[2/3] 连接MCP服务器...")
    connected = await manager.connect_all()
    print(f"✓ 已连接 {connected} 个服务器")

    # 显示可用工具
    print("\n[3/3] 可用MCP工具:")
    all_tools = []
    for name, client in manager.clients.items():
        if client._connected:
            tools = client.tools if hasattr(client, 'tools') else []
            print(f"\n  {name} ({len(tools)} 个工具):")
            for tool in tools[:5]:  # 只显示前5个
                tool_name = tool.get('name', 'unknown')
                desc = tool.get('description', '')[:50]
                print(f"    - {tool_name}: {desc}...")
            all_tools.extend(tools)

    # 测试执行降雨查询工具
    rainfall_tools = [t for t in all_tools if 'rain' in t.get('name', '').lower()]
    if rainfall_tools:
        print(f"\n测试执行降雨查询工具...")
        tool = rainfall_tools[0]
        tool_name = tool.get('name')

        try:
            result = await manager.call_tool(
                server_name="hydrology",
                tool_name=tool_name,
                params={"city": "北京", "days": 3}
            )
            print(f"  ✓ 工具执行成功")
            print(f"    结果: {str(result)[:200]}...")
        except Exception as e:
            print(f"  ✗ 工具执行失败: {e}")

    # 关闭连接
    await manager.close_all()
    print("\n✓ MCP连接已关闭")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("MCP服务器启动和复杂Pipeline任务测试")
    print("测试Plan模式和Spec模式的完整MCP集成")
    print("=" * 70)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 检查API Key
    if not os.environ.get("KIMI_API_KEY"):
        print("\n✗ 错误: 需要设置 KIMI_API_KEY 环境变量")
        print("  请运行: $env:KIMI_API_KEY='your-api-key'")
        sys.exit(1)

    # 创建MCP服务器管理器
    mcp_manager = MCPServerManager()

    try:
        # 1. 启动MCP服务器
        mcp_manager.start_all()

        # 2. 等待服务器完全启动
        print("\n等待MCP服务器初始化...")
        time.sleep(3)

        # 3. 测试模式检测
        test_mode_detection()

        # 4. 测试Plan模式
        plan_result = test_plan_mode_with_mcp()

        # 5. 测试Spec模式
        spec_result = test_spec_mode_with_mcp()

        # 6. 直接测试MCP工具
        asyncio.run(test_mcp_tools_directly())

        # 显示最终总结
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        print(f"\nPlan模式:")
        print(f"  成功: {plan_result.success}")
        print(f"  节点数: {len(plan_result.decision_chain)}")
        print(f"  执行结果数: {len(plan_result.execution_results)}")

        print(f"\nSpec模式:")
        print(f"  成功: {spec_result.success}")
        print(f"  节点数: {len(spec_result.decision_chain)}")
        print(f"  执行结果数: {len(spec_result.execution_results)}")

        print("\n" + "=" * 70)
        print("所有测试完成！")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 停止MCP服务器
        mcp_manager.stop_all()


if __name__ == "__main__":
    main()
