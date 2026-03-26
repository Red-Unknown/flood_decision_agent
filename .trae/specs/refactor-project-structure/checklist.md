# 项目目录结构重构检查清单

## Phase 1: 基础结构搭建

### Task 1: 创建新目录结构
- [ ] configs/ 目录及子目录已创建
  - [ ] configs/app/ 存在
  - [ ] configs/mcp/ 存在
  - [ ] configs/evaluation/ 存在
- [ ] domain/ 目录结构已创建
  - [ ] domain/entities/ 存在
  - [ ] domain/value_objects/ 存在
  - [ ] domain/events/ 存在
- [ ] application/ 目录结构已创建
  - [ ] application/services/ 存在
  - [ ] application/use_cases/ 存在
  - [ ] application/dto/ 存在
- [ ] infrastructure/ 目录结构已创建
  - [ ] infrastructure/llm/ 存在
  - [ ] infrastructure/persistence/ 存在
  - [ ] infrastructure/logging/ 存在
- [ ] mcp/protocol/ 目录已创建
- [ ] interfaces/ 目录结构已创建
  - [ ] interfaces/api/ 存在
  - [ ] interfaces/websocket/ 存在
  - [ ] interfaces/cli/ 存在
- [ ] shared/ 目录结构已创建
  - [ ] shared/exceptions/ 存在
  - [ ] shared/utils/ 存在

### Task 2: 重构 agents 目录
- [ ] agents/base/ 目录已创建
  - [ ] 现有基类已迁移到 base/
  - [ ] 统一的 Agent 基类已创建
- [ ] agents/decision_chain/ 目录已创建
  - [ ] decision_chain_generator.py 已迁移
  - [ ] decision_chain_generator_mcp.py 已迁移
  - [ ] chain_optimizer.py 已从 core/ 迁移
  - [ ] prompts.py 已从 core/ 迁移
- [ ] agents/node_scheduler/ 目录已创建
  - [ ] node_scheduler.py 已迁移
  - [ ] task_graph_builder.py 已从 core/ 迁移
- [ ] agents/task_executor/ 目录已创建
  - [ ] unit_task_executor.py 已迁移
  - [ ] task_decomposer.py 已从 core/ 迁移
- [ ] agents/intent_parser/ 目录已创建
  - [ ] intent_parser.py 已从 core/ 迁移
  - [ ] intent_parser_v2.py 已从 core/ 迁移

### Task 3: 重构 evaluation 目录
- [ ] evaluation/core/ 目录已创建
  - [ ] evaluator.py 已迁移
  - [ ] runner.py 已创建
  - [ ] registry.py 已创建
- [ ] evaluation/metrics/ 目录已创建
  - [ ] metrics.py 已迁移为 base.py
  - [ ] 具体指标实现文件已创建
- [ ] evaluation/test_cases/ 目录已创建
  - [ ] test_case.py 已迁移
  - [ ] builder.py 已创建
  - [ ] loaders/ 子目录已创建
- [ ] evaluation/reports/ 目录已创建
  - [ ] report.py 已迁移
  - [ ] formatters/ 子目录已创建
  - [ ] templates/ 子目录已创建
- [ ] evaluation/scenarios/ 目录已创建
  - [ ] base.py 已创建
  - [ ] flood_scenarios.py 已创建

### Task 4: 重构 mcp 目录
- [ ] mcp/protocol/ 目录已创建
  - [ ] types.py 已创建
  - [ ] messages.py 已创建
  - [ ] constants.py 已创建
- [ ] mcp/core/ 目录已创建
  - [ ] server.py 已创建
  - [ ] client.py 已创建
  - [ ] session.py 已创建
  - [ ] transport.py 已创建
- [ ] 现有 servers/ 实现已迁移
- [ ] 现有 clients/ 实现已迁移
- [ ] 现有 tools/ 实现已迁移

### Task 5: 创建 resources 目录
- [ ] resources/data/ 目录已创建
  - [ ] raw/ 存在
  - [ ] processed/ 存在
  - [ ] samples/ 存在
- [ ] resources/documents/ 目录已创建
  - [ ] templates/ 存在
  - [ ] outputs/ 存在
- [ ] resources/prompts/ 目录已创建
  - [ ] decision_chain/ 存在
  - [ ] node_scheduler/ 存在
  - [ ] task_executor/ 存在
- [ ] resources/static/ 目录已创建
  - [ ] images/ 存在
  - [ ] fonts/ 存在

### Task 6: 重构 tests 目录
- [ ] tests/unit/ 目录结构已创建
  - [ ] unit/domain/ 存在
  - [ ] unit/application/ 存在
  - [ ] unit/agents/ 存在
  - [ ] unit/infrastructure/ 存在
  - [ ] unit/evaluation/ 存在
- [ ] tests/integration/ 目录结构已创建
  - [ ] integration/api/ 存在
  - [ ] integration/mcp/ 存在
  - [ ] integration/agents/ 存在
- [ ] tests/e2e/ 目录结构已创建
  - [ ] e2e/scenarios/ 存在
  - [ ] e2e/workflows/ 存在
- [ ] tests/fixtures/ 目录已创建
  - [ ] fixtures/data/ 存在
  - [ ] fixtures/mocks/ 存在
- [ ] tests/utils/ 目录已创建

### Task 7: 重构 web 目录
- [ ] web/backend/ 结构已重构
  - [ ] core/ 目录已创建
  - [ ] api/ 目录已创建
  - [ ] services/ 目录已创建
- [ ] web/frontend/ 结构已重构
  - [ ] components/common/ 目录已创建
  - [ ] components/chat/ 目录已创建
  - [ ] components/visualization/ 目录已创建
  - [ ] composables/ 目录已创建
  - [ ] utils/ 目录已创建
  - [ ] tests/ 目录已创建

## Phase 2: 配置文件迁移

### Task 8: 创建 YAML 配置文件
- [ ] configs/app/default.yaml 已创建
- [ ] configs/app/development.yaml 已创建
- [ ] configs/app/production.yaml 已创建
- [ ] configs/mcp/servers.yaml 已创建（从 mcp_servers.json 迁移）
- [ ] configs/mcp/tools.yaml 已创建
- [ ] configs/evaluation/metrics.yaml 已创建
- [ ] configs/evaluation/scenarios.yaml 已创建

### Task 9: 配置加载器实现
- [ ] 配置加载工具类已实现
  - [ ] 支持 YAML 格式
  - [ ] 支持 JSON 格式（向后兼容）
  - [ ] 环境变量覆盖
  - [ ] 配置合并策略

## Phase 3: 向后兼容性实现

### Task 10: 创建重导出 __init__.py
- [ ] agents/ 重导出已创建
- [ ] core/ 重导出已创建
- [ ] evaluation/ 重导出已创建
- [ ] mcp/ 重导出已创建
- [ ] tools/ 重导出已创建

### Task 11: 迁移数据文件
- [ ] data/ 已迁移到 resources/data/
- [ ] plans/ 已迁移到 resources/documents/outputs/
- [ ] 所有文件引用路径已更新

### Task 12: 更新导入语句
- [ ] 所有文件中的导入语句已扫描
- [ ] 相对导入已更新为绝对导入
- [ ] 无循环导入

## Phase 4: 验证与测试

### Task 13: 导入验证
- [ ] 所有旧导入路径仍然有效
- [ ] 新导入路径正常工作
- [ ] 快速启动示例验证通过

### Task 14: 测试验证
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 测试覆盖率达标（≥80%）

### Task 15: 功能验证
- [ ] MCP 功能正常
- [ ] Evaluation 功能正常
- [ ] Web 端功能正常
- [ ] Pipeline 功能正常

## Phase 5: 文档更新

### Task 16: 更新项目文档
- [ ] README.md 已更新
- [ ] docs/architecture/ 文档已创建
- [ ] docs/development/ 开发指南已创建
- [ ] 目录结构说明文档已创建

### Task 17: 创建迁移指南
- [ ] 文件定位指南已编写
- [ ] 命名规范文档已编写
- [ ] 开发规范文档已编写
