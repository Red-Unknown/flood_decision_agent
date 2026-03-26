# 项目目录结构完整说明

## 项目根目录

```
flood_decision_agent/
├── .github/                    # GitHub 工作流与贡献规范
├── .trae/                      # Trae IDE 配置
│   ├── documents/              # 文档
│   ├── rules/                  # 项目规则
│   ├── skills/                 # 自定义技能
│   └── specs/                  # 功能规格文档
├── configs/                    # 【新增】集中式配置管理
├── data/                       # 【待迁移】数据文件（将迁移到 resources/data/）
├── debug/                      # 调试脚本
├── docs/                       # 文档
│   ├── architecture/           # 架构文档
│   ├── api/                    # API 文档
│   ├── development/            # 开发指南
│   └── deployment/             # 部署文档
├── evaluation/                 # 【已整合】评估框架（已整合到 src/）
├── examples/                   # 示例代码
├── experiments/                # 实验代码
├── notebooks/                  # Jupyter 笔记本
├── plans/                      # 【待迁移】规划文件（将迁移到 resources/documents/outputs/）
├── resources/                  # 【新增】资源文件
├── scripts/                    # 脚本工具
├── src/                        # 【重构】核心业务代码
├── tests/                      # 【重构】测试目录
├── web/                        # 【重构】Web 应用
├── .flake8                     # Flake8 配置
├── .gitignore                  # Git 忽略配置
├── .pre-commit-config.yaml     # pre-commit 配置
├── environment.yml             # Conda 环境配置
├── pyproject.toml              # Python 项目配置
├── requirements.txt            # Python 依赖
├── requirements-dev.txt        # 开发依赖
├── setup.py                    # 安装脚本
└── README.md                   # 项目说明
```

---

## 核心代码目录 (src/flood_decision_agent/)

```
src/flood_decision_agent/
├── __init__.py
├── __version__.py              # 版本信息
│
├── domain/                     # 【新增】领域层 - 核心业务实体
│   ├── __init__.py
│   ├── entities/               # 领域实体
│   │   ├── __init__.py
│   │   ├── decision.py         # 决策实体
│   │   ├── task.py             # 任务实体
│   │   ├── message.py          # 消息实体
│   │   └── conversation.py     # 对话实体
│   ├── value_objects/          # 值对象
│   │   ├── __init__.py
│   │   ├── priority.py         # 优先级
│   │   └── status.py           # 状态
│   └── events/                 # 领域事件
│       ├── __init__.py
│       └── task_events.py      # 任务事件
│
├── application/                # 【新增】应用层 - 业务逻辑编排
│   ├── __init__.py
│   ├── services/               # 应用服务
│   │   ├── __init__.py
│   │   ├── decision_service.py
│   │   ├── chat_service.py
│   │   └── evaluation_service.py
│   ├── use_cases/              # 用例实现
│   │   ├── __init__.py
│   │   ├── generate_decision_chain.py
│   │   ├── schedule_nodes.py
│   │   └── execute_unit_task.py
│   └── dto/                    # 数据传输对象
│       ├── __init__.py
│       ├── request.py
│       └── response.py
│
├── infrastructure/             # 【重构】基础设施层
│   ├── __init__.py
│   ├── config_loader.py        # 配置加载器
│   ├── llm/                    # LLM 客户端
│   │   ├── __init__.py
│   │   ├── client.py           # 统一LLM接口
│   │   ├── kimi_client.py      # Kimi实现
│   │   └── guards/             # 安全守卫
│   │       └── kimi_guard.py
│   ├── persistence/            # 数据持久化
│   │   ├── __init__.py
│   │   ├── repositories/       # 仓储模式
│   │   │   ├── conversation_repo.py
│   │   │   └── decision_repo.py
│   │   └── cache/              # 缓存
│   │       └── redis_cache.py
│   └── logging/                # 日志
│       └── structured_logger.py
│
├── mcp/                        # 【重构】MCP 协议层
│   ├── __init__.py
│   ├── README.md
│   ├── adapters/               # 适配器层
│   │   ├── __init__.py
│   │   └── tool_adapter.py
│   ├── clients/                # 客户端实现
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── filesystem.py
│   ├── configs/                # 配置文件
│   │   └── mcp_servers.json
│   ├── core/                   # 【新增】核心组件
│   │   ├── __init__.py
│   │   ├── server.py           # 服务器基类
│   │   ├── client.py           # 客户端基类
│   │   ├── session.py          # 会话管理
│   │   └── transport.py        # 传输层
│   ├── protocol/               # 【新增】协议定义
│   │   ├── __init__.py
│   │   ├── types.py            # 类型定义
│   │   ├── messages.py         # 消息格式
│   │   └── constants.py        # 常量
│   ├── servers/                # 服务器实现
│   │   ├── __init__.py
│   │   ├── document_server.py
│   │   ├── filesystem_server.py
│   │   └── hydrology_server.py
│   └── tools/                  # 工具定义
│       ├── __init__.py
│       ├── registry.py
│       └── adapters/           # 工具适配器
│           ├── hydrology_adapter.py
│           └── document_adapter.py
│
├── agents/                     # 【重构】智能体层
│   ├── __init__.py
│   ├── base/                   # 【新增】基类
│   │   ├── __init__.py
│   │   └── agent.py            # 统一Agent基类
│   ├── decision_chain/         # 决策链生成
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   ├── chain_optimizer.py
│   │   ├── task_decomposer.py
│   │   └── prompts.py
│   ├── intent_parser/          # 意图解析
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   └── parser_v2.py
│   ├── node_scheduler/         # 节点调度
│   │   ├── __init__.py
│   │   └── scheduler.py
│   ├── summarizer.py
│   └── task_executor/          # 任务执行
│       ├── __init__.py
│       └── executor.py
│
├── evaluation/                 # 【重构】评估框架
│   ├── __init__.py
│   ├── core/                   # 评估核心
│   │   ├── __init__.py
│   │   ├── evaluator.py
│   │   ├── runner.py           # 运行器
│   │   └── registry.py         # 注册表
│   ├── metrics/                # 评估指标
│   │   ├── __init__.py
│   │   └── base.py
│   ├── test_cases/             # 测试用例
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── builder.py
│   │   └── loaders/            # 加载器
│   │       ├── __init__.py
│   │       ├── json_loader.py
│   │       └── yaml_loader.py
│   ├── reports/                # 报告生成
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── formatters/         # 格式化器
│   │   │   ├── __init__.py
│   │   │   ├── csv_formatter.py
│   │   │   ├── json_formatter.py
│   │   │   └── markdown_formatter.py
│   │   └── templates/          # 模板
│   │       ├── __init__.py
│   │       ├── default_template.py
│   │       └── minimal_template.py
│   └── scenarios/              # 评估场景
│       ├── __init__.py
│       ├── base.py
│       └── flood_scenarios.py
│
├── interfaces/                 # 【新增】接口适配层
│   ├── __init__.py
│   ├── api/                    # REST API
│   │   ├── __init__.py
│   │   ├── routes/             # 路由
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── conversations.py
│   │   │   └── health.py
│   │   ├── middleware/         # 中间件
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── cors.py
│   │   │   └── logging.py
│   │   ├── dependencies/       # 依赖注入
│   │   │   ├── __init__.py
│   │   │   └── services.py
│   │   └── schemas/            # API 模式
│   │       ├── __init__.py
│   │       ├── request.py
│   │       └── response.py
│   ├── websocket/              # WebSocket
│   │   ├── __init__.py
│   │   ├── handlers/           # 处理器
│   │   │   ├── __init__.py
│   │   │   └── chat_handler.py
│   │   └── connection.py       # 连接管理
│   └── cli/                    # 命令行接口
│       ├── __init__.py
│       └── commands/           # 命令定义
│           ├── __init__.py
│           ├── chat.py
│           └── evaluate.py
│
├── conversation/               # 【保留】对话管理
│   ├── __init__.py
│   ├── context.py
│   ├── manager.py
│   └── state.py
│
├── shared/                     # 【新增】共享组件
│   ├── __init__.py
│   ├── constants.py            # 全局常量
│   ├── exceptions/             # 异常定义
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── mcp_errors.py
│   │   └── agent_errors.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── datetime.py
│       ├── validation.py
│       └── crypto.py
│
├── visualization/              # 【保留】可视化
│   ├── __init__.py
│   ├── base.py
│   ├── models.py
│   ├── terminal.py
│   └── renderers/              # 【新增】渲染器
│       ├── __init__.py
│       ├── graph_renderer.py
│       └── table_renderer.py
│
└── core/                       # 【保留但重导出】核心模块
    ├── __init__.py
    ├── message.py
    ├── shared_data_pool.py
    ├── task_graph.py
    ├── task_graph_builder.py
    ├── task_types.py
    └── README.md
```

---

## 配置目录 (configs/)

```
configs/
├── app/                        # 应用配置
│   ├── default.yaml            # 默认配置
│   ├── development.yaml        # 开发环境
│   └── production.yaml         # 生产环境
├── mcp/                        # MCP 配置
│   ├── servers.yaml            # 服务器注册表
│   └── tools.yaml              # 工具定义
└── evaluation/                 # 评估配置
    ├── metrics.yaml
    └── scenarios.yaml
```

---

## 资源目录 (resources/)

```
resources/
├── data/                       # 数据文件
│   ├── raw/                    # 原始数据
│   ├── processed/              # 处理后数据
│   └── samples/                # 样本数据
├── documents/                  # 文档
│   ├── templates/              # 文档模板
│   └── outputs/                # 输出文件（原 plans/）
├── prompts/                    # Prompt 模板
│   ├── decision_chain/         # 决策链 Prompt
│   ├── node_scheduler/         # 调度 Prompt
│   └── task_executor/          # 执行 Prompt
└── static/                     # 静态资源
    ├── images/
    └── fonts/
```

---

## Web 目录 (web/)

```
web/
├── backend/                    # 后端服务
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口
│   ├── lifespan.py             # 生命周期管理
│   ├── core/                   # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── events.py
│   │   └── security.py
│   ├── api/                    # API 层
│   │   └── __init__.py
│   └── services/               # Web 专属服务
│       ├── __init__.py
│       ├── session_manager.py
│       └── rate_limiter.py
│
└── frontend/                   # 前端应用
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── public/                 # 静态资源
    │   ├── favicon.ico
    │   └── logo.svg
    └── src/
        ├── main.js
        ├── App.vue
        ├── api/                # API 客户端
        │   ├── index.js
        │   ├── client.js
        │   ├── chat.js
        │   └── websocket.js
        ├── components/         # 组件
        │   ├── common/         # 通用组件
        │   │   ├── Button.vue
        │   │   ├── Modal.vue
        │   │   └── Loading.vue
        │   ├── chat/           # 聊天相关
        │   │   ├── ChatHeader.vue
        │   │   ├── ChatInput.vue
        │   │   ├── ChatMessage.vue
        │   │   ├── ChatSidebar.vue
        │   │   └── EmptyState.vue
        │   └── visualization/  # 可视化组件
        │       └── ProcessTimeline.vue
        ├── composables/        # 组合式函数
        │   ├── useChat.js
        │   ├── useWebSocket.js
        │   └── useConversation.js
        ├── stores/             # 状态管理
        │   ├── index.js
        │   ├── chat.js
        │   └── user.js
        ├── router/             # 路由
        │   └── index.js
        ├── views/              # 页面
        │   ├── ChatView.vue
        │   └── HomeView.vue
        ├── styles/             # 样式
        │   ├── global.scss
        │   ├── variables.scss
        │   └── mixins.scss
        └── utils/              # 工具
            ├── index.js
            ├── formatters.js
            └── validators.js
```

---

## 测试目录 (tests/)

```
tests/
├── __init__.py
├── conftest.py                 # pytest 配置
├── pytest.ini                  # pytest 配置
├── README.md
│
├── unit/                       # 单元测试
│   ├── __init__.py
│   ├── domain/                 # 领域层测试
│   ├── application/            # 应用层测试
│   ├── agents/                 # Agent 测试
│   ├── infrastructure/         # 基础设施测试
│   └── evaluation/             # 评估测试
│
├── integration/                # 集成测试
│   ├── __init__.py
│   ├── api/                    # API 集成
│   ├── mcp/                    # MCP 集成
│   └── agents/                 # Agent 集成
│
├── e2e/                        # 端到端测试
│   ├── __init__.py
│   ├── scenarios/              # 场景测试
│   └── workflows/              # 工作流测试
│
├── fixtures/                   # 测试夹具
│   ├── __init__.py
│   ├── data/                   # 测试数据
│   │   ├── conversations.json
│   │   └── decisions.json
│   └── mocks/                  # Mock 对象
│       ├── llm_client.py
│       └── mcp_server.py
│
└── utils/                      # 测试工具
    ├── __init__.py
    ├── factories.py            # 工厂函数
    └── helpers.py
```

---

## 关键设计原则

### 1. 分层架构

```
┌─────────────────────────────────────────┐
│           Interfaces 接口层              │  ← API / CLI / WebSocket
├─────────────────────────────────────────┤
│         Application 应用层              │  ← 用例编排、事务控制
├─────────────────────────────────────────┤
│           Domain 领域层                 │  ← 核心业务逻辑
├─────────────────────────────────────────┤
│       Infrastructure 基础设施层          │  ← 技术实现细节
└─────────────────────────────────────────┘
```

### 2. 依赖规则

- **Domain** 不依赖任何其他层
- **Application** 只依赖 Domain
- **Infrastructure** 依赖 Domain 和 Application
- **Interfaces** 依赖所有层

### 3. 向后兼容

通过 `__init__.py` 重导出保持旧导入路径有效：

```python
# 旧导入（仍然有效）
from flood_decision_agent.core import BaseAgent

# 新导入（推荐）
from flood_decision_agent.agents.base import BaseAgent
```

---

## 文件定位速查表

| 功能类型 | 目标目录 |
|---------|---------|
| 业务实体定义 | `domain/entities/` |
| 业务逻辑编排 | `application/services/` 或 `use_cases/` |
| Agent 实现 | `agents/{agent_name}/` |
| MCP 相关 | `mcp/{servers|clients|tools}/` |
| 数据访问 | `infrastructure/persistence/` |
| API 接口 | `interfaces/api/routes/` |
| 评估相关 | `evaluation/{metrics|test_cases|reports}/` |
| 测试代码 | `tests/{unit|integration|e2e}/` |
| 配置文件 | `configs/{app|mcp|evaluation}/` |
| 静态资源 | `resources/{data|documents|prompts|static}/` |
