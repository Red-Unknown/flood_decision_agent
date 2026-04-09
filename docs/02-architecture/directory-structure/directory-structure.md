# 项目目录结构说明

## 概述

本文档详细说明 `flood_decision_agent` 项目的目录结构设计，包括各目录的功能定义、文件存放规则及使用规范。

项目采用 **DDD（领域驱动设计）** 分层架构，结合 **Web 前后端分离** 和 **MCP 服务协议**，确保代码的可维护性和可扩展性。

## 目录结构总览

```
flood_decision_agent/
├── configs/                    # 集中式配置管理
├── src/flood_decision_agent/   # 核心业务代码
│   ├── domain/                 # 领域层 - 核心业务实体
│   ├── application/            # 应用层 - 业务逻辑编排
│   ├── infrastructure/         # 基础设施层
│   ├── mcp/                    # MCP 协议层
│   ├── agents/                 # 智能体层
│   ├── evaluation/             # 评估框架
│   ├── interfaces/             # 接口适配层
│   ├── shared/                 # 共享组件
│   ├── conversation/           # 对话管理
│   └── visualization/          # 可视化
├── web/                        # Web 应用
│   ├── backend/                # 后端服务
│   └── frontend/               # 前端应用
├── tests/                      # 测试目录
├── resources/                  # 资源文件
├── docs/                       # 文档
├── scripts/                    # 脚本工具
├── debug/                      # 调试工具
├── examples/                   # 示例代码
├── logs/                       # 日志文件
└── notebooks/                  # Jupyter notebooks
```

## 根目录文件说明

| 文件 | 用途 |
|------|------|
| `README.md` | 项目说明文档 |
| `requirements.txt` | Python 依赖列表 |
| `environment.yml` | Conda 环境配置 |
| `setup.py` | Python 包安装配置 |
| `pyproject.toml` | Python 项目配置文件 |
| `.gitignore` | Git 忽略规则 |
| `.flake8` | Flake8 代码规范配置 |

## 详细说明

### 1. configs/ - 集中式配置管理

存放所有配置文件，支持 YAML 和 JSON 格式。

| 目录/文件 | 用途 |
|------|------|
| `configs/app/` | 应用配置（default.yaml, development.yaml, production.yaml） |
| `configs/mcp/` | MCP 服务配置（servers.yaml, tools.yaml） |
| `configs/evaluation/` | 评估配置（metrics.yaml, scenarios.yaml） |
| `configs/.env.example` | 环境变量示例 |

**使用示例：**
```python
from flood_decision_agent.infrastructure import load_config

config = load_config('app', env='development')
```

### 2. src/flood_decision_agent/domain/ - 领域层

核心业务实体定义，采用 DDD（领域驱动设计）思想。

| 目录 | 用途 |
|------|------|
| `domain/entities/` | 领域实体（Decision, Task, Message, Conversation） |
| `domain/value_objects/` | 值对象（Priority, Status） |
| `domain/events/` | 领域事件（TaskCreatedEvent, TaskCompletedEvent） |

### 3. src/flood_decision_agent/application/ - 应用层

业务逻辑编排，负责用例的执行和协调。

| 目录 | 用途 |
|------|------|
| `application/services/` | 应用服务（DecisionService, ChatService） |
| `application/use_cases/` | 用例实现（GenerateDecisionChainUseCase） |
| `application/dto/` | 数据传输对象（Request, Response） |

### 4. src/flood_decision_agent/infrastructure/ - 基础设施层

技术实现细节，包括 LLM 客户端、数据持久化等。

| 目录/文件 | 用途 |
|------|------|
| `infrastructure/llm/` | LLM 客户端（KimiClient, LLMClient） |
| `infrastructure/persistence/` | 数据持久化（Repository 模式） |
| `infrastructure/config_loader.py` | 配置加载器 |

### 5. src/flood_decision_agent/mcp/ - MCP 协议层

Model Context Protocol 实现。

| 目录 | 用途 |
|------|------|
| `mcp/protocol/` | 协议定义（types, messages, constants） |
| `mcp/core/` | 核心组件（server, client, session, transport） |
| `mcp/servers/` | 服务器实现（filesystem, hydrology, document, hipims, rainfall, web_search, yolo_vision 等） |
| `mcp/clients/` | 客户端实现 |
| `mcp/tools/` | 工具定义和适配器 |
| `mcp/adapters/` | 工具适配器 |
| `mcp/log/` | MCP 日志系统 |
| `mcp/utils/` | MCP 工具函数 |
| `mcp/configs/` | MCP 配置文件 |

### 6. src/flood_decision_agent/agents/ - 智能体层

各类 Agent 的实现。

| 目录/文件 | 用途 |
|------|------|
| `agents/base/` | Agent 基类 |
| `agents/decision_chain/` | 决策链生成（generator, optimizer, decomposer 等） |
| `agents/node_scheduler/` | 节点调度 |
| `agents/task_executor/` | 任务执行（含 MCP 集成） |
| `agents/intent_parser/` | 意图解析 |
| `agents/prompts/` | Prompt 模板 |
| `agents/summarizer/` | 总结智能体 |

### 7. src/flood_decision_agent/evaluation/ - 评估框架

系统评估相关功能。

| 目录 | 用途 |
|------|------|
| `evaluation/core/` | 评估核心（evaluator, runner, registry） |
| `evaluation/metrics/` | 评估指标 |
| `evaluation/test_cases/` | 测试用例 |
| `evaluation/reports/` | 报告生成 |
| `evaluation/scenarios/` | 评估场景 |

### 8. src/flood_decision_agent/interfaces/ - 接口适配层

对外接口实现。

| 目录 | 用途 |
|------|------|
| `interfaces/api/` | REST API（routes, middleware, schemas） |
| `interfaces/websocket/` | WebSocket 处理器 |
| `interfaces/cli/` | 命令行接口 |

### 9. src/flood_decision_agent/shared/ - 共享组件

跨层共享的组件。

| 目录/文件 | 用途 |
|------|------|
| `shared/exceptions/` | 异常定义 |
| `shared/utils/` | 工具函数 |
| `shared/constants.py` | 全局常量 |

### 10. src/flood_decision_agent/conversation/ - 对话管理

对话上下文和状态管理。

| 文件 | 用途 |
|------|------|
| `conversation/context.py` | 对话上下文 |
| `conversation/manager.py` | 对话管理器 |
| `conversation/state.py` | 对话状态 |

### 11. src/flood_decision_agent/visualization/ - 可视化

终端可视化模块。

| 文件 | 用途 |
|------|------|
| `visualization/base.py` | 可视化基类 |
| `visualization/models.py` | 可视化模型 |
| `visualization/terminal.py` | 终端可视化实现 |

### 12. web/ - Web 应用

Web 端实现。

| 目录 | 用途 |
|------|------|
| `web/backend/` | FastAPI 后端服务 |
| `web/backend/api/` | REST API 路由 |
| `web/backend/websocket/` | WebSocket 处理器 |
| `web/frontend/` | Vue 3 前端应用 |
| `web/frontend/src/` | 前端源代码 |
| `web/frontend/e2e/` | 端到端测试 |
| `web/deploy/` | 部署脚本 |

### 13. tests/ - 测试目录

测试代码组织。

| 目录 | 用途 |
|------|------|
| `tests/unit/` | 单元测试（按模块组织：agents/, core/, api/ 等） |
| `tests/integration/` | 集成测试 |
| `tests/e2e/` | 端到端测试 |
| `tests/mcp/` | MCP 相关测试 |
| `tests/debug/` | 调试测试脚本 |
| `tests/diagnosis/` | 诊断测试脚本 |
| `tests/evaluation/` | 评估测试 |
| `tests/plan/` | Plan 模式测试 |
| `tests/output/` | 测试输出 |
| `tests/data/` | 测试数据 |
| `tests/reports/` | 测试报告 |

### 14. resources/ - 资源文件

静态资源和数据文件。

| 目录 | 用途 |
|------|------|
| `resources/data/raw/` | 原始数据文件 |
| `resources/data/hipims_results/` | HIPIMS 模拟结果 |
| `resources/datasets/` | 数据集（flood_sample, realistic_test） |
| `resources/models/` | 模型文件（如 yolo11n.pt） |
| `resources/documents/outputs/` | 文档输出 |
| `resources/plans/` | 规划文档归档 |
| `resources/results/` | 结果文件归档 |

### 15. docs/ - 文档

项目文档。

| 目录 | 用途 |
|------|------|
| `docs/01-getting-started/` | 入门指南 |
| `docs/02-architecture/` | 架构文档 |
| `docs/03-development/` | 开发指南 |
| `docs/04-api-reference/` | API 参考 |
| `docs/05-deployment/` | 部署文档 |
| `docs/06-specifications/` | 技术规范 |
| `docs/07-design-docs/` | 设计文档 |
| `docs/mcp/` | MCP 相关文档 |

### 16. scripts/ - 脚本工具

辅助脚本。

| 文件 | 用途 |
|------|------|
| `scripts/setup_env.ps1` | 环境设置脚本 |
| `scripts/deploy_mcp_services.ps1` | MCP 服务部署 |
| `scripts/start_web.py` | 启动 Web 服务 |
| `scripts/start_backend.py` | 启动后端服务 |
| `scripts/start_server.py` | 启动服务器 |
| `scripts/run_server.py` | 运行服务器 |
| `scripts/stop_web.py` | 停止 Web 服务 |

### 17. debug/ - 调试工具

调试相关工具和场景。

| 目录/文件 | 用途 |
|------|------|
| `debug/scenarios/` | 调试场景配置 |
| `debug/run_debug.py` | 调试入口 |
| `debug/run_backend.py` | 后端调试 |
| `debug/test_mcp_connection.py` | MCP 连接测试 |
| `debug/fix_environment.py` | 环境修复工具 |

### 18. examples/ - 示例代码

端到端示例和演示。

| 文件 | 用途 |
|------|------|
| `examples/quick_start.py` | 快速开始示例 |
| `examples/run_visualized_demo.py` | 可视化演示 |
| `examples/interactive_chat.py` | 交互式聊天示例 |
| `examples/demo_*.py` | 各 Agent 演示脚本 |

### 19. logs/ - 日志文件

运行时日志输出。

| 文件 | 用途 |
|------|------|
| `logs/stdout.txt` | 标准输出日志 |
| `logs/stderr.txt` | 错误输出日志 |
| `logs/test_output.txt` | 测试输出日志 |
| `logs/pipeline_output.txt` | Pipeline 输出日志 |

### 20. notebooks/ - Jupyter notebooks

分析 notebooks 和报告。

| 文件 | 用途 |
|------|------|
| `notebooks/quick_start_report.ipynb` | 快速开始报告 |

## 文件命名规范

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| Python 模块 | 小写 + 下划线 | `decision_service.py` |
| Python 类 | 大驼峰 | `DecisionService` |
| Python 常量 | 大写 + 下划线 | `MAX_RETRY_COUNT` |
| Vue 组件 | 大驼峰 | `ChatHeader.vue` |
| 配置文件 | 小写 + 连字符 | `mcp-servers.yaml` |
| 测试文件 | `test_` 前缀 | `test_decision_service.py` |
| 脚本文件 | 小写 + 下划线 | `setup_env.ps1` |
| 日志文件 | 描述性名称 | `stdout.txt`, `stderr.txt` |

## 文件定位规则

新增功能时，按以下决策树定位文件：

1. **是业务实体定义？** → `domain/entities/`
2. **是业务逻辑编排？** → `application/services/` 或 `use_cases/`
3. **是 Agent 实现？** → `agents/{agent_name}/`
4. **是 MCP 相关？** → `mcp/{servers|clients|tools}/`
5. **是数据访问？** → `infrastructure/persistence/`
6. **是 API 接口？** → `interfaces/api/routes/`
7. **是评估相关？** → `evaluation/{metrics|test_cases|reports}/`
8. **是测试代码？** → `tests/{unit|integration|e2e|mcp|debug}/对应模块/`
9. **是资源文件？** → `resources/{data|datasets|models|documents}/`
10. **是脚本工具？** → `scripts/`
11. **是日志文件？** → `logs/`

## 向后兼容性

通过 `__init__.py` 重导出保持旧导入路径兼容：

```python
# 旧导入方式（仍然有效）
from flood_decision_agent.core import BaseAgent
from flood_decision_agent.agents import DecisionChainGeneratorAgent

# 新导入方式（推荐）
from flood_decision_agent.agents.base import BaseAgent
from flood_decision_agent.agents.decision_chain import DecisionChainGeneratorAgent
```

## 配置管理

### 配置文件优先级

1. 环境变量（最高优先级）
2. 环境特定配置（development.yaml, production.yaml）
3. 默认配置（default.yaml）

### 环境变量格式

```bash
FLOOD_AGENT_APP__DEBUG=true
FLOOD_AGENT_LLM__TEMPERATURE=0.8
```

## 最佳实践

1. **分层原则**：严格遵循 DDD 分层，避免跨层调用
2. **依赖方向**：Domain → Application → Infrastructure
3. **接口隔离**：通过接口层与外部系统交互
4. **配置外部化**：所有可配置项放入 configs/
5. **测试覆盖**：每个模块对应 tests/ 中的测试
6. **资源归档**：所有数据、模型、结果文件放入 resources/
7. **日志集中**：所有日志输出集中到 logs/
8. **脚本统一**：所有启动、部署脚本放入 scripts/

## 更新日志

- **2026-04-09**: 重构项目结构，归档独立文件到对应目录
  - 移动测试文件到 `tests/debug/` 和 `tests/mcp/`
  - 移动调试脚本到 `tests/debug/`
  - 移动启动脚本到 `scripts/`
  - 移动模型文件到 `resources/models/`
  - 移动日志文件到 `logs/`
  - 移动测试报告到 `tests/reports/`
  - 移动诊断工具到 `tests/diagnosis/`
  - 移动规划文档到 `resources/plans/`
  - 移动结果文件到 `resources/results/`
  - 移动数据集到 `resources/datasets/`
