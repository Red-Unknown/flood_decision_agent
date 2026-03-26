# 项目目录结构重构任务列表

## Phase 1: 基础结构搭建

### Task 1: 创建新目录结构
- [ ] 创建 configs/ 目录及子目录
  - [ ] configs/app/ - 应用配置
  - [ ] configs/mcp/ - MCP配置
  - [ ] configs/evaluation/ - 评估配置
- [ ] 创建 src/flood_decision_agent/domain/ 目录结构
  - [ ] domain/entities/ - 领域实体
  - [ ] domain/value_objects/ - 值对象
  - [ ] domain/events/ - 领域事件
- [ ] 创建 src/flood_decision_agent/application/ 目录结构
  - [ ] application/services/ - 应用服务
  - [ ] application/use_cases/ - 用例编排
  - [ ] application/dto/ - DTO定义
- [ ] 创建 src/flood_decision_agent/infrastructure/ 目录结构
  - [ ] infrastructure/llm/ - LLM客户端
  - [ ] infrastructure/persistence/ - 数据持久化
  - [ ] infrastructure/logging/ - 日志
- [ ] 创建 src/flood_decision_agent/mcp/protocol/ 目录
- [ ] 创建 src/flood_decision_agent/interfaces/ 目录结构
  - [ ] interfaces/api/ - REST API
  - [ ] interfaces/websocket/ - WebSocket
  - [ ] interfaces/cli/ - 命令行
- [ ] 创建 src/flood_decision_agent/shared/ 目录结构
  - [ ] shared/exceptions/ - 异常定义
  - [ ] shared/utils/ - 工具函数

### Task 2: 重构 agents 目录
- [ ] 创建 agents/base/ 目录
  - [ ] 迁移现有基类到 base/
  - [ ] 创建统一的 Agent 基类
- [ ] 创建 agents/decision_chain/ 目录
  - [ ] 迁移 decision_chain_generator.py
  - [ ] 迁移 decision_chain_generator_mcp.py
  - [ ] 从 core/ 迁移 chain_optimizer.py
  - [ ] 从 core/ 迁移 prompts.py
- [ ] 创建 agents/node_scheduler/ 目录
  - [ ] 迁移 node_scheduler.py
  - [ ] 从 core/ 迁移 task_graph_builder.py
- [ ] 创建 agents/task_executor/ 目录
  - [ ] 迁移 unit_task_executor.py
  - [ ] 从 core/ 迁移 task_decomposer.py
- [ ] 创建 agents/intent_parser/ 目录
  - [ ] 从 core/ 迁移 intent_parser.py
  - [ ] 从 core/ 迁移 intent_parser_v2.py

### Task 3: 重构 evaluation 目录
- [ ] 创建 evaluation/core/ 目录
  - [ ] 迁移 evaluator.py
  - [ ] 创建 runner.py 运行器
  - [ ] 创建 registry.py 注册表
- [ ] 创建 evaluation/metrics/ 目录
  - [ ] 迁移 metrics.py 为 base.py
  - [ ] 创建具体指标实现文件
- [ ] 创建 evaluation/test_cases/ 目录
  - [ ] 迁移 test_case.py
  - [ ] 创建 builder.py
  - [ ] 创建 loaders/ 子目录
- [ ] 创建 evaluation/reports/ 目录
  - [ ] 迁移 report.py
  - [ ] 创建 formatters/ 子目录
  - [ ] 创建 templates/ 子目录
- [ ] 创建 evaluation/scenarios/ 目录
  - [ ] 创建 base.py
  - [ ] 创建 flood_scenarios.py

### Task 4: 重构 mcp 目录
- [ ] 创建 mcp/protocol/ 目录
  - [ ] 创建 types.py - 类型定义
  - [ ] 创建 messages.py - 消息格式
  - [ ] 创建 constants.py - 常量定义
- [ ] 创建 mcp/core/ 目录
  - [ ] 创建 server.py - 服务器基类
  - [ ] 创建 client.py - 客户端基类
  - [ ] 创建 session.py - 会话管理
  - [ ] 创建 transport.py - 传输层
- [ ] 迁移现有 servers/ 实现
- [ ] 迁移现有 clients/ 实现
- [ ] 迁移现有 tools/ 实现

### Task 5: 创建 resources 目录
- [ ] 创建 resources/data/ 目录
  - [ ] raw/ - 原始数据
  - [ ] processed/ - 处理后数据
  - [ ] samples/ - 样本数据
- [ ] 创建 resources/documents/ 目录
  - [ ] templates/ - 文档模板
  - [ ] outputs/ - 输出文件（迁移 plans/）
- [ ] 创建 resources/prompts/ 目录
  - [ ] decision_chain/ - 决策链Prompt
  - [ ] node_scheduler/ - 调度Prompt
  - [ ] task_executor/ - 执行Prompt
- [ ] 创建 resources/static/ 目录
  - [ ] images/
  - [ ] fonts/

### Task 6: 重构 tests 目录
- [ ] 创建 tests/unit/ 目录结构
  - [ ] unit/domain/
  - [ ] unit/application/
  - [ ] unit/agents/
  - [ ] unit/infrastructure/
  - [ ] unit/evaluation/
- [ ] 创建 tests/integration/ 目录结构
  - [ ] integration/api/
  - [ ] integration/mcp/
  - [ ] integration/agents/
- [ ] 创建 tests/e2e/ 目录结构
  - [ ] e2e/scenarios/
  - [ ] e2e/workflows/
- [ ] 创建 tests/fixtures/ 目录
  - [ ] fixtures/data/
  - [ ] fixtures/mocks/
- [ ] 创建 tests/utils/ 目录

### Task 7: 重构 web 目录
- [ ] 重构 web/backend/ 结构
  - [ ] 创建 core/ 目录
  - [ ] 创建 api/ 目录（从 interfaces 复用）
  - [ ] 创建 services/ 目录
- [ ] 重构 web/frontend/ 结构
  - [ ] 创建 components/common/ 目录
  - [ ] 创建 components/chat/ 目录
  - [ ] 创建 components/visualization/ 目录
  - [ ] 创建 composables/ 目录
  - [ ] 创建 utils/ 目录
  - [ ] 创建 tests/ 目录

## Phase 2: 配置文件迁移

### Task 8: 创建 YAML 配置文件
- [ ] 创建 configs/app/default.yaml
- [ ] 创建 configs/app/development.yaml
- [ ] 创建 configs/app/production.yaml
- [ ] 创建 configs/mcp/servers.yaml（从 mcp_servers.json 迁移）
- [ ] 创建 configs/mcp/tools.yaml
- [ ] 创建 configs/evaluation/metrics.yaml
- [ ] 创建 configs/evaluation/scenarios.yaml

### Task 9: 配置加载器实现
- [ ] 实现配置加载工具类
  - [ ] 支持 YAML 格式
  - [ ] 支持 JSON 格式（向后兼容）
  - [ ] 环境变量覆盖
  - [ ] 配置合并策略

## Phase 3: 向后兼容性实现

### Task 10: 创建重导出 __init__.py
- [ ] 为 agents/ 创建重导出
- [ ] 为 core/ 创建重导出
- [ ] 为 evaluation/ 创建重导出
- [ ] 为 mcp/ 创建重导出
- [ ] 为 tools/ 创建重导出

### Task 11: 迁移数据文件
- [ ] 迁移 data/ 到 resources/data/
- [ ] 迁移 plans/ 到 resources/documents/outputs/
- [ ] 更新所有文件引用路径

### Task 12: 更新导入语句
- [ ] 扫描所有文件中的导入语句
- [ ] 更新相对导入为绝对导入
- [ ] 验证无循环导入

## Phase 4: 验证与测试

### Task 13: 导入验证
- [ ] 验证所有旧导入路径仍然有效
- [ ] 验证新导入路径正常工作
- [ ] 运行快速启动示例验证

### Task 14: 测试验证
- [ ] 运行单元测试
- [ ] 运行集成测试
- [ ] 验证测试覆盖率

### Task 15: 功能验证
- [ ] 验证 MCP 功能正常
- [ ] 验证 Evaluation 功能正常
- [ ] 验证 Web 端功能正常
- [ ] 验证 Pipeline 功能正常

## Phase 5: 文档更新

### Task 16: 更新项目文档
- [ ] 更新 README.md
- [ ] 创建 docs/architecture/ 文档
- [ ] 创建 docs/development/ 开发指南
- [ ] 创建目录结构说明文档

### Task 17: 创建迁移指南
- [ ] 编写文件定位指南
- [ ] 编写命名规范文档
- [ ] 编写开发规范文档

# 任务依赖关系

```
Phase 1: 基础结构
    │
    ├──► Task 1 (创建目录) ──► Task 2 (重构agents)
    │                            │
    ├──► Task 3 (重构evaluation) ◄┘
    │
    ├──► Task 4 (重构mcp)
    │
    ├──► Task 5 (创建resources)
    │
    ├──► Task 6 (重构tests)
    │
    └──► Task 7 (重构web)

Phase 2: 配置迁移
    │
    └──► Task 8 (YAML配置) ──► Task 9 (配置加载器)

Phase 3: 向后兼容
    │
    ├──► Task 10 (重导出)
    │
    ├──► Task 11 (迁移数据)
    │
    └──► Task 12 (更新导入)

Phase 4: 验证
    │
    ├──► Task 13 (导入验证)
    │
    ├──► Task 14 (测试验证)
    │
    └──► Task 15 (功能验证)

Phase 5: 文档
    │
    ├──► Task 16 (更新文档)
    │
    └──► Task 17 (迁移指南)
```

# 并行开发建议

- **可并行**: Phase 1 中的所有 Task 1-7 可以并行
- **可并行**: Task 8 和 Task 10 可以并行
- **必须串行**: Phase 2 依赖 Phase 1
- **必须串行**: Phase 3 依赖 Phase 2
- **必须串行**: Phase 4 依赖 Phase 3
- **必须串行**: Phase 5 依赖 Phase 4
