# flood_decision_agent

面向防汛调度的智能决策科研原型工程。项目围绕"决策链生成Agent → 节点调度Agent → 单元任务执行Agent → 决策融合模块"组织代码，当前阶段已实现完整的端到端链路，支持真实LLM API调用和可视化展示。

## 项目进展

### 已实现功能

#### 1. 核心Agent架构
- **DecisionChainGeneratorAgent**: 决策链生成Agent，基于LLM进行意图解析和任务分解
- **NodeSchedulerAgent**: 节点调度Agent，负责任务图的调度和执行
- **UnitTaskExecutionAgent**: 单元任务执行Agent，支持动态工具选择和执行
- **SummarizerAgent**: 总结智能体，对执行过程和结果进行智能总结

#### 2. 意图解析与任务分解
- 使用Kimi LLM进行自然语言意图识别
- 支持流式输出，实时显示AI思考过程
- 基于prefix mode引导JSON格式输出
- 支持10+种业务类型（洪水预警、水库调度、数据查询等）

#### 3. 工具系统
- **专用工具**: 数据采集、预测预报、计算分析、决策生成等（10种）
- **通用查询工具**: 使用LLM直接回答任意问题，不局限于水利领域
- 工具注册中心支持动态注册和查询
- 支持工具执行策略：single、parallel、fallback、ensemble

#### 4. 可视化展示
- PowerShell终端可视化，支持ANSI颜色
- 显示Agent调用链和数据流
- 展示决策链任务列表和执行状态
- 实时显示任务执行进度（打勾标记）

#### 5. 流式输出
- 意图解析流式输出
- 通用查询流式输出
- 执行总结流式输出

## 环境配置

### 1. 一键安装

进入项目根目录，运行PowerShell脚本：

```powershell
.\scripts\setup_env.ps1
```

### 2. 配置API Key

需要在系统环境变量中配置Kimi API Key：

```powershell
setx KIMI_API_KEY "your_api_key"
```

重新打开PowerShell终端使配置生效。

## 演示方式

### 快速运行示例

```powershell
# 示例1: 洪水预警分析
python .\examples\run_visualized_demo.py 1

# 示例2: 水库联合调度
python .\examples\run_visualized_demo.py 2

# 示例3: 数据查询
python .\examples\run_visualized_demo.py 3

# 示例4: 洪水风险评估
python .\examples\run_visualized_demo.py 4

# 示例5: 应急响应决策
python .\examples\run_visualized_demo.py 5

# 示例6: 自定义问题（通用查询）
python .\examples\run_visualized_demo.py 6 "河海大学怎么样？"

# 运行所有预设示例
python .\examples\run_visualized_demo.py all
```

### 演示效果

运行后会展示：
1. **意图解析**: AI实时分析用户问题，流式输出JSON格式的意图识别结果
2. **任务列表**: 展示生成的决策链任务列表
3. **执行过程**: 实时显示每个任务的执行状态和Agent调用链
4. **AI回答**: 对于通用问题，流式显示LLM的回答
5. **执行总结**: AI对整个过程和结果进行智能总结

### 示例输出

```
======================================================================
[AI 思考中...]{
    "task_type": "flood_warning",
    "goal": {...},
    "confidence": 0.9
}

┌──────────────────────────────────────────────────────────┐
│ 决策链任务列表                                                  │
└──────────────────────────────────────────────────────────┘
  ○ task 1 : 数据采集
  ○ task 2 : 预测预报 [依赖: task_1]
  ...

◑ 数据采集 ▶ 执行中
✓ 数据采集 ✓ 已完成 (0ms)
...

======================================================================
[AI 正在生成执行总结...]
======================================================================

**任务执行概况：**
...
```

## 目录结构

- `src/`: 核心Python包与可复用模块
  - `agents/`: Agent实现（决策链生成、节点调度、任务执行、总结）
  - `core/`: 核心模块（消息、数据池、任务图、任务类型）
  - `tools/`: 工具系统（执行工具、LLM工具、工具注册表）
  - `visualization/`: 可视化模块
  - `app/`: 应用层（Pipeline集成）
- `data/`: 数据样例与数据约定（非Python包）
- `experiments/`: 实验脚本与可复现实验配置
- `notebooks/`: 实验报告与分析Notebook
- `tests/`: 单元测试（Python包）
- `docs/`: 架构与设计文档
  - `tools.md`: 工具定义和使用文档
- `examples/`: 端到端最小可运行示例
- `scripts/`: 环境与开发辅助脚本（PowerShell）
- `logs/`: 运行日志输出目录
- `debug/`: 多层调试场景目录与调试主入口

## 技术特点

1. **Agent架构**: 基于消息传递的Agent协作机制
2. **流式输出**: 所有LLM调用均支持流式传输，提升用户体验
3. **工具系统**: 支持专用工具和通用工具，灵活应对不同场景
4. **可视化**: 终端实时展示执行流程和Agent调用链
5. **类型安全**: 统一的任务类型定义，避免类型不匹配问题

## 开发规范

- 代码风格: PEP8
- 提交前必须通过pre-commit（black/isort/flake8）
- 单元测试: pytest，覆盖率目标≥80%
- 所有入口脚本必须检查KIMI_API_KEY环境变量

## 注意事项

- 若未配置API Key，程序启动时会直接输出：`需要kimi_api_key`
- 通用查询工具会调用真实LLM API，可能产生费用
- 流式输出需要稳定的网络连接
