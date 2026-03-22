"""
环境修复脚本

解决以下问题：
1. API_KEY 环境变量检测不到
2. 模块导入错误
"""

import os
import sys
import subprocess


def check_and_fix_api_key():
    """检查并修复 API Key 问题"""
    print("=" * 70)
    print("检查 API_KEY 环境变量")
    print("=" * 70)
    
    # 方法1: 检查当前环境变量
    api_key = os.environ.get("KIMI_API_KEY")
    
    if api_key:
        masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✓ 当前终端已检测到 KIMI_API_KEY: {masked}")
        return True
    
    print("✗ 当前终端未检测到 KIMI_API_KEY")
    print("\n可能的原因：")
    print("  1. 使用 setx 设置后未重启终端")
    print("  2. 在系统环境变量中设置但未重新加载")
    print("  3. 使用 PowerShell 但设置方式不正确")
    
    print("\n" + "-" * 70)
    print("解决方案（选择一种）：")
    print("-" * 70)
    
    print("\n【方案1】当前终端临时设置（立即生效）：")
    print("  PowerShell: $env:KIMI_API_KEY='your_key'")
    print("  CMD: set KIMI_API_KEY=your_key")
    
    print("\n【方案2】永久设置（需重启终端）：")
    print("  PowerShell: [Environment]::SetEnvironmentVariable('KIMI_API_KEY', 'your_key', 'User')")
    print("  CMD: setx KIMI_API_KEY your_key")
    
    print("\n【方案3】在当前脚本中直接设置（仅本次运行）：")
    print("  编辑 debug/test_unit_task_executor_interactive.py")
    print("  在文件开头添加: os.environ['KIMI_API_KEY'] = 'your_key'")
    
    return False


def check_and_fix_module():
    """检查并修复模块导入问题"""
    print("\n" + "=" * 70)
    print("检查模块导入")
    print("=" * 70)
    
    # 检查是否在正确的目录
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # 检查 src 目录是否存在
    src_path = os.path.join(current_dir, "src")
    if not os.path.exists(src_path):
        print(f"✗ 未找到 src 目录: {src_path}")
        print("  请确保在项目根目录运行脚本")
        return False
    
    print(f"✓ 找到 src 目录")
    
    # 检查包是否已安装
    try:
        import flood_decision_agent
        print(f"✓ flood_decision_agent 已安装")
        print(f"  位置: {flood_decision_agent.__file__}")
        return True
    except ImportError:
        print(f"✗ flood_decision_agent 未安装")
        
        print("\n" + "-" * 70)
        print("解决方案：")
        print("-" * 70)
        
        print("\n【方案1】安装包（推荐）：")
        print("  pip install -e .")
        
        print("\n【方案2】添加路径到 PYTHONPATH：")
        print("  PowerShell: $env:PYTHONPATH='./src'")
        print("  Python: sys.path.insert(0, './src')")
        
        return False


def fix_module_import():
    """自动修复模块导入"""
    print("\n" + "=" * 70)
    print("尝试自动修复模块导入")
    print("=" * 70)
    
    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    src_path = os.path.join(project_root, "src")
    
    if os.path.exists(src_path):
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            print(f"✓ 已添加 {src_path} 到 Python 路径")
        
        # 再次尝试导入
        try:
            import flood_decision_agent
            print(f"✓ 导入成功: {flood_decision_agent.__file__}")
            return True
        except ImportError as e:
            print(f"✗ 导入失败: {e}")
            return False
    else:
        print(f"✗ 未找到 src 目录: {src_path}")
        return False


def create_fixed_demo_script():
    """创建一个修复后的演示脚本"""
    print("\n" + "=" * 70)
    print("创建修复后的演示脚本")
    print("=" * 70)
    
    script_content = '''"""
修复后的演示脚本 - 自动处理环境变量和模块导入
"""

import os
import sys

# ========== 自动修复模块导入 ==========
# 添加项目 src 目录到 Python 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# ========== API Key 设置 ==========
# 方法1: 从环境变量读取（推荐）
api_key = os.environ.get("KIMI_API_KEY")

# 方法2: 如果环境变量未设置，可以在这里直接设置（仅测试用）
# 注意：生产环境请勿硬编码 API Key
if not api_key:
    # 取消下面一行的注释并填入你的 API Key
    # api_key = "your_api_key_here"
    pass

if not api_key:
    print("=" * 70)
    print("错误: 未找到 KIMI_API_KEY")
    print("=" * 70)
    print("\\n请设置环境变量：")
    print("  PowerShell: $env:KIMI_API_KEY='your_key'")
    print("  CMD: set KIMI_API_KEY=your_key")
    print("\\n或在脚本中取消注释并设置 api_key 变量")
    sys.exit(1)

# 设置到环境变量（供其他模块使用）
os.environ["KIMI_API_KEY"] = api_key
masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
print(f"✓ KIMI_API_KEY 已配置: {masked_key}")

# ========== 继续导入和运行 ==========
try:
    from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
    from flood_decision_agent.core.shared_data_pool import SharedDataPool
    from flood_decision_agent.tools.registry import ToolMetadata, register_tool
    print("✓ 模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    print("\\n请确保已安装包: pip install -e .")
    sys.exit(1)


# ========== 演示代码 ==========
def print_section(title):
    print("\\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_1():
    """场景1: 上游指定工具充足"""
    print_section("场景1: 上游指定工具充足")
    
    @register_tool(ToolMetadata(
        name="demo_rainfall_api",
        description="降雨预报API",
        task_types={"hydrological_model"},
        priority=10,
        output_keys={"rainfall"}
    ))
    def demo_rainfall_api(data_pool, config):
        return {"rainfall": {"24h": 50.5, "unit": "mm"}}
    
    agent = UnitTaskExecutionAgent(agent_id="Demo1", enable_common_tools=False)
    data_pool = SharedDataPool()
    
    result = agent.execute_task(
        node_id="N1",
        task_type="hydrological_model",
        data_pool=data_pool,
        tools=[{"tool_name": "demo_rainfall_api", "tool_config": {}}],
        execution_strategy="single",
    )
    
    print(f"状态: {result['status']}")
    print(f"工具: {result['metrics']['tools_used']}")
    print(f"输出: {result['output']}")


def demo_2():
    """场景2: 上游工具不足，自主补充"""
    print_section("场景2: 上游工具不足，自主补充")
    
    agent = UnitTaskExecutionAgent(agent_id="Demo2")
    data_pool = SharedDataPool()
    
    result = agent.execute_task(
        node_id="N2",
        task_type="data_query",  # 会自主选用常用工具
        data_pool=data_pool,
        tools=[],  # 空列表触发自主选用
        execution_strategy="auto",
    )
    
    print(f"状态: {result['status']}")
    print(f"自主选用工具: {result['metrics']['tools_used']}")


def main():
    print("\\n" + "=" * 70)
    print("  UnitTaskExecutionAgent 修复版演示")
    print("=" * 70)
    
    demo_1()
    demo_2()
    
    print("\\n" + "=" * 70)
    print("  演示完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
'''
    
    # 保存脚本
    script_path = os.path.join(os.path.dirname(__file__), "demo_fixed.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"✓ 已创建修复脚本: {script_path}")
    print(f"  使用方法: python debug/demo_fixed.py")
    return script_path


def main():
    """主函数"""
    print("环境诊断和修复工具")
    print("=" * 70)
    
    # 检查 API Key
    api_ok = check_and_fix_api_key()
    
    # 检查模块
    module_ok = check_and_fix_module()
    
    # 如果模块有问题，尝试自动修复
    if not module_ok:
        module_ok = fix_module_import()
    
    # 创建修复后的脚本
    script_path = create_fixed_demo_script()
    
    print("\n" + "=" * 70)
    print("诊断结果")
    print("=" * 70)
    print(f"API_KEY: {'✓ 正常' if api_ok else '✗ 需要设置'}")
    print(f"模块导入: {'✓ 正常' if module_ok else '✗ 需要修复'}")
    
    print("\n" + "=" * 70)
    print("下一步操作")
    print("=" * 70)
    
    if not api_ok:
        print("\n1. 设置 API_KEY（选择一种方式）：")
        print("   PowerShell: $env:KIMI_API_KEY='your_key'")
        print("   CMD: set KIMI_API_KEY=your_key")
    
    if not module_ok:
        print("\n2. 安装包：")
        print("   pip install -e .")
    
    print(f"\n3. 运行修复后的脚本：")
    print(f"   python debug/demo_fixed.py")


if __name__ == "__main__":
    main()
