# 可视化模块 (Visualization)

Agent 调用链、数据流和决策过程的展示模块。

## 功能特性

- **任务列表展示**: TaskGraph 生成后自动列出所有任务
- **实时状态更新**: NodeSchedulerAgent 执行时实时显示状态变化
- **执行状态打勾**: 任务完成后显示 ✓ 标记
- **Agent 调用链**: 展示 Agent 之间的调用关系
- **执行汇总**: 统计任务数、成功率、耗时等信息
- **可扩展架构**: 支持终端、Web、桌面应用等多种渲染后端

## 快速开始

### 基础使用

```python
from flood_decision_agent.app import run_visualized_pipeline

# 运行可视化 Pipeline
result = run_visualized_pipeline(
    task_request={
        "type": "flood_warning",
        "params": {"station": "test_station"},
    },
    enable_visualization=True,
)
```

### 自定义可视化器

```python
from flood_decision_agent.visualization import TerminalVisualizer

# 创建自定义配置的可视化器
visualizer = TerminalVisualizer(
    enabled=True,
    use_colors=True,
    use_unicode=True,
    indent_size=2,
)

result = run_visualized_pipeline(
    task_request={"type": "flood_warning", "params": {}},
    visualizer=visualizer,
)
```

### 注册事件处理器

```python
from flood_decision_agent.visualization.models import EventType

def on_task_completed(event):
    if event.task_info:
        print(f"任务完成: {event.task_info.task_name}")

visualizer.register_event_handler(EventType.NODE_COMPLETED, on_task_completed)
```

## 模块结构

```
visualization/
├── __init__.py          # 模块入口
├── base.py              # 可视化基类 BaseVisualizer
├── models.py            # 数据模型 (TaskInfo, ExecutionEvent 等)
├── terminal.py          # 终端可视化器 TerminalVisualizer
└── README.md            # 本文档
```

## 扩展新渲染器

继承 `BaseVisualizer` 实现新的渲染后端：

```python
from flood_decision_agent.visualization.base import BaseVisualizer
from flood_decision_agent.visualization.models import ExecutionEvent

class WebVisualizer(BaseVisualizer):
    def _render_task_list(self, task_infos):
        # 实现 Web 端任务列表展示
        pass

    def _render_node_completed(self, node_id, agent_id, duration_ms, task_info):
        # 实现 Web 端节点完成展示
        pass

    # ... 实现其他抽象方法
```

## 显示效果

### 任务列表

```
┌─────────────────────────────────────────────────────────────┐
│                    决策链任务列表                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ○ task 1 : 数据查询 (node_1)                              │
│   ○ task 2 : 风险评估 (node_2) [依赖: node_1]               │
│   ○ task 3 : 洪水预警 (node_3) [依赖: node_1, node_2]       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 执行状态

```
◑ 数据查询 (node_1) ▶ 执行中   →  执行中显示为 ◑
✓ 数据查询 (node_1) ✓ 已完成 (120ms)   →  完成后显示为 ✓
```

### Agent 调用链

```
◆ Pipeline → DecisionChainGeneratorAgent
◆ Pipeline → NodeSchedulerAgent
◆ NodeSchedulerAgent → UnitTaskExecutionAgent
```

## 运行演示

```bash
# 基础演示
python examples/demo_visualization.py

# 所有演示
python examples/demo_visualization.py all

# 查看帮助
python examples/demo_visualization.py --help
```
