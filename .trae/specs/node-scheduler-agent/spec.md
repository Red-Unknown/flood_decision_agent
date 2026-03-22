# 节点调度Agent (NodeSchedulerAgent) 设计规范

## Why

节点调度Agent是防汛调度智能决策系统的核心路由组件，负责协调任务图中各节点的执行顺序、管理节点间依赖关系、动态选择工具并生成执行策略。它是连接决策链生成Agent和单元任务执行Agent的关键桥梁，确保任务按照正确的依赖顺序高效执行。

## What Changes

- 新增 NodeSchedulerAgent 类，实现5步调度流程
- 新增 TaskGraph 任务图数据结构
- 新增 Node 节点定义（包含依赖、工具候选、执行策略等）
- 新增工具候选集构建算法
- 新增执行策略生成器
- 集成 UnitTaskExecutionAgent 作为节点执行代理

## Impact

- 新增模块: `src/flood_decision_agent/agents/node_scheduler.py`
- 新增模块: `src/flood_decision_agent/core/task_graph.py`
- 影响: UnitTaskExecutionAgent 作为下游执行器
- 影响: 决策链生成Agent 作为上游输入源

## ADDED Requirements

### Requirement: 节点依赖关系检查
The system SHALL 在节点执行前检查所有前置依赖是否已完成。

#### Scenario: 依赖已满足
- **GIVEN** 节点A依赖节点B和节点C
- **WHEN** 节点B和节点C都已标记为完成状态
- **THEN** 节点A可以开始执行

#### Scenario: 依赖未满足
- **GIVEN** 节点A依赖节点B和节点C
- **WHEN** 节点B已完成但节点C未完成
- **THEN** 节点A进入等待状态，记录等待原因

### Requirement: 前置节点结果获取
The system SHALL 从共享数据池中获取前置节点的执行结果。

#### Scenario: 成功获取结果
- **GIVEN** 前置节点已完成并产生输出
- **WHEN** 当前节点开始执行
- **THEN** 自动从SharedDataPool获取所需输入数据

#### Scenario: 结果缺失
- **GIVEN** 前置节点标记完成但输出数据缺失
- **WHEN** 尝试获取输入数据
- **THEN** 抛出异常并记录错误日志

### Requirement: 工具候选集构建
The system SHALL 根据节点任务类型动态构建可用工具候选集。

#### Scenario: 构建工具候选集
- **GIVEN** 节点任务类型为"hydrological_model"
- **WHEN** 执行工具候选集构建步骤
- **THEN** 返回该任务类型支持的所有工具列表，包含工具元数据

#### Scenario: 评估工具适用性
- **GIVEN** 多个工具候选
- **WHEN** 评估工具适用性
- **THEN** 根据历史成功率、响应时间、资源占用等指标排序

### Requirement: 执行策略生成
The system SHALL 根据节点特性和资源情况生成执行策略。

#### Scenario: 单工具执行
- **GIVEN** 只有一个合适的工具
- **WHEN** 生成执行策略
- **THEN** 返回"single"策略

#### Scenario: 多工具并行
- **GIVEN** 多个工具候选且任务类型支持并行
- **WHEN** 生成执行策略
- **THEN** 返回"parallel"策略，包含工具列表

#### Scenario: 降级策略
- **GIVEN** 任务要求高可靠性
- **WHEN** 生成执行策略
- **THEN** 返回"fallback"策略，按优先级依次尝试

### Requirement: 节点执行代理
The system SHALL 调用 UnitTaskExecutionAgent 执行节点任务。

#### Scenario: 成功执行
- **GIVEN** 节点依赖已满足、工具已选择、策略已生成
- **WHEN** 调用节点执行代理
- **THEN** 创建 UnitTaskExecutionAgent 实例，发送 NODE_EXECUTE 消息
- **AND** 等待执行完成，获取结果

#### Scenario: 执行失败重试
- **GIVEN** 节点执行失败
- **WHEN** 错误类型为可重试错误
- **THEN** 按指数退避算法重试，最多3次

### Requirement: 任务图遍历执行
The system SHALL 按照拓扑顺序遍历执行任务图中的所有节点。

#### Scenario: 顺序执行
- **GIVEN** 任务图包含节点N1→N2→N3的依赖链
- **WHEN** 开始执行任务图
- **THEN** 按N1→N2→N3顺序依次执行

#### Scenario: 并行执行
- **GIVEN** 任务图中N2和N3都依赖N1，但彼此无依赖
- **WHEN** N1完成后
- **THEN** N2和N3可以并行执行

## MODIFIED Requirements

### Requirement: NodeSchedulerAgent 与 UnitTaskExecutionAgent 集成
**原有**: NodeSchedulerAgent 直接调用 handler 函数
**修改**: NodeSchedulerAgent 通过消息调用 UnitTaskExecutionAgent
**原因**: 解耦调度与执行，支持分布式部署

## REMOVED Requirements

无
