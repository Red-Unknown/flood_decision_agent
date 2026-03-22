# 决策链生成Agent 开发任务列表

## Task 1: 设计意图理解模块
- [x] 创建 IntentParser 类
  - [x] 实现 parse_natural_language() 方法解析自然语言
  - [x] 实现 parse_structured() 方法解析结构化输入
  - [x] 定义 TaskIntent 数据类（目标、约束、上下文）
- [x] 实现基于规则的意图解析（模板匹配）
  - [x] 定义常见任务模板（洪水调度、干旱调度、常规调度）
  - [x] 实现关键词提取
  - [x] 实现目标数值解析（如"19000 m³/s"）
- [x] 实现简单的NLP解析（可选）
  - [x] 集成基础NLP库或API
  - [x] 实现实体识别（地点、时间、数值）

## Task 2: 实现任务分解模块
- [x] 创建 TaskDecomposer 类
  - [x] 实现 decompose_backward() 逆向分解方法
  - [x] 实现 verify_forward() 正向验证方法
  - [x] 实现 structure_nodes() 节点结构化方法
- [x] 定义任务分解规则库
  - [x] 定义常见任务分解模式
  - [x] 定义任务类型到子任务的映射
  - [x] 定义输入输出依赖关系
- [x] 实现逆向任务分解
  - [x] 从最终目标反向推导子任务
  - [x] 识别任务间的数据依赖
  - [x] 构建初步任务链
- [x] 实现正向过程验证
  - [x] 验证任务可行性
  - [x] 检查输入输出匹配
  - [x] 调整任务顺序

## Task 3: 实现链路优化模块
- [x] 创建 ChainOptimizer 类
  - [x] 实现 generate_alternatives() 生成备选链
  - [x]  evaluate_reliability() 评估可靠性
  - [x] 实现 optimize_iteratively() 迭代优化
- [x] 实现多次任务链生成
  - [x] 使用不同分解策略生成多条链
  - [x] 使用不同工具选择生成多条链
- [x] 实现链路可靠性评估
  - [x] 检查循环依赖
  - [x] 评估工具可用性
  - [x] 评估数据依赖合理性
  - [x] 计算可靠性评分
- [x] 实现多轮迭代优化
  - [x] 识别瓶颈节点
  - [x] 调整任务分解粒度
  - [x] 优化节点执行顺序

## Task 4: 实现 TaskGraph 生成器
- [x] 创建 TaskGraphBuilder 类
  - [x] 实现 build_from_chain() 从任务链构建图
  - [x] 实现 add_dependencies() 添加依赖边
  - [x] 实现 validate_graph() 验证图结构
- [x] 实现节点详细配置生成
  - [x] 为每个节点分配工具候选
  - [x] 为每个节点确定执行策略
  - [x] 为每个节点定义输入输出key

## Task 5: 实现 DecisionChainGeneratorAgent 主类
- [x] 创建 DecisionChainGeneratorAgent 类
  - [x] 集成 IntentParser
  - [x] 集成 TaskDecomposer
  - [x] 集成 ChainOptimizer
  - [x] 集成 TaskGraphBuilder
- [x] 实现 generate_chain() 主方法
  - [x] 调用意图理解
  - [x] 调用任务分解
  - [x] 调用链路优化
  - [x] 调用图生成
  - [x] 返回 TaskGraph
- [x] 实现 execute() 方法（继承BaseAgent）
  - [x] 解析输入消息
  - [x] 调用 generate_chain()
  - [x] 返回生成的 TaskGraph

## Task 6: 集成 NodeSchedulerAgent
- [x] 实现端到端流程
  - [x] DecisionChainGeneratorAgent 生成 TaskGraph
  - [x] 自动传递给 NodeSchedulerAgent
  - [x] NodeSchedulerAgent 执行 TaskGraph
- [x] 实现 Pipeline 类整合两个Agent
  - [x] 顺序调用两个Agent
  - [x] 传递 SharedDataPool
  - [x] 返回最终执行结果

## Task 7: 编写单元测试
- [x] 测试 IntentParser
  - [x] 自然语言解析测试
  - [x] 结构化输入解析测试
- [x] 测试 TaskDecomposer
  - [x] 逆向分解测试
  - [x] 正向验证测试
- [x] 测试 ChainOptimizer
  - [x] 备选链生成测试
  - [x] 可靠性评估测试
- [x] 测试 TaskGraphBuilder
  - [x] 图构建测试
  - [x] 依赖添加测试
- [x] 测试 DecisionChainGeneratorAgent
  - [x] 完整流程测试
  - [x] 集成测试

## Task 8: 编写演示脚本
- [x] 创建演示脚本
  - [x] 自然语言输入示例
  - [x] 展示意图理解结果
  - [x] 展示任务分解过程
  - [x] 展示链路优化结果
  - [x] 展示生成的 TaskGraph
  - [x] 展示完整执行流程

# 任务依赖关系

```
Task 1 (意图理解)
    │
    ├──► Task 2 (任务分解)
    │       │
    │       └──► Task 3 (链路优化)
    │               │
    │               └──► Task 4 (图生成)
    │                       │
    │                       └──► Task 5 (主类实现)
    │                               │
    │                               └──► Task 6 (集成)
    │                                       │
    │                                       └──► Task 7 (单元测试)
    │                                               │
    │                                               └──► Task 8 (演示脚本)
    │
    └──► Task 2-4 可并行开发基础组件
```

# 并行开发建议

- **可并行**: Task 1/2/3/4 可以并行开发基础模块
- **必须串行**: Task 5 依赖 Task 1-4
- **必须串行**: Task 6 依赖 Task 5 和 NodeSchedulerAgent
- **必须串行**: Task 7/8 依赖 Task 6
