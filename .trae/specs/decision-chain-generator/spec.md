# 决策链生成Agent (DecisionChainGeneratorAgent) 设计规范

## Why

决策链生成Agent是防汛调度智能决策系统的入口组件，负责将高层任务描述转化为可执行的任务图。它是整个系统的"大脑"，通过意图理解、任务分解和链路优化，将复杂的防汛调度任务分解为一系列相互依赖的单元任务，为后续的节点调度Agent提供执行蓝图。

## What Changes

- 新增 DecisionChainGeneratorAgent 类，实现3阶段处理流程
- 新增意图理解模块（NLP解析或规则模板）
- 新增任务分解模块（逆向分解+正向验证）
- 新增链路优化模块（可靠性评估+迭代优化）
- 新增 TaskGraph 生成器
- 集成 NodeSchedulerAgent 作为下游执行器

## Impact

- 新增模块: `src/flood_decision_agent/agents/decision_chain_generator.py`
- 新增模块: `src/flood_decision_agent/core/intent_parser.py`
- 新增模块: `src/flood_decision_agent/core/task_decomposer.py`
- 新增模块: `src/flood_decision_agent/core/chain_optimizer.py`
- 影响: NodeSchedulerAgent 作为下游执行器
- 影响: 系统入口从直接创建TaskGraph改为通过自然语言描述生成

## ADDED Requirements

### Requirement: 意图理解
The system SHALL 解析用户输入的任务描述，提取任务目标和约束条件。

#### Scenario: 自然语言输入
- **GIVEN** 用户输入"北江发生超标准洪水，需要生成调度方案，目标是将石角洪峰降至19000 m³/s以下"
- **WHEN** 执行意图理解
- **THEN** 解析出目标"石角洪峰≤19000"，约束"超标准洪水"

#### Scenario: 结构化输入
- **GIVEN** 用户输入包含目标、约束、时间范围的JSON
- **WHEN** 执行意图理解
- **THEN** 直接提取结构化信息，无需NLP解析

### Requirement: 任务分解
The system SHALL 将高层任务分解为相互依赖的单元任务。

#### Scenario: 逆向任务分解
- **GIVEN** 最终目标"输出调度方案"
- **WHEN** 执行逆向分解
- **THEN** 识别出需要：计算水位流量、评估淹没风险、检查规则符合性、优化多目标等子任务

#### Scenario: 正向过程验证
- **GIVEN** 初步任务序列
- **WHEN** 执行正向验证
- **THEN** 验证任务可行性，调整任务顺序，确保输入输出匹配

#### Scenario: 节点结构化输出
- **GIVEN** 分解后的子任务
- **WHEN** 执行节点结构化
- **THEN** 每个子任务定义为节点，明确任务类型、输入、输出、所需工具

### Requirement: 链路优化
The system SHALL 对生成的任务链进行优化，提高可靠性。

#### Scenario: 多次任务链生成
- **GIVEN** 同一任务
- **WHEN** 执行多次分解
- **THEN** 产生多条备选任务链（不同分解粒度或替代路径）

#### Scenario: 链路可靠性评估
- **GIVEN** 生成的任务链
- **WHEN** 执行可靠性评估
- **THEN** 检查循环依赖、工具可用性、数据依赖合理性

#### Scenario: 多轮迭代优化
- **GIVEN** 初始任务链
- **WHEN** 执行迭代优化
- **THEN** 通过模拟执行或专家反馈，调整任务分解结构，优化节点顺序

### Requirement: 任务执行有向图生成
The system SHALL 生成最终的任务执行有向图。

#### Scenario: 生成TaskGraph
- **GIVEN** 优化后的任务链
- **WHEN** 执行图生成
- **THEN** 生成TaskGraph，节点=单元任务，边=依赖关系

#### Scenario: 输出可执行方案
- **GIVEN** TaskGraph
- **WHEN** 执行方案生成
- **THEN** 输出包含每个节点的详细配置（工具、参数、数据需求）

## MODIFIED Requirements

### Requirement: 系统入口
**原有**: 直接创建TaskGraph并传递给NodeSchedulerAgent
**修改**: 通过自然语言描述或结构化输入，由DecisionChainGeneratorAgent生成TaskGraph
**原因**: 降低用户使用门槛，支持自然语言交互

## REMOVED Requirements

无
