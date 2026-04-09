# 文档中心

本文档中心包含防汛调度智能决策 Agent 系统的完整技术文档。

## 文档组织结构

文档按以下层次结构组织，采用数字前缀确保目录按逻辑顺序排列：

```
docs/
├── 01-getting-started/          # 入门指南
├── 02-architecture/             # 架构文档
│   ├── directory-structure/     # 目录结构
│   └── system-overview/         # 系统概览
├── 03-development/              # 开发文档
│   ├── frontend/                # 前端开发
│   └── guides/                  # 开发指南
├── 04-api-reference/            # API 参考
├── 05-deployment/               # 部署文档
│   └── operations/              # 运维文档
├── 06-specifications/           # 技术规格
│   └── agents/                  # Agent 规格
├── 07-design-docs/              # 设计文档
│   └── prototypes/              # 原型设计
└── mcp/                         # MCP 协议文档
```

## 快速导航

### 新用户入门
- [快速开始](../README.md#快速开始) - 项目快速入门指南
- [入门指南](01-getting-started/README.md) - 详细入门教程

### 架构师/设计师
- [架构摘要](02-architecture/system-overview/architecture-summary.md) - 系统整体架构概览
- [详细架构](02-architecture/system-overview/detailed-architecture.md) - 详细架构说明
- [目录结构](02-architecture/directory-structure/directory-structure.md) - 项目目录结构说明

### 开发者
- [开发者指南](03-development/guides/developer-guide.md) - 开发指南和最佳实践
- [前端集成指南](03-development/frontend/integration-guide.md) - 前端开发集成指南
- [意图解析与参数提取](03-development/guides/intent-param-extraction.md) - 用户查询参数提取说明

### MCP 开发
- [MCP 服务使用指南](mcp/mcp_services_usage.md) - MCP 服务使用说明
- [MCP 开发者指南](mcp/mcp_developer_guide.md) - MCP 服务开发指南
- [MCP 子进程数据流](mcp/subprocess-dataflow.md) - 子进程通信机制

### API 使用者
- [决策链生成 API](04-api-reference/chain-generation-api.md) - 决策链生成 API 参考
- [输入计划规范](04-api-reference/input_plan_spec.md) - 输入计划规范说明

### 运维人员
- [HIPIMS 部署](05-deployment/operations/hipims_deployment.md) - HIPIMS 水动力模型部署
- [计划规范部署](05-deployment/operations/plan_spec_deployment.md) - 计划规范部署说明

### 技术规格
- [决策链生成器规格](06-specifications/agents/decision-chain-generator/technical-specification.md)
- [节点调度器规格](06-specifications/agents/node-scheduler/technical-specification.md)
- [单元任务执行器规格](06-specifications/agents/unit-task-executor/technical-specification.md)

### 设计文档
- [系统原型](07-design-docs/prototypes/system-prototype.md) - 系统原型设计

## 文档规范

### 文件命名规范
- 使用小写字母
- 单词间使用连字符（-）分隔
- 使用描述性名称反映内容

### 文档格式
- 所有文档使用 Markdown 格式
- 使用中文编写
- 代码示例使用相应语言的语法高亮

### 目录编号规则
- `01-` 入门和概览类文档
- `02-` 架构和设计类文档
- `03-` 开发相关文档
- `04-` API 和接口文档
- `05-` 部署和运维文档
- `06-` 技术规格和详细设计
- `07-` 设计文档和原型
- `mcp/` - MCP 协议相关文档（无编号，独立分类）

## 文档更新日志

### 2026-04-09
- ✅ 更新文档中心索引，反映最新架构
- ✅ 更新目录结构文档
- ✅ 添加 MCP 协议文档分类
- ✅ 更新开发指南和 API 参考

### 2026-04-07
- ✅ 添加 Web API 文档
- ✅ 更新前端集成指南
- ✅ 添加 Plan/Spec 模式文档

## 贡献指南

添加新文档时，请遵循以下步骤：

1. 根据文档类型选择合适的目录
2. 使用规范的命名方式创建文件
3. 更新相关目录的 README 文件
4. 确保文档格式符合规范
5. 更新本文档中心的索引

## 文档维护

- 所有文档应与代码保持同步
- 定期审查和更新过时内容
- 保持文档间的链接有效性
- 重大架构变更时同步更新架构文档

## 相关链接

- [项目 README](../README.md) - 项目总体说明
- [目录结构文档](02-architecture/directory-structure/directory-structure.md) - 详细目录结构
- [开发者指南](03-development/guides/developer-guide.md) - 开发最佳实践
