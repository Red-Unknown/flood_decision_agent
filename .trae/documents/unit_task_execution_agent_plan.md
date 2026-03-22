# 单元任务执行 Agent (UnitTaskExecutionAgent) 实施计划

## 1. 核心职责与边界

### 核心职责

* **节点逻辑执行**：根据上游Agent动态指定的工具列表执行节点任务，不固定绑定特定处理器。

* **数据标准化**：在调用工具/模型前后，确保数据格式符合输入输出规范。

* **动态工具执行**：接收上游Agent（NodeSchedulerAgent）动态评估后指定的工具/模型列表，按执行策略（单工具/并行/降级）调用。

* **多模型协同**：支持同时调用多个模型，并将结果汇总。

* **决策融合触发**：将多个模型的输出送入 `DecisionFusion` 模块进行加权、投票或贝叶斯融合。

### 工具分配机制

#### 策略一：上游指定（优先）
上游Agent（NodeSchedulerAgent）根据任务上下文动态评估后指定工具列表。

#### 策略二：自由选用（兜底）
本Agent维护一个**常用工具库**，当上游未指定工具或指定工具不可用时，Agent可从工具库中自主选用合适的工具。

```
┌─────────────────────┐     动态指定      ┌─────────────────────────┐
│ NodeSchedulerAgent  │ ───────────────> │ UnitTaskExecutionAgent  │
│  (上游Agent)         │   tools列表      │   (本Agent)              │
│                     │                  │                         │
│ • 工具候选集构建     │                  │ • 优先使用上游指定工具    │
│ • 适用性评估         │                  │ • 自主选用常用工具（兜底）│
│ • 执行策略生成       │                  │ • 按strategy执行         │
└─────────────────────┘                  └─────────────────────────┘
                                                  │
                                                  ▼
                                        ┌─────────────────┐
                                        │   常用工具库     │
                                        │ • 数据查询工具   │
                                        │ • 计算工具      │
                                        │ • 格式转换工具   │
                                        │ • 日志工具      │
                                        └─────────────────┘
```

**关键原则**：
1. **上游优先**：优先使用上游Agent指定的工具列表
2. **自主兜底**：上游未指定或指定失败时，从常用工具库自主选用
3. **任务匹配**：根据 `task_type` 匹配工具库中的合适工具
4. **可配置**：常用工具库通过配置文件动态加载，支持热更新

### 边界

* **不负责任务分解**：由 `DecisionChainGeneratorAgent` 负责。

* **不负责节点调度顺序**：由 `NodeSchedulerAgent` 负责。

* **不负责全局状态管理**：数据存储在 `SharedDataPool` 中，本 Agent 仅负责读写其相关的部分。

## 2. 消息格式设计

### 消息类型 (MessageType)

* `NODE_EXECUTE`: 请求执行单元任务。

* `NODE_RESULT`: 执行成功后的结果反馈。

* `ERROR`: 执行过程中发生异常的消息。

### 字段规范 (BaseMessage.payload)

* **请求消息 (NODE\_EXECUTE)**:

  * `node_id`: (str) 节点唯一标识符。
  * `task_type`: (str) 任务类型（如"hydrological_model", "reservoir_dispatch", "data_query"）。
  * `tools`: (list[dict], 可选) 上游Agent动态指定的工具/模型列表，每个元素包含：
    - `tool_name`: (str) 工具名称
    - `tool_config`: (dict) 工具配置参数
    - `priority`: (int) 执行优先级
    - *若为空或未指定，Agent将从常用工具库自主选用*
  * `execution_strategy`: (str) 执行策略（"single"/"parallel"/"fallback"/"auto"）。
    - `"auto"`: Agent根据工具数量和任务类型自动选择策略
  * `data_pool`: (SharedDataPool) 数据池引用。
  * `context`: (dict) 运行时上下文信息（如租户ID、重试次数、是否允许自主选用工具）。

* **结果消息 (NODE\_RESULT)**:

  * `status`: (str) "success" 或 "failed"。

  * `output`: (dict) 节点的计算输出。

  * `metrics`: (dict) 性能指标（耗时、内存使用等）。

### 序列化协议

* **JSON**: 使用 `BaseMessage.serialize()` 和 `deserialize()` 进行序列化。

* **复杂对象处理**: `SharedDataPool` 或 `TaskGraph` 等复杂对象在消息传递时应尽量通过引用传递，或在序列化时转换为结构化数据。

## 3. 任务状态机与生命周期管理

### 状态机 (AgentStatus)

* `INITIALIZING`: 加载处理器映射、初始化融合算法。

* `IDLE`: 等待消息。

* `BUSY`: 正在执行处理器逻辑或等待模型返回。

* `ERROR`: 捕获未处理异常。

* `STOPPED`: 释放资源并退出。

### 生命周期钩子

* `on_start`: 加载模型配置、连接外部 API。

* `before_execute`: 打印日志、校验数据池中是否存在必要的输入 Key。

* `after_execute`: 统计执行时长、清理临时文件。

* `on_error`: 记录错误日志、触发警报。

## 4. 输入输出接口规范

* **输入**:

  * `SharedDataPool`: 必须包含节点定义中 `input_keys` 指定的所有字段。

  * `Handler`: 必须遵循 `Callable[[SharedDataPool], dict[str, Any]]` 签名。

* **输出**:

  * 返回值必须为 `dict`，且 Key 需匹配节点定义中的 `output_keys`。

## 5. API Key 管理
### 5.1 核心 Key 获取策略
- **必要 Key (如 KIMI_API_KEY)**: 
  - 优先级：从环境变量获取（通过 `os.environ.get()`）
  - 环境变量设置方式：`setx KIMI_API_KEY=your_api_key`（Windows）或 `export KIMI_API_KEY=your_api_key`（Linux）
  - 缺失处理：启动时直接输出 `需要kimi_api_key` 并以退出码 1 结束

### 5.2 可选 Key 获取策略（如小模型 Key）
- **获取优先级**:
  1. 从环境变量获取
  2. 从配置文件读取
  3. 动态调用时提示用户输入（仅交互式环境）
  4. 若以上均失败，使用默认的模拟实现
- **安全机制**:
  - 所有 Key 必须加密存储在内存中
  - 禁止硬编码 Key 到代码或配置文件
  - 日志中禁止打印 Key 明文

## 6. 异常处理与重试机制
### 异常分类
- **业务异常 (BusinessError)**: 模型输入参数越界、规则校验不通过。
- **系统异常 (SystemError)**: 网络超时、内存溢出、文件读写失败。

### 重试策略
- 使用指数退避算法 (Exponential Backoff)。
- **默认配置**: 重试 3 次，初始间隔 1s，最大间隔 10s。
- **不可重试场景**: 语法错误、权限不足。

## 7. 日志记录与监控指标
### 7.1 统一日志轮转规则
- **轮转策略**: 
  - 按大小轮转：单个日志文件最大 1MB
  - 保留策略：保留最多 10 个文件
- **日志格式**:
  ```
  %(asctime)s - %(name)s - %(levelname)s - [agent_id: %(agent_id)s, message_id: %(message_id)s] - %(message)s
  ```
- **日志文件路径**:
  - 主日志：`./logs/agent.log`
  - 错误日志：`./logs/agent_error.log` (仅记录 ERROR 及以上级别)
  - 调试日志：`./logs/agent_debug.log` (仅记录 DEBUG 及以上级别)
- **配置方式**: 使用 Python logging 模块的 RotatingFileHandler 和 TimedRotatingFileHandler 实现
- **日志显示**： 主日志文件会显示所有日志，错误日志文件仅显示 ERROR 及以上级别，调试日志文件仅显示 DEBUG 及以上级别，分配不同的颜色（红色、黄色、绿色）在控制台显示。
- **日志名称**： 不同种类的agent对应不同的日志文件，文件名格式为 `agent_*.log`。


### 7.2 日志规范
- **级别**: 关键路径使用 `INFO`，调试信息使用 `DEBUG`，异常使用 `ERROR`。
- **内容**: 包含 `agent_id`, `message_id`, `handler_name`, `elapsed_time`。
- **禁止项**: 禁止打印敏感信息（如 API Key、用户数据）

### 7.3 监控指标 (Prometheus 格式)
- `agent_task_total`: 处理任务总数。
- `agent_task_duration_seconds`: 任务执行耗时分布。
- `agent_task_error_total`: 任务失败总数。
- `agent_memory_usage_bytes`: 运行时内存占用。

## 8. 单元测试用例与覆盖率要求

### 测试场景
- **正常路径**: 单处理器执行、多模型并行执行、结果正确融合。
- **异常路径**: 处理器不存在、数据池缺少输入、处理器抛出异常、融合逻辑报错。
- **边界场景**: 超大数据包处理、极端并发下的幂等性。

### 覆盖率要求
- **Line Coverage**: ≥ 90%。
- **Branch Coverage**: ≥ 85%。

## 9. 性能基准与资源限制
- **执行耗时**: 单个节点逻辑处理（不含模型计算）应控制在 50ms 以内。
- **并发能力**: 单 Agent 实例支持同时挂起 100 个异步任务。
- **内存限制**: 单实例基准内存占用 ≤ 256MB。

## 10. 版本控制与回滚策略
- **版本标识**: 使用语义化版本号 (SemVer)。
- **灰度发布**: 支持通过配置动态切换 `ExecutionStrategy` 的版本。
- **回滚**: 记录每次部署的 Git Commit Hash，支持一键切换至上一个稳定 Tag。

## 11. 里程碑与交付物验收标准

| 阶段     | 里程碑     | 交付物                             | 验收标准              |
| :----- | :------ | :------------------------------ | :---------------- |
| **M1** | 详细设计完成  | 实施计划文档 (本文件)                    | 文档内容完整，通过架构评审。    |
| **M2** | 核心框架实现  | 增强型 `UnitTaskExecutionAgent` 代码 | 支持消息驱动，集成生命周期钩子。  |
| **M3** | 功能集成与测试 | 单元测试套件 + 模拟环境运行                 | 单元测试覆盖率达标，集成测试通过。 |
| **M4** | 性能优化与交付 | 性能测试报告 + 最终代码合入                 | 满足性能基准与资源限制要求。    |

## 12. UnitTaskExecutionAgent 完整工作流

### 12.1 工作流概览

UnitTaskExecutionAgent 从建立到释放的完整生命周期包括：初始化、等待任务、执行任务、结果处理和资源释放五个主要阶段。

### 12.2 详细工作流步骤

#### 阶段 1: 初始化 (INITIALIZING)
1. **Agent 实例化**: 
   - 节点调度 Agent 创建 UnitTaskExecutionAgent 实例
   - 传入必要参数：`agent_id`, `message_bus`, `shared_data_pool`

2. **配置加载**:
   - 读取全局配置文件
   - 初始化日志系统（应用统一日志轮转规则）
   - 加载处理器映射表（`handler_name` 到实际处理函数的映射）

3. **API Key 初始化**:
   - 检查核心 Key (如 KIMI_API_KEY) 是否存在
   - 加载可选 Key（如小模型 Key）
   - 初始化 Key 管理模块

4. **决策融合模块准备**:
   - 加载融合算法配置
   - 初始化多模型协同机制

5. **状态转换**: 
   - 初始化完成后，状态从 `INITIALIZING` 转换为 `IDLE`
   - 向消息总线注册自身，开始监听 `NODE_EXECUTE` 类型的消息

#### 阶段 2: 等待任务 (IDLE)
1. **消息监听**:
   - 阻塞等待消息总线的 `NODE_EXECUTE` 消息
   - 接收到消息后，解析消息内容，提取 `handler_name`, `data_pool`, `context`

2. **前置校验**:
   - 验证消息格式是否合法
   - 检查 `handler_name` 是否在处理器映射表中
   - 调用 `before_execute` 生命周期钩子

3. **状态转换**:
   - 校验通过后，状态从 `IDLE` 转换为 `BUSY`

#### 阶段 3: 执行任务 (BUSY)
1. **解析上游指令**:
   - 从消息中提取 `task_type`、`tools` 列表和 `execution_strategy`
   - 检查 `context` 中是否允许自主选用工具（默认允许）

2. **工具选择决策**:
   - **若上游指定了 tools 列表**: 验证工具可用性，使用上游指定工具
   - **若上游未指定 tools 或验证失败**:
     - 从常用工具库中根据 `task_type` 匹配候选工具
     - 按工具优先级排序，选择最合适的工具
     - 记录工具选择原因（日志）

3. **数据准备**:
   - 从 `SharedDataPool` 中获取节点所需的输入数据
   - 对输入数据进行标准化处理，确保格式符合各工具要求

4. **API Key 动态获取**:
   - 对于可选 Key，若初始化时未获取到，尝试动态获取
   - 必要时提示用户输入（仅交互式环境）

5. **任务执行（按执行策略）**:
   - **single（单工具）**: 调用选定的单个工具执行
   - **parallel（并行多工具）**: 同时调用所有选定工具，异步等待结果
   - **fallback（降级）**: 按优先级依次尝试，成功后立即停止
   - **auto（自动）**: 
     - 若只有1个工具 → 使用 single
     - 若有多个工具且任务类型支持并行 → 使用 parallel
     - 若任务类型要求可靠性 → 使用 fallback
   - 记录每个工具的执行性能指标（耗时、内存使用等）

6. **多模型结果处理**:
   - 收集各工具的输出结果
   - 若执行策略为 parallel 或 auto选择了并行，调用决策融合模块
   - 生成最终的节点执行结果

#### 阶段 4: 结果处理
1. **结果封装**:
   - 将执行结果封装为 `NODE_RESULT` 消息格式
   - 包含：执行状态、输出数据、性能指标

2. **结果存储与反馈**:
   - 将结果写入 `SharedDataPool`，供后续节点使用
   - 向消息总线发送 `NODE_RESULT` 消息，通知节点调度 Agent
   - 调用 `after_execute` 生命周期钩子

3. **异常处理**:
   - 若执行过程中发生异常，捕获并分类
   - 记录详细错误日志
   - 调用 `on_error` 生命周期钩子
   - 发送 `ERROR` 类型消息
   - 根据重试策略决定是否重试

4. **状态转换**:
   - 任务执行完成（成功或失败）后，状态从 `BUSY` 转换为 `IDLE`

#### 阶段 5: 资源释放 (STOPPED)
1. **停止信号处理**:
   - 接收到停止信号（如系统关闭、手动停止）
   - 或达到最大运行时间/任务数量上限

2. **资源清理**:
   - 关闭模型连接和外部 API 会话
   - 释放内存中的 Key 信息
   - 清理临时文件和缓存数据
   - 关闭日志文件句柄

3. **状态转换**:
   - 状态从当前状态（`IDLE` 或 `BUSY`）转换为 `STOPPED`

4. **退出**:
   - 从消息总线注销自身
   - 释放所有持有的资源
   - 进程退出

### 12.3 工作流示例（北江洪水调度场景）

以 "北江洪水调度方案生成" 中的节点 N3（计算飞来峡入库洪水）为例：

1. **初始化阶段**:
   - 节点调度 Agent 创建 UnitTaskExecutionAgent 实例
   - 加载水文模型处理器、初始化日志系统
   - 验证 KIMI_API_KEY 存在
   - 状态转换为 `IDLE`

2. **等待任务阶段**:
   - 监听 `NODE_EXECUTE` 消息
   - 接收到节点 N3 的执行请求
   - 校验通过，状态转换为 `BUSY`

3. **执行任务阶段**:
   - 从消息中提取上游Agent动态指定的工具列表：
     ```python
     tools = [
       {"tool_name": "xin_anjiang_model", "tool_config": {"version": "v2.1"}, "priority": 1},
       {"tool_name": "api_hydrology_model", "tool_config": {"endpoint": "..."}, "priority": 2}
     ]
     execution_strategy = "parallel"
     ```
   - 从 `SharedDataPool` 获取：实时水雨情数据（节点 N1 输出）、气象预报（节点 N2 输出）
   - 按 `execution_strategy="parallel"` 同时调用两个模型
   - 收集两个模型的输出：
     - 新安江模型：计算得到入库流量过程 A
     - API 模型：计算得到入库流量过程 B
   - 决策融合模块对 A 和 B 进行加权融合，得到最终入库流量过程

4. **结果处理阶段**:
   - 将融合后的入库流量过程写入 `SharedDataPool`
   - 向节点调度 Agent 发送 `NODE_RESULT` 消息
   - 调用 `after_execute` 钩子，记录执行耗时 120ms
   - 状态转换为 `IDLE`

5. **资源释放阶段**:
   - 所有节点执行完成后，接收到停止信号
   - 关闭水文模型连接
   - 清理内存中的临时数据
   - 状态转换为 `STOPPED`
   - 退出进程

### 12.4 工作流特点

- **消息驱动**: 完全基于消息总线进行通信，解耦节点间依赖
- **异步执行**: 支持多模型并行执行，提高执行效率
- **生命周期管理**: 完整的状态机管理，确保资源正确释放
- **容错机制**: 完善的异常处理和重试策略，提高系统可靠性
- **可扩展性**: 模块化设计，支持动态添加新的处理器和融合算法

