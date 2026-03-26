# 项目目录结构重构规格说明

## Why

随着MCP服务的引入、evaluation机制的确认与web端开发，项目的目录结构已无法满足日益复杂的业务需求，存在组织混乱、文件定位困难等问题。需要重新设计一套精细化的项目目录结构，以提升团队协作效率与代码可维护性。

## What Changes

### 新增目录结构

1. **configs/** - 集中式配置管理
   - 应用配置（支持YAML格式）
   - MCP服务配置
   - 评估配置

2. **src/flood_decision_agent/domain/** - 领域层
   - 核心业务实体定义
   - 值对象
   - 领域事件

3. **src/flood_decision_agent/application/** - 应用层
   - 应用服务
   - 用例编排
   - DTO定义

4. **src/flood_decision_agent/infrastructure/** - 基础设施层
   - LLM客户端
   - 数据持久化
   - 日志、缓存

5. **src/flood_decision_agent/mcp/protocol/** - MCP协议层
   - 类型定义
   - 消息格式
   - 常量定义

6. **src/flood_decision_agent/interfaces/** - 接口适配层
   - REST API路由
   - WebSocket处理器
   - CLI命令

7. **src/flood_decision_agent/shared/** - 共享组件
   - 异常定义
   - 工具函数
   - 全局常量

8. **resources/** - 资源文件
   - 数据文件
   - 文档模板
   - Prompt模板
   - 静态资源

### 重构目录

1. **src/flood_decision_agent/agents/** - 智能体层
   - 增加base/子目录存放基类
   - 按功能划分为decision_chain/、node_scheduler/、task_executor/、intent_parser/

2. **src/flood_decision_agent/evaluation/** - 评估框架
   - 细分为core/、metrics/、test_cases/、reports/、scenarios/

3. **src/flood_decision_agent/mcp/** - MCP模块
   - 增加protocol/、core/子目录
   - servers/、clients/、tools/保持现有实现

4. **web/** - Web应用
   - backend/作为独立Python包
   - frontend/增加composables/、utils/子目录

5. **tests/** - 测试目录
   - 细分为unit/、integration/、e2e/
   - 增加fixtures/、utils/子目录

### 保留但迁移的目录

- data/ → resources/data/
- plans/ → resources/documents/outputs/
- docs/ 保留，增加architecture/、api/、development/、deployment/子目录

### 向后兼容性

- 通过`__init__.py`重导出保持旧导入路径兼容
- 渐进式迁移，不一次性破坏现有功能

## Impact

### 受影响模块
- `src/flood_decision_agent/` - 核心代码结构重构
- `tests/` - 测试目录重组
- `web/` - Web层结构调整
- `data/`、`plans/` - 迁移至resources/
- `evaluation/` - 整合至src内

### 新增模块
- `configs/` - 集中配置
- `resources/` - 资源管理

## ADDED Requirements

### Requirement 1: 分层架构

#### Scenario 1.1: 领域层定义
- **GIVEN** 新增业务实体
- **WHEN** 需要定义领域模型
- **THEN** 文件应存放于 `domain/entities/`

#### Scenario 1.2: 应用层编排
- **GIVEN** 需要编排业务逻辑
- **WHEN** 实现用例
- **THEN** 文件应存放于 `application/use_cases/`

### Requirement 2: MCP协议层

#### Scenario 2.1: 协议类型定义
- **GIVEN** MCP需要统一类型
- **WHEN** 定义消息格式
- **THEN** 直接复用现有实现，存放于 `mcp/protocol/`

### Requirement 3: Web后端独立包

#### Scenario 3.1: 后端服务结构
- **GIVEN** Web后端需要独立运行
- **WHEN** 启动服务
- **THEN** `web/backend/` 作为独立Python包，可从src复用代码

### Requirement 4: 配置格式YAML

#### Scenario 4.1: YAML配置支持
- **GIVEN** 需要统一配置格式
- **WHEN** 加载配置
- **THEN** 优先使用YAML格式，同时兼容现有JSON配置

#### Scenario 4.2: 配置兼容性
- **GIVEN** 存在现有JSON配置
- **WHEN** 迁移配置
- **THEN** 保持向后兼容，逐步迁移至YAML

### Requirement 5: 测试目录结构

#### Scenario 5.1: 单元测试
- **GIVEN** 编写单元测试
- **WHEN** 选择测试目录
- **THEN** 存放于 `tests/unit/对应模块/`

#### Scenario 5.2: 集成测试
- **GIVEN** 编写集成测试
- **WHEN** 选择测试目录
- **THEN** 存放于 `tests/integration/对应模块/`

### Requirement 6: 向后兼容

#### Scenario 6.1: 导入兼容
- **GIVEN** 重构后的新结构
- **WHEN** 使用旧导入路径
- **THEN** 通过`__init__.py`重导出，不出现大量import错误

## MODIFIED Requirements

无

## REMOVED Requirements

无
