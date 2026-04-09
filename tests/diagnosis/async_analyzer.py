"""
异步代码静态分析器
用于识别所有异步函数、await表达式和潜在的阻塞调用
"""

import ast
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from collections import defaultdict


@dataclass
class AsyncFunctionInfo:
    """异步函数信息"""
    name: str
    file_path: str
    line_number: int
    has_await: bool = False
    await_count: int = 0
    blocking_calls: List[Dict] = field(default_factory=list)
    calls_sync_functions: List[str] = field(default_factory=list)


@dataclass
class BlockingCallInfo:
    """阻塞调用信息"""
    call_type: str
    file_path: str
    line_number: int
    code_snippet: str
    severity: str  # 'high', 'medium', 'low'
    suggestion: str


class AsyncCodeAnalyzer(ast.NodeVisitor):
    """异步代码分析器"""

    # 已知的阻塞调用模式
    BLOCKING_PATTERNS = {
        'high': [
            # 文件I/O
            ('open', '使用 aiofiles 替代'),
            ('read', '使用异步读取方法'),
            ('write', '使用异步写入方法'),
            # 时间睡眠
            ('time.sleep', '使用 asyncio.sleep'),
            # 子进程
            ('subprocess.call', '使用 asyncio.create_subprocess_exec'),
            ('subprocess.run', '使用 asyncio.create_subprocess_exec'),
            ('os.system', '使用 asyncio.create_subprocess_exec'),
            # 同步HTTP
            ('requests.get', '使用 aiohttp'),
            ('requests.post', '使用 aiohttp'),
            ('urllib.request', '使用 aiohttp'),
        ],
        'medium': [
            # 数据库操作
            ('sqlite3', '使用 aiosqlite'),
            ('pymongo', '使用 motor'),
            ('redis', '使用 aioredis'),
            # 锁操作
            ('threading.Lock', '使用 asyncio.Lock'),
            ('threading.Semaphore', '使用 asyncio.Semaphore'),
        ],
        'low': [
            # 计算密集型操作
            ('json.dumps', '大型数据时使用异步处理'),
            ('json.loads', '大型数据时使用异步处理'),
            ('pickle.dumps', '大型数据时使用异步处理'),
        ]
    }

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.async_functions: List[AsyncFunctionInfo] = []
        self.blocking_calls: List[BlockingCallInfo] = []
        self.current_function: Optional[AsyncFunctionInfo] = None
        self.sync_functions_in_async: List[Dict] = []

    def visit_AsyncFunctionDef(self, node):
        """访问异步函数定义"""
        func_info = AsyncFunctionInfo(
            name=node.name,
            file_path=self.file_path,
            line_number=node.lineno
        )
        self.async_functions.append(func_info)
        old_function = self.current_function
        self.current_function = func_info

        self.generic_visit(node)

        self.current_function = old_function

    def visit_Await(self, node):
        """访问 await 表达式"""
        if self.current_function:
            self.current_function.has_await = True
            self.current_function.await_count += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        """访问函数调用"""
        call_name = self._get_call_name(node)

        if call_name:
            # 检查是否是阻塞调用
            self._check_blocking_call(node, call_name)

            # 如果在异步函数中调用同步函数
            if self.current_function and not call_name.startswith('async'):
                # 检查是否是已知的同步调用
                if self._is_likely_sync_call(call_name):
                    self.current_function.calls_sync_functions.append(call_name)

        self.generic_visit(node)

    def _get_call_name(self, node) -> Optional[str]:
        """获取调用的函数名"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            value = node.func.value
            if isinstance(value, ast.Name):
                return f"{value.id}.{node.func.attr}"
            elif isinstance(value, ast.Attribute):
                return f"{self._get_attribute_chain(value)}.{node.func.attr}"
        return None

    def _get_attribute_chain(self, node) -> str:
        """获取属性链"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_attribute_chain(node.value)}.{node.attr}"
        return ""

    def _check_blocking_call(self, node, call_name: str):
        """检查是否是阻塞调用"""
        for severity, patterns in self.BLOCKING_PATTERNS.items():
            for pattern, suggestion in patterns:
                if pattern in call_name or call_name.endswith(pattern.split('.')[-1]):
                    # 获取代码片段
                    code_snippet = ast.unparse(node) if hasattr(ast, 'unparse') else call_name

                    blocking_info = BlockingCallInfo(
                        call_type=call_name,
                        file_path=self.file_path,
                        line_number=node.lineno,
                        code_snippet=code_snippet,
                        severity=severity,
                        suggestion=suggestion
                    )
                    self.blocking_calls.append(blocking_info)

                    if self.current_function:
                        self.current_function.blocking_calls.append({
                            'call': call_name,
                            'line': node.lineno,
                            'severity': severity
                        })
                    return

    def _is_likely_sync_call(self, call_name: str) -> bool:
        """判断是否是可能的同步调用"""
        sync_patterns = [
            'parse', 'generate', 'execute', 'process',
            'load', 'save', 'read', 'write',
            'compute', 'calculate', 'transform'
        ]
        return any(pattern in call_name.lower() for pattern in sync_patterns)


def analyze_project(project_path: str) -> Dict:
    """分析整个项目"""
    all_async_functions: List[AsyncFunctionInfo] = []
    all_blocking_calls: List[BlockingCallInfo] = []
    files_analyzed = 0
    errors = []

    # 遍历项目中的所有Python文件
    for root, dirs, files in os.walk(project_path):
        # 跳过某些目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'venv', 'node_modules']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if not content.strip():
                        continue

                    tree = ast.parse(content)
                    analyzer = AsyncCodeAnalyzer(relative_path)
                    analyzer.visit(tree)

                    all_async_functions.extend(analyzer.async_functions)
                    all_blocking_calls.extend(analyzer.blocking_calls)
                    files_analyzed += 1

                except SyntaxError as e:
                    errors.append(f"{relative_path}: Syntax error - {e}")
                except Exception as e:
                    errors.append(f"{relative_path}: Error - {e}")

    return {
        'async_functions': all_async_functions,
        'blocking_calls': all_blocking_calls,
        'files_analyzed': files_analyzed,
        'errors': errors
    }


def generate_report(results: Dict) -> str:
    """生成分析报告"""
    report = []
    report.append("=" * 80)
    report.append("异步代码静态分析报告")
    report.append("=" * 80)
    report.append("")

    # 统计信息
    report.append("## 统计信息")
    report.append(f"- 分析文件数: {results['files_analyzed']}")
    report.append(f"- 异步函数数: {len(results['async_functions'])}")
    report.append(f"- 潜在阻塞调用: {len(results['blocking_calls'])}")
    report.append(f"- 分析错误: {len(results['errors'])}")
    report.append("")

    # 异步函数列表
    report.append("## 异步函数列表")
    report.append("")

    # 按文件分组
    by_file = defaultdict(list)
    for func in results['async_functions']:
        by_file[func.file_path].append(func)

    for file_path, functions in sorted(by_file.items()):
        report.append(f"### {file_path}")
        for func in functions:
            await_info = f" (await: {func.await_count})" if func.has_await else " (无await)"
            report.append(f"  - Line {func.line_number}: `{func.name}`{await_info}")
            if func.blocking_calls:
                for call in func.blocking_calls:
                    report.append(f"    ⚠️  阻塞调用: {call['call']} (行 {call['line']}, {call['severity']})")
        report.append("")

    # 阻塞调用详情
    if results['blocking_calls']:
        report.append("## 潜在阻塞调用详情")
        report.append("")

        # 按严重程度分组
        by_severity = defaultdict(list)
        for call in results['blocking_calls']:
            by_severity[call.severity].append(call)

        for severity in ['high', 'medium', 'low']:
            if severity in by_severity:
                report.append(f"### {severity.upper()} 级别")
                for call in by_severity[severity]:
                    report.append(f"- **{call.call_type}**")
                    report.append(f"  - 位置: {call.file_path}:{call.line_number}")
                    report.append(f"  - 代码: `{call.code_snippet}`")
                    report.append(f"  - 建议: {call.suggestion}")
                    report.append("")

    # 错误列表
    if results['errors']:
        report.append("## 分析错误")
        report.append("")
        for error in results['errors'][:10]:  # 只显示前10个
            report.append(f"- {error}")
        if len(results['errors']) > 10:
            report.append(f"- ... 还有 {len(results['errors']) - 10} 个错误")
        report.append("")

    report.append("=" * 80)
    report.append("报告生成完成")
    report.append("=" * 80)

    return "\n".join(report)


if __name__ == "__main__":
    import sys
    import io

    # 设置UTF-8编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # 分析项目
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"正在分析项目: {project_path}")
    print("-" * 80)

    results = analyze_project(project_path)
    report = generate_report(results)

    # 保存报告
    report_path = os.path.join(project_path, "diagnosis", "static_analysis_report.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # 替换特殊字符以避免编码问题
    safe_report = report.replace('⚠️', '[WARN]').replace('✓', '[OK]').replace('✗', '[ERR]')
    print(safe_report)
    print(f"\n报告已保存到: {report_path}")
