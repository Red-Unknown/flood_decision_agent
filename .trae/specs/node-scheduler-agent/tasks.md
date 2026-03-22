# 节点调度Agent 开发任务列表

## Task 1: 设计 TaskGraph 和 Node 数据结构
- [x] 创建 TaskGraph 类，支持有向图表示
  - [x] 实现 add_node() 方法添加节点
  - [x] 实现 add_edge() 方法添加依赖关系
  - [x] 实现 topological_sort() 拓扑排序
  - [x] 实现 get_ready_nodes() 获取可执行节点
- [x] 创建 Node 类定义节点属性
  - [x] node_id: 节点唯一标识
  - [x] task_type: 任务类型
  - [x] dependencies: 依赖节点列表
  - [x] status: 节点状态 (PENDING/READY/RUNNING/COMPLETED/FAILED)
  - [x] tool_candidates: 工具候选集
  - [x] execution_strategy: 执行策略
  - [x] output_keys: 输出数据key列表

## Task 2: 实现节点依赖关系检查
- [x] 实现 check_dependencies() 方法
  - [x] 检查所有前置节点是否已完成
  - [x] 返回依赖满足状态和缺失依赖列表
- [x] 实现依赖等待机制
  - [x] 记录节点等待原因
  - [x] 支持超时检测

## Task 3: 实现前置节点结果获取
- [x] 实现 fetch_predecessor_results() 方法
  - [x] 从 SharedDataPool 获取前置节点输出
  - [x] 验证所需数据是否完整
  - [x] 处理数据缺失异常情况

## Task 4: 实现工具候选集构建
- [x] 实现 build_tool_candidates() 方法
  - [x] 根据 task_type 查询 ToolRegistry
  - [x] 返回可用工具列表
- [x] 实现工具适用性评估
  - [x] 根据历史成功率排序
  - [x] 根据响应时间排序
  - [x] 综合评分算法

## Task 5: 实现执行策略生成
- [x] 实现 generate_execution_strategy() 方法
  - [x] 根据工具数量选择策略
  - [x] 根据任务类型选择策略
  - [x] 返回策略配置对象
- [x] 支持策略: single/parallel/fallback/auto

## Task 6: 实现节点执行代理
- [x] 集成 UnitTaskExecutionAgent
  - [x] 创建执行器实例
  - [x] 构建 NODE_EXECUTE 消息
  - [x] 发送消息并等待结果
- [x] 实现执行结果处理
  - [x] 更新节点状态
  - [x] 存储结果到 SharedDataPool
  - [x] 记录执行日志

## Task 7: 实现任务图遍历执行
- [x] 实现 execute_task_graph() 主方法
  - [x] 拓扑排序获取执行顺序
  - [x] 循环执行可执行节点
  - [x] 处理并行执行
- [x] 实现执行状态管理
  - [x] 跟踪所有节点状态
  - [x] 检测执行完成或失败
  - [x] 支持执行取消

## Task 8: 实现重试机制
- [x] 实现重试逻辑
  - [x] 识别可重试错误
  - [x] 指数退避算法
  - [x] 最大重试次数限制
- [x] 实现失败处理
  - [x] 记录失败原因
  - [x] 触发告警

## Task 9: 编写单元测试
- [x] 测试 TaskGraph 功能
  - [x] 拓扑排序测试
  - [x] 依赖检测测试
- [x] 测试 NodeSchedulerAgent 功能
  - [x] 单节点执行测试
  - [x] 多节点依赖执行测试
  - [x] 工具候选集构建测试
  - [x] 执行策略生成测试
- [x] 测试集成场景
  - [x] 与 UnitTaskExecutionAgent 集成测试

## Task 10: 编写演示脚本
- [x] 创建演示脚本
  - [x] 构建示例任务图
  - [x] 展示执行过程
  - [x] 输出执行结果

# 任务依赖关系

```
Task 1 (数据结构)
    │
    ├──► Task 2 (依赖检查)
    │       │
    │       └──► Task 3 (结果获取)
    │               │
    │               └──► Task 6 (执行代理)
    │                       │
    │                       └──► Task 7 (遍历执行)
    │
    ├──► Task 4 (工具候选集)
    │       │
    │       └──► Task 5 (执行策略)
    │               │
    │               └──► Task 6 (执行代理)
    │
    └──► Task 8 (重试机制)
            │
            └──► Task 6 (执行代理)

Task 7 (遍历执行) ──► Task 9 (单元测试)
                         │
                         └──► Task 10 (演示脚本)
```

# 并行开发建议

- **可并行**: Task 2/3 与 Task 4/5 可以并行开发
- **可并行**: Task 8 可以与 Task 2-5 并行开发
- **必须串行**: Task 6 依赖 Task 2-5
- **必须串行**: Task 7 依赖 Task 6
- **必须串行**: Task 9/10 依赖 Task 7
