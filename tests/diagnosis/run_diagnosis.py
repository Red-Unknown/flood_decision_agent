"""
异步调用机制与阻塞问题全面诊断主脚本
整合静态分析、性能测试和端到端诊断
"""

import asyncio
import subprocess
import sys
import os
import time
import io
from pathlib import Path
from datetime import datetime

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 使用简单字符替代Unicode符号
CHECK = "[OK]"
CROSS = "[ERR]"
WARN = "[WARN]"


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_section(title: str):
    """打印章节标题"""
    print(f"\n## {title}")
    print("-" * 40)


def safe_print(msg: str):
    """安全打印，处理编码问题"""
    try:
        print(msg)
    except UnicodeEncodeError:
        # 移除或替换无法编码的字符
        safe_msg = msg.encode('ascii', 'replace').decode('ascii')
        print(safe_msg)


def run_static_analysis() -> bool:
    """运行静态代码分析"""
    print_section("阶段一：静态代码分析")

    try:
        # 运行静态分析器
        result = subprocess.run(
            [sys.executable, "diagnosis/async_analyzer.py"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            print(f"{CHECK} 静态分析完成")
            output = result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
            safe_print(output)
            return True
        else:
            print(f"{CROSS} 静态分析失败: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"{CROSS} 静态分析超时")
        return False
    except Exception as e:
        print(f"{CROSS} 静态分析出错: {e}")
        return False


def check_backend_running() -> bool:
    """检查后端服务是否运行"""
    print_section("检查后端服务状态")

    import websockets

    async def test_connection():
        try:
            async with websockets.connect("ws://localhost:8000/ws/chat", timeout=5):
                return True
        except:
            return False

    try:
        is_running = asyncio.run(test_connection())
        if is_running:
            print(f"{CHECK} 后端服务正在运行")
            return True
        else:
            print(f"{CROSS} 后端服务未运行")
            return False
    except Exception as e:
        print(f"{CROSS} 检查后端服务时出错: {e}")
        return False


def start_backend_service() -> subprocess.Popen:
    """启动后端服务"""
    print_section("启动后端服务")

    # 检查API Key
    if not os.environ.get("KIMI_API_KEY"):
        print(f"{WARN} 警告: KIMI_API_KEY 环境变量未设置")
        print("  尝试从 .env 文件加载...")

        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                        print(f"  已加载: {key}")

    # 启动后端服务
    try:
        # 使用 CREATE_NEW_PROCESS_GROUP 标志以便在 Windows 上正确终止进程
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        
        process = subprocess.Popen(
            [sys.executable, "-m", "web.backend.main"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=os.environ.copy(),
            creationflags=creationflags
        )

        # 等待服务启动
        print("  等待服务启动...")
        time.sleep(5)

        # 检查是否成功启动
        if process.poll() is None:
            print(f"{CHECK} 后端服务启动成功")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"{CROSS} 后端服务启动失败")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None

    except Exception as e:
        print(f"{CROSS} 启动后端服务时出错: {e}")
        return None


def run_performance_tests() -> bool:
    """运行性能测试"""
    print_section("阶段二：性能测试")

    try:
        result = subprocess.run(
            [sys.executable, "diagnosis/performance_tester.py"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout
        safe_print(output)

        if result.returncode == 0:
            print(f"{CHECK} 性能测试通过")
            return True
        else:
            print(f"{WARN} 性能测试发现问题: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"{CROSS} 性能测试超时")
        return False
    except Exception as e:
        print(f"{CROSS} 性能测试出错: {e}")
        return False


def run_e2e_diagnosis() -> bool:
    """运行端到端诊断"""
    print_section("阶段三：端到端诊断")

    try:
        result = subprocess.run(
            [sys.executable, "diagnosis/e2e_diagnosis.py"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout
        safe_print(output)

        if result.returncode == 0:
            print(f"{CHECK} 端到端诊断通过")
            return True
        else:
            print(f"{WARN} 端到端诊断发现问题")
            return False

    except subprocess.TimeoutExpired:
        print(f"{CROSS} 端到端诊断超时")
        return False
    except Exception as e:
        print(f"{CROSS} 端到端诊断出错: {e}")
        return False


def generate_comprehensive_report():
    """生成综合诊断报告"""
    print_section("生成综合诊断报告")

    diagnosis_dir = Path(__file__).parent
    project_dir = diagnosis_dir.parent

    # 收集所有报告
    reports = {
        "static_analysis": diagnosis_dir / "static_analysis_report.md",
        "performance": diagnosis_dir / "performance_test_report.md",
        "e2e": diagnosis_dir / "e2e_diagnosis_report.md"
    }

    # 生成综合报告
    comprehensive_report = []
    comprehensive_report.append("=" * 80)
    comprehensive_report.append("异步调用机制与阻塞问题全面诊断报告")
    comprehensive_report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    comprehensive_report.append("=" * 80)
    comprehensive_report.append("")

    # 执行摘要
    comprehensive_report.append("## 执行摘要")
    comprehensive_report.append("")

    # 读取各报告并汇总
    for report_name, report_path in reports.items():
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取关键信息
            if "静态分析" in content:
                comprehensive_report.append("### 静态代码分析")
                # 提取统计信息
                for line in content.split('\n'):
                    if '分析文件数' in line or '异步函数数' in line or '潜在阻塞调用' in line:
                        comprehensive_report.append(line.strip())
                comprehensive_report.append("")

            elif "性能测试" in content:
                comprehensive_report.append("### 性能测试")
                for line in content.split('\n'):
                    if '总测试数' in line or '通过' in line or '失败' in line:
                        comprehensive_report.append(line.strip())
                comprehensive_report.append("")

            elif "端到端诊断" in content:
                comprehensive_report.append("### 端到端诊断")
                for line in content.split('\n'):
                    if '总测试数' in line or '阻塞检测' in line:
                        comprehensive_report.append(line.strip())
                comprehensive_report.append("")

    # 关键发现
    comprehensive_report.append("## 关键发现")
    comprehensive_report.append("")

    # 检查是否有阻塞问题
    blocking_found = False
    for report_path in reports.values():
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if '阻塞' in content and '未检测' not in content:
                blocking_found = True
                break

    if blocking_found:
        comprehensive_report.append("⚠ 检测到潜在的阻塞问题，详见各专项报告")
    else:
        comprehensive_report.append("✓ 未检测到明显的阻塞问题")

    comprehensive_report.append("")

    # 报告位置
    comprehensive_report.append("## 详细报告")
    comprehensive_report.append("")
    for report_name, report_path in reports.items():
        if report_path.exists():
            comprehensive_report.append(f"- {report_name}: {report_path}")

    comprehensive_report.append("")
    comprehensive_report.append("=" * 80)

    # 保存综合报告
    comprehensive_path = diagnosis_dir / "comprehensive_diagnosis_report.md"
    with open(comprehensive_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(comprehensive_report))

    print(f"{CHECK} 综合报告已保存到: {comprehensive_path}")

    return comprehensive_path


def main():
    """主函数"""
    print_header("异步调用机制与阻塞问题全面诊断")

    start_time = time.time()
    backend_process = None
    results = {
        "static_analysis": False,
        "backend_started": False,
        "performance_test": False,
        "e2e_diagnosis": False
    }

    try:
        # 阶段一：静态代码分析
        results["static_analysis"] = run_static_analysis()

        # 检查后端服务
        if not check_backend_running():
            # 尝试启动后端服务
            backend_process = start_backend_service()
            if backend_process:
                results["backend_started"] = True
                # 再次检查
                time.sleep(3)
                if not check_backend_running():
                    print("✗ 后端服务未能正常启动，跳过后续测试")
                    return 1
            else:
                print("✗ 无法启动后端服务，跳过后续测试")
                return 1
        else:
            results["backend_started"] = True

        # 阶段二：性能测试
        results["performance_test"] = run_performance_tests()

        # 阶段三：端到端诊断
        results["e2e_diagnosis"] = run_e2e_diagnosis()

        # 生成综合报告
        report_path = generate_comprehensive_report()

        # 打印总结
        print_header("诊断完成")
        print(f"\n总耗时: {time.time() - start_time:.2f} 秒")
        print("\n各阶段结果:")
        for stage, success in results.items():
            status = f"{CHECK} 通过" if success else f"{CROSS} 失败"
            print(f"  {stage}: {status}")

        print(f"\n详细报告: {report_path}")

        # 返回退出码
        return 0 if all(results.values()) else 1

    except KeyboardInterrupt:
        print("\n\n诊断被用户中断")
        return 130

    finally:
        # 关闭后端服务（如果是我们启动的）
        if backend_process and backend_process.poll() is None:
            print("\n正在关闭后端服务...")
            if sys.platform == 'win32':
                backend_process.send_signal(subprocess.signal.CTRL_BREAK_EVENT)
            else:
                backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
