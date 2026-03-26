# 项目目录结构说明

## 概述

本文档详细说明 `flood_decision_agent` 项目的目录结构设计，包括各目录的功能定义、文件存放规则及使用规范。

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
└── scripts/                    # 脚本工具
```

## 详细说明

### 1. configs/ - 集中式配置管理

存放所有配置文件，支持 YAML 和 JSON 格式。

| 目录 | 用途 |
|------|------|
| `configs/app/` | 应用配置（default.yaml, development.yaml, production.yaml） |
| `configs/mcp/` | MCP 服务配置（servers.yaml, tools.yaml） |
| `configs/evaluation/` | 评估配置（metrics.yaml, scenarios.yaml） |

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

| 目录 | 用途 |
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
| `mcp/servers/` | 服务器实现（filesystem, hydrology, document） |
| `mcp/clients/` | 客户端实现 |
| `mcp/tools/` | 工具定义和适配器 |

### 6. src/flood_decision_agent/agents/ - 智能体层

各类 Agent 的实现。

| 目录 | 用途 |
|------|------|
| `agents/base/` | Agent 基类 |
| `agents/decision_chain/` | 决策链生成 |
| `agents/node_scheduler/` | 节点调度 |
| `agents/task_executor/` | 任务执行 |
| `agents/intent_parser/` | 意图解析 |

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

| 目录 | 用途 |
|------|------|
| `shared/exceptions/` | 异常定义 |
| `shared/utils/` | 工具函数 |
| `shared/constants.py` | 全局常量 |

### 10. web/ - Web 应用

Web 端实现。

| 目录 | 用途 |
|------|------|
| `web/backend/` | FastAPI 后端服务 |
| `web/frontend/` | Vue 3 前端应用 |

### 11. tests/ - 测试目录

测试代码组织。

| 目录 | 用途 |
|------|------|
| `tests/unit/` | 单元测试 |
| `tests/integration/` | 集成测试 |
| `tests/e2e/` | 端到端测试 |
| `tests/fixtures/` | 测试夹具 |
| `tests/utils/` | 测试工具 |

### 12. resources/ - 资源文件

静态资源和数据文件。

| 目录 | 用途 |
|------|------|
| `resources/data/` | 数据文件（raw, processed, samples） |
| `resources/documents/` | 文档模板和输出 |
| `resources/prompts/` | Prompt 模板 |
| `resources/static/` | 静态资源（images, fonts） |

## 文件命名规范

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| Python 模块 | 小写 + 下划线 | `decision_service.py` |
| Python 类 | 大驼峰 | `DecisionService` |
| Python 常量 | 大写 + 下划线 | `MAX_RETRY_COUNT` |
| Vue 组件 | 大驼峰 | `ChatHeader.vue` |
| 配置文件 | 小写 + 连字符 | `mcp-servers.yaml` |
| 测试文件 | `test_` 前缀 | `test_decision_service.py` |

## 文件定位规则

新增功能时，按以下决策树定位文件：

1. **是业务实体定义？** → `domain/entities/`
2. **是业务逻辑编排？** → `application/services/` 或 `use_cases/`
3. **是 Agent 实现？** → `agents/{agent_name}/`
4. **是 MCP 相关？** → `mcp/{servers|clients|tools}/`
5. **是数据访问？** → `infrastructure/persistence/`
6. **是 API 接口？** → `interfaces/api/routes/`
7. **是评估相关？** → `evaluation/{metrics|test_cases|reports}/`
8. **是测试代码？** → `tests/{unit|integration|e2e}/对应模块/`

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
