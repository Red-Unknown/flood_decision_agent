# 项目目录结构规则

## 核心目录结构

```
src/flood_decision_agent/
├── domain/          # 业务实体：entities/, value_objects/, events/
├── application/     # 业务逻辑：services/, use_cases/, dto/
├── infrastructure/  # 技术实现：llm/, persistence/, config_loader.py
├── mcp/            # MCP协议：protocol/, core/, servers/, clients/, tools/
├── agents/         # 智能体：base/, decision_chain/, node_scheduler/, task_executor/, intent_parser/
├── evaluation/     # 评估：core/, metrics/, test_cases/, reports/, scenarios/
├── interfaces/     # 接口：api/, websocket/, cli/
└── shared/         # 共享：exceptions/, utils/, constants.py
```

## 文件定位速查表

| 功能类型 | 目标目录 |
|---------|---------|
| 业务实体定义 | `domain/entities/` |
| 业务逻辑编排 | `application/services/` 或 `use_cases/` |
| Agent 实现 | `agents/{agent_name}/` |
| MCP 相关 | `mcp/{servers\|clients\|tools}/` |
| 数据访问 | `infrastructure/persistence/` |
| API 接口 | `interfaces/api/routes/` |
| 评估相关 | `evaluation/{metrics\|test_cases\|reports}/` |
| 测试代码 | `tests/{unit\|integration\|e2e}/` |
| 配置文件 | `configs/{app\|mcp\|evaluation}/` |
| 静态资源 | `resources/{data\|documents\|prompts\|static}/` |

## 必须遵守的规则

1. **所有业务实体**必须放在 `domain/entities/`
2. **所有 Agent**必须放在 `agents/{功能名}/`
3. **所有 API 路由**必须放在 `interfaces/api/routes/`
4. **所有配置**必须使用 YAML 格式放在 `configs/`
5. **所有工具函数**必须放在 `shared/utils/`
6. **所有异常定义**必须放在 `shared/exceptions/`

## 禁止事项

- 禁止在根目录创建新的 Python 文件
- 禁止跨层导入（如 domain 导入 infrastructure）
- 禁止使用 JSON 配置（除遗留代码外）
- 禁止在 `core/` 目录新增文件（仅用于向后兼容重导出）

## 命名规范

- Python 模块：小写 + 下划线（`decision_service.py`）
- Python 类：大驼峰（`DecisionService`）
- 配置文件：小写 + 连字符（`mcp-servers.yaml`）
- 测试文件：`test_` 前缀（`test_decision_service.py`）
