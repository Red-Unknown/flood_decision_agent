"""终端可视化渲染器.

使用 PowerShell/终端 ANSI 颜色代码和 Unicode 字符实现美观的终端展示。
支持任务列表、执行状态打勾、Agent 调用链展示。
"""

from __future__ import annotations

import sys
from typing import Dict, List, Optional

from flood_decision_agent.visualization.base import BaseVisualizer
from flood_decision_agent.visualization.models import (
    AgentCallInfo,
    DataFlowInfo,
    ExecutionEvent,
    ExecutionSummary,
    TaskInfo,
    TaskStatus,
)


class TerminalColors:
    """终端颜色代码.

    使用 ANSI 转义序列实现颜色输出。
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 亮前景色
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class TerminalVisualizer(BaseVisualizer):
    """终端可视化器.

    在 PowerShell/终端中展示 Agent 调用链、任务执行状态和数据流。
    使用 ANSI 颜色代码和 Unicode 字符美化输出。

    Attributes:
        use_colors: 是否使用颜色
        use_unicode: 是否使用 Unicode 字符
        show_timestamps: 是否显示时间戳
        indent_size: 缩进大小
    """

    # 状态图标
    ICONS = {
        "pending": "○",  # 未开始
        "ready": "◐",  # 准备就绪
        "running": "◑",  # 执行中
        "completed": "✓",  # 已完成
        "failed": "✗",  # 失败
        "arrow": "→",
        "bullet": "•",
        "diamond": "◆",
        "box_horizontal": "─",
        "box_vertical": "│",
        "box_top_left": "┌",
        "box_top_right": "┐",
        "box_bottom_left": "└",
        "box_bottom_right": "┘",
        "box_cross": "┼",
        "box_t_right": "├",
        "box_t_left": "┤",
    }

    def __init__(
        self,
        enabled: bool = True,
        use_colors: bool = True,
        use_unicode: bool = True,
        show_timestamps: bool = False,
        indent_size: int = 2,
        silent: bool = False,
        stream_callback=None,
    ):
        """初始化终端可视化器.

        Args:
            enabled: 是否启用可视化
            use_colors: 是否使用颜色，默认 True
            use_unicode: 是否使用 Unicode 字符，默认 True
            show_timestamps: 是否显示时间戳，默认 False
            indent_size: 缩进大小，默认 2
            silent: 是否静默模式（不输出到控制台），默认 False
            stream_callback: 流式输出回调函数，用于将输出转发到前端
        """
        super().__init__(enabled)
        self.use_colors = use_colors and self._supports_colors()
        self.use_unicode = use_unicode
        self.show_timestamps = show_timestamps
        self.indent_size = indent_size
        self._line_count = 0  # 已输出行数，用于动态刷新
        self.silent = silent
        self.stream_callback = stream_callback

    def _supports_colors(self) -> bool:
        """检测终端是否支持颜色.

        Returns:
            是否支持颜色
        """
        # Windows PowerShell 和大多数现代终端都支持 ANSI 颜色
        if sys.platform == "win32":
            return True
        # 检查是否连接到终端
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def _color(self, text: str, *colors: str) -> str:
        """为文本添加颜色.

        Args:
            text: 原文本
            *colors: 颜色代码

        Returns:
            带颜色的文本
        """
        if not self.use_colors:
            return text
        color_codes = "".join(colors)
        return f"{color_codes}{text}{TerminalColors.RESET}"

    def _icon(self, name: str) -> str:
        """获取图标字符.

        Args:
            name: 图标名称

        Returns:
            图标字符
        """
        if not self.use_unicode:
            # ASCII 回退
            ascii_map = {
                "pending": "[ ]",
                "ready": "[~]",
                "running": "[*]",
                "completed": "[x]",
                "failed": "[!]",
                "arrow": "->",
                "bullet": "*",
                "diamond": "*",
                "box_horizontal": "-",
                "box_vertical": "|",
                "box_top_left": "+",
                "box_top_right": "+",
                "box_bottom_left": "+",
                "box_bottom_right": "+",
                "box_cross": "+",
                "box_t_right": "+",
                "box_t_left": "+",
            }
            return ascii_map.get(name, "")
        return self.ICONS.get(name, "")

    def _indent(self, level: int = 1) -> str:
        """生成缩进字符串.

        Args:
            level: 缩进级别

        Returns:
            缩进字符串
        """
        return " " * (self.indent_size * level)

    def _print(self, text: str = "", end: str = "\n", flush: bool = False) -> None:
        """打印文本.

        Args:
            text: 要打印的文本
            end: 行尾字符
            flush: 是否立即刷新
        """
        # 静默模式下不输出到控制台，但如果有回调则转发
        if self.silent:
            if self.stream_callback and text:
                self.stream_callback(text)
            return

        print(text, end=end, flush=flush)
        if end == "\n":
            self._line_count += 1

    def _print_header(self, title: str) -> None:
        """打印标题头.

        Args:
            title: 标题文本
        """
        width = 60
        h_line = self._icon("box_horizontal") * (width - 2)

        self._print()
        self._print(
            self._color(
                f"{self._icon('box_top_left')}{h_line}{self._icon('box_top_right')}",
                TerminalColors.CYAN,
            )
        )
        self._print(
            self._color(
                f"{self._icon('box_vertical')} {title:<{width-3}}{self._icon('box_vertical')}",
                TerminalColors.CYAN,
            )
        )
        self._print(
            self._color(
                f"{self._icon('box_bottom_left')}{h_line}{self._icon('box_bottom_right')}",
                TerminalColors.CYAN,
            )
        )

    def _print_separator(self) -> None:
        """打印分隔线."""
        sep = self._icon("box_horizontal") * 60
        self._print(self._color(sep, TerminalColors.DIM))

    def _status_icon(self, status: TaskStatus) -> str:
        """获取状态对应的图标.

        Args:
            status: 任务状态

        Returns:
            状态图标
        """
        icon_map = {
            TaskStatus.PENDING: ("pending", TerminalColors.DIM),
            TaskStatus.READY: ("ready", TerminalColors.YELLOW),
            TaskStatus.RUNNING: ("running", TerminalColors.BLUE),
            TaskStatus.COMPLETED: ("completed", TerminalColors.GREEN),
            TaskStatus.FAILED: ("failed", TerminalColors.RED),
        }
        icon_name, color = icon_map.get(status, ("pending", TerminalColors.DIM))
        icon = self._icon(icon_name)
        return self._color(icon, color, TerminalColors.BOLD)

    def _status_text(self, status: TaskStatus) -> str:
        """获取状态对应的文本.

        Args:
            status: 任务状态

        Returns:
            状态文本
        """
        text_map = {
            TaskStatus.PENDING: ("等待中", TerminalColors.DIM),
            TaskStatus.READY: ("就绪", TerminalColors.YELLOW),
            TaskStatus.RUNNING: ("执行中", TerminalColors.BLUE),
            TaskStatus.COMPLETED: ("已完成", TerminalColors.GREEN),
            TaskStatus.FAILED: ("失败", TerminalColors.RED),
        }
        text, color = text_map.get(status, ("未知", TerminalColors.DIM))
        return self._color(text, color)

    def _render_event(self, event: ExecutionEvent) -> None:
        """渲染事件.

        Args:
            event: 执行事件
        """
        # 基类已实现主要逻辑，这里可以添加额外的终端特定处理
        pass

    def _render_pipeline_start(self, context: Optional[Dict]) -> None:
        """渲染流程开始.

        Args:
            context: 上下文信息
        """
        self._print_header("Agent 执行流程")

        if context:
            self._print(self._color("上下文信息:", TerminalColors.BOLD))
            for key, value in context.items():
                self._print(f"{self._indent()}{self._icon('bullet')} {key}: {value}")
            self._print()

    def _render_task_list(self, task_infos: List[TaskInfo]) -> None:
        """渲染任务列表.

        格式示例：
        o task 1 : 检查代码
        o task 2 : 修改代码

        Args:
            task_infos: 任务信息列表
        """
        self._print_header("决策链任务列表")

        for i, task_info in enumerate(task_infos, 1):
            icon = self._status_icon(task_info.status)
            task_name = task_info.task_name

            # 构建任务行
            line = f"{self._indent()}{icon} task {i} : {task_name}"

            # 如果有依赖，显示依赖信息
            if task_info.dependencies:
                deps_str = ", ".join(task_info.dependencies)
                line += self._color(f" [依赖: {deps_str}]", TerminalColors.DIM)

            self._print(line)

        self._print()
        self._print(
            self._color(
                f"共 {len(task_infos)} 个任务，准备执行...",
                TerminalColors.BRIGHT_CYAN,
            )
        )
        self._print()

    def _render_node_started(self, node_id: str, agent_id: str, task_info: Optional[TaskInfo]) -> None:
        """渲染节点开始.

        Args:
            node_id: 节点ID
            agent_id: 执行 Agent ID
            task_info: 任务信息
        """
        if task_info:
            icon = self._status_icon(TaskStatus.RUNNING)
            status_text = self._status_text(TaskStatus.RUNNING)
            line = f"{icon} {task_info.task_name} {self._color('▶', TerminalColors.BLUE)} {status_text}"
            self._print(line, end=" ", flush=True)

    def _render_node_completed(
        self, node_id: str, agent_id: str, duration_ms: float, task_info: Optional[TaskInfo]
    ) -> None:
        """渲染节点完成（打勾）.

        Args:
            node_id: 节点ID
            agent_id: 执行 Agent ID
            duration_ms: 执行耗时（毫秒）
            task_info: 任务信息
        """
        # 清除当前行并重新打印
        print("\r", end="", flush=True)

        if task_info:
            icon = self._status_icon(TaskStatus.COMPLETED)
            status_text = self._status_text(TaskStatus.COMPLETED)

            # 格式化耗时
            if duration_ms < 1000:
                duration_str = f"{duration_ms:.0f}ms"
            else:
                duration_str = f"{duration_ms / 1000:.2f}s"

            line = f"{icon} {task_info.task_name} {self._color('✓', TerminalColors.GREEN)} {status_text} ({duration_str})"
            self._print(line)

    def _render_node_failed(
        self, node_id: str, agent_id: str, error_message: str, task_info: Optional[TaskInfo]
    ) -> None:
        """渲染节点失败.

        Args:
            node_id: 节点ID
            agent_id: 执行 Agent ID
            error_message: 错误信息
            task_info: 任务信息
        """
        # 清除当前行并重新打印
        print("\r", end="", flush=True)

        if task_info:
            icon = self._status_icon(TaskStatus.FAILED)
            status_text = self._status_text(TaskStatus.FAILED)
            line = f"{icon} {task_info.task_name} {self._color('✗', TerminalColors.RED)} {status_text}"
            self._print(line)

            # 显示错误信息
            error_line = f"{self._indent()}  {self._color('错误:', TerminalColors.RED)} {error_message}"
            self._print(error_line)

    def _render_agent_call(self, agent_call: AgentCallInfo) -> None:
        """渲染 Agent 调用.

        Args:
            agent_call: Agent 调用信息
        """
        arrow = self._color(self._icon("arrow"), TerminalColors.CYAN)
        caller = self._color(agent_call.caller_agent, TerminalColors.YELLOW)
        callee = self._color(agent_call.callee_agent, TerminalColors.YELLOW)

        line = f"{self._indent()}{self._icon('diamond')} {caller} {arrow} {callee}"

        if agent_call.input_summary:
            line += f" {self._color(f'({agent_call.input_summary})', TerminalColors.DIM)}"

        self._print(line)

    def _render_data_flow(self, data_flow: DataFlowInfo) -> None:
        """渲染数据流.

        Args:
            data_flow: 数据流信息
        """
        arrow = self._color(self._icon("arrow"), TerminalColors.CYAN)
        source = self._color(data_flow.source_node, TerminalColors.GREEN)
        target = self._color(data_flow.target_node, TerminalColors.GREEN)
        keys = self._color(
            f"[{', '.join(data_flow.data_keys)}]", TerminalColors.DIM
        )

        line = f"{self._indent(2)}{self._icon('bullet')} 数据流: {source} {arrow} {target} {keys}"
        self._print(line)

    def _render_pipeline_completed(self, success: bool, summary: ExecutionSummary) -> None:
        """渲染流程完成.

        Args:
            success: 是否成功完成
            summary: 执行汇总
        """
        self._print_separator()

        # 状态图标和文本
        if success and summary.failed_tasks == 0:
            status_icon = self._color("✓", TerminalColors.GREEN, TerminalColors.BOLD)
            status_text = self._color("执行成功", TerminalColors.GREEN, TerminalColors.BOLD)
        elif summary.completed_tasks > 0:
            status_icon = self._color("⚠", TerminalColors.YELLOW, TerminalColors.BOLD)
            status_text = self._color("部分成功", TerminalColors.YELLOW, TerminalColors.BOLD)
        else:
            status_icon = self._color("✗", TerminalColors.RED, TerminalColors.BOLD)
            status_text = self._color("执行失败", TerminalColors.RED, TerminalColors.BOLD)

        self._print(f"{status_icon} {status_text}")

        # 统计信息
        self._print(self._color("执行统计:", TerminalColors.BOLD))
        self._print(
            f"{self._indent()}{self._icon('bullet')} 总任务数: {summary.total_tasks}"
        )
        self._print(
            f"{self._indent()}{self._icon('bullet')} 成功: {self._color(str(summary.completed_tasks), TerminalColors.GREEN)}"
        )
        self._print(
            f"{self._indent()}{self._icon('bullet')} 失败: {self._color(str(summary.failed_tasks), TerminalColors.RED if summary.failed_tasks > 0 else TerminalColors.DIM)}"
        )

        # 总耗时
        if summary.total_duration_ms < 1000:
            duration_str = f"{summary.total_duration_ms:.0f}ms"
        else:
            duration_str = f"{summary.total_duration_ms / 1000:.2f}s"
        self._print(
            f"{self._indent()}{self._icon('bullet')} 总耗时: {self._color(duration_str, TerminalColors.CYAN)}"
        )

        self._print()

    def print_agent_chain(self, agent_calls: List[AgentCallInfo]) -> None:
        """打印 Agent 调用链（独立方法，供外部调用）.

        Args:
            agent_calls: Agent 调用列表
        """
        self._print_header("Agent 调用链")

        if not agent_calls:
            self._print(self._color("暂无 Agent 调用记录", TerminalColors.DIM))
            return

        for i, call in enumerate(agent_calls, 1):
            arrow = self._color(self._icon("arrow"), TerminalColors.CYAN)
            caller = self._color(call.caller_agent, TerminalColors.YELLOW)
            callee = self._color(call.callee_agent, TerminalColors.YELLOW)

            self._print(f"{self._indent()}{i}. {caller} {arrow} {callee}")

            if call.input_summary:
                self._print(
                    f"{self._indent(2)}{self._color('输入:', TerminalColors.DIM)} {call.input_summary}"
                )
            if call.output_summary:
                self._print(
                    f"{self._indent(2)}{self._color('输出:', TerminalColors.DIM)} {call.output_summary}"
                )

        self._print()

    def print_task_summary(self, task_infos: List[TaskInfo]) -> None:
        """打印任务执行汇总（独立方法，供外部调用）.

        Args:
            task_infos: 任务信息列表
        """
        self._print_header("任务执行汇总")

        if not task_infos:
            self._print(self._color("暂无任务记录", TerminalColors.DIM))
            return

        # 表头
        header = f"{'序号':<6}{'状态':<10}{'任务名称':<30}{'耗时':<12}"
        self._print(self._color(header, TerminalColors.BOLD))
        self._print(self._color("-" * 60, TerminalColors.DIM))

        # 任务列表
        for i, task in enumerate(task_infos, 1):
            status_icon = self._status_icon(task.status)
            status_text = self._status_text(task.status)

            if task.duration_ms:
                if task.duration_ms < 1000:
                    duration_str = f"{task.duration_ms:.0f}ms"
                else:
                    duration_str = f"{task.duration_ms / 1000:.2f}s"
            else:
                duration_str = "-"

            # 截断任务名称
            task_name = task.task_name[:28] if len(task.task_name) > 28 else task.task_name

            line = f"{i:<6}{status_icon} {status_text:<8}{task_name:<30}{duration_str:<12}"
            self._print(line)

        self._print()
