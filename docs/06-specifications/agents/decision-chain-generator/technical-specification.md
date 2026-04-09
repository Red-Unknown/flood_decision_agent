# 决策链生成 Agent 技术规格说明书

## 1. 概述

### 1.1 设计目标
决策链生成 Agent（DecisionChainGeneratorAgent）是洪水调度决策支持系统的**入口 Agent**，负责将用户的自然语言或结构化输入转换为可执行的任务图（TaskGraph）。它是连接用户需求与系统执行的核心枢纽。

### 1.2 核心职责
- **意图理解**：解析用户输入，提取任务目标、约束条件和上下文
- **任务分解**：将复杂决策任务分解为可执行的子任务序列
- **链路优化**：生成多条备选任务链，评估可靠性并选择最优方案
- **图生成**：构建标准化的 TaskGraph，供 NodeSchedulerAgent 执行

### 1.3 架构定位
```
用户输入 → DecisionChainGeneratorAgent → TaskGraph → NodeSchedulerAgent → 执行结果
                ↑                           ↑
         IntentParser                 TaskGraphBuilder
         TaskDecomposer                    ↑
         ChainOptimizer ← TaskNodeInfo[]
```

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    DecisionChainGeneratorAgent                   │
│                         （决策链生成 Agent）                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ 意图理解模块 │→│ 任务分解模块 │→│ 链路优化模块 │→│ 图生成器 │ │
│  │IntentParser │  │TaskDecomposer│  │ChainOptimizer│  │TaskGraph │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  │ Builder │ │
│                                                      └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                        ┌──────────┐
                        │ TaskGraph │
                        │ (输出)    │
                        └──────────┘
```

### 2.2 3 阶段处理流程

```
┌────────────────────────────────────────────────────────────────────┐
│                        决策链生成流程                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   阶段 1: 意图理解        阶段 2: 任务分解        阶段 3: 链路优化   │
│   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐   │
│   │ 自然语言输入  │       │ 逆向分解      │       │ 生成备选链    │   │
│   │ 结构化输入   │────→│ 正向验证      │────→│ 可靠性评估    │   │
│   └──────────────┘       └──────────────┘       └──────────────┘   │
│          ↓                      ↓                      ↓           │
│   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐   │
│   │ TaskIntent   │       │ TaskNodeInfo │       │ 选择最优链    │   │
│   │ (目标/约束)  │       │ [] (任务节点) │       │ 迭代优化      │   │
│   └──────────────┘       └──────────────┘       └──────────────┘   │
│                                                                    │
│   阶段 4: TaskGraph 生成                                           │
│   ┌──────────────┐                                                │
│   │ 构建节点     │                                                │
│   │ 添加依赖边   │────→ TaskGraph (可执行任务图)                   │
│   │ 验证图结构   │                                                │
│   └──────────────┘                                                │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## 3. 核心组件详解

### 3.1 意图理解模块 (IntentParser)

#### 3.1.1 功能描述
将用户的自然语言输入或结构化数据解析为统一的 `TaskIntent` 对象。

#### 3.1.2 输入输出
| 类型 | 格式 | 示例 |
|------|------|------|
| 自然语言 | 字符串 | "三峡大坝需要将出库流量调整到19000立方米每秒" |
| 结构化 | JSON | `{"task_type": "flood_dispatch", "target": {"outflow": 19000}}` |
| 输出 | TaskIntent | 包含 goal, constraints, context, task_type |

#### 3.1.3 核心方法
```python
class IntentParser:
    def parse_natural_language(self, text: str) -> TaskIntent
    def parse_structured(self, data: Dict[str, Any]) -> TaskIntent
```

#### 3.1.4 模板匹配机制
```python
# 预定义模板示例
IntentTemplate(
    name="flood_dispatch",
    task_type=TaskType.FLOOD_DISPATCH,
    keywords=["洪水", "泄洪", "防洪", "出库", "流量"],
    patterns=[re.compile(r".*?(?:洪水|泄洪|防洪).*?")],
    extractors={
        "outflow": re.compile(r"(\d+(?:\.\d+)?)\s*(?:立方米每秒|m³/s)"),
        "reservoir": re.compile(r"(三峡大坝|三峡|葛洲坝)"),
    },
)
```

### 3.2 任务分解模块 (TaskDecomposer)

#### 3.2.1 功能描述
采用**逆向分解 + 正向验证**的双向策略，将高层目标分解为可执行的原子任务。

#### 3.2.2 逆向分解流程
```
最终目标: 调整出库流量到19000m³/s
    ↓
执行调度操作 (需要: 调度方案)
    ↓
计算调度方案 (需要: 来水预测, 当前状态)
    ↓
预测未来来水 (需要: 降雨数据, 上游流量)
    ↓
采集降雨数据 (无依赖)
采集上游流量 (无依赖)
获取当前水库状态 (无依赖)
```

#### 3.2.3 核心方法
```python
class TaskDecomposer:
    def decompose_backward(
        self,
        goal: str,
        task_type: TaskType,
        required_outputs: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[TaskNodeInfo]
    
    def verify_forward(self, nodes: List[TaskNodeInfo]) -> Tuple[bool, List[str]]
    
    def structure_nodes(self, nodes: List[TaskNodeInfo]) -> List[Node]
```

#### 3.2.4 分解规则库
```python
DecompositionRule(
    sub_tasks=[
        {"task_type": TaskType.EXECUTION, "description": "执行调度操作", ...},
        {"task_type": TaskType.CALCULATION, "description": "计算调度方案", ...},
        {"task_type": TaskType.DATA_COLLECTION, "description": "获取当前水库状态", ...},
        {"task_type": TaskType.PREDICTION, "description": "预测未来来水", ...},
    ]
)
```

### 3.3 链路优化模块 (ChainOptimizer)

#### 3.3.1 功能描述
生成多条备选任务链，通过可靠性评估选择最优方案，并支持迭代优化。

#### 3.3.2 优化策略
| 策略 | 描述 | 适用场景 |
|------|------|----------|
| default | 保持原始任务链 | 标准执行 |
| parallel | 并行化数据采集任务 | 提高执行效率 |
| granular | 拆分复杂计算任务 | 细粒度控制 |

#### 3.3.3 可靠性评估指标
```python
reliability_score = (
    tool_score * 0.4 +      # 工具可用性 (40%)
    dep_score * 0.4 +       # 数据依赖合理性 (40%)
    0.2 -                   # 基础分 (20%)
    len(issues) * 0.05      # 问题扣分
)
```

#### 3.3.4 瓶颈识别
- **high_degree**: 高度数节点（依赖多或被依赖多）
- **long_execution**: 长执行时间任务
- **single_point_failure**: 单点故障（关键路径无冗余）

### 3.4 TaskGraph 生成器 (TaskGraphBuilder)

#### 3.4.1 功能描述
将优化后的任务节点列表转换为标准的 TaskGraph 对象。

#### 3.4.2 构建流程
```python
def build_from_chain(self, task_chain: List[TaskChainItem]) -> TaskGraph:
    # 1. 创建所有节点
    for task in task_chain:
        node = Node(...)
        graph.add_node(node)
    
    # 2. 添加依赖边
    for task in task_chain:
        self.add_dependencies(graph, task.task_id, task.dependencies)
    
    # 3. 验证图结构
    self.validate_graph(graph)
    
    return graph
```

#### 3.4.3 节点配置生成
- **工具候选分配**: 根据 task_type 从 ToolRegistry 查找匹配工具
- **执行策略确定**: 
  - `no_handler`: 无可用工具
  - `single`: 单一工具
  - `fallback`: 多工具回退
  - `ensemble`: 关键任务集成
- **输入输出 Key 定义**: 基于任务输入输出和工具元数据

## 4. 数据模型

### 4.1 TaskIntent (意图)
```python
@dataclass
class TaskIntent:
    goal: Dict[str, Any]              # 目标参数
    constraints: Dict[str, Any]       # 约束条件
    context: Dict[str, Any]           # 上下文信息
    task_type: TaskType               # 任务类型
    raw_input: Optional[str]          # 原始输入
```

### 4.2 TaskNodeInfo (任务节点信息)
```python
@dataclass
class TaskNodeInfo:
    task_id: str                      # 任务唯一标识
    task_type: TaskType               # 任务类型
    description: str                  # 任务描述
    inputs: List[str]                 # 输入数据 key 列表
    outputs: List[str]                # 输出数据 key 列表
    dependencies: List[str]           # 依赖任务 ID 列表
    metadata: Dict[str, Any]          # 额外元数据
```

### 4.3 ChainAlternative (备选链)
```python
@dataclass
class ChainAlternative:
    chain_id: str                     # 链唯一标识
    nodes: List[TaskNodeInfo]         # 任务节点列表
    reliability_score: float          # 可靠性评分 (0-1)
    strategy: str                     # 生成策略
    metadata: Dict[str, Any]          # 额外元数据
```

### 4.4 TaskChainItem (任务链项)
```python
@dataclass
class TaskChainItem:
    task_id: str                      # 任务唯一标识
    task_type: str                    # 任务类型
    description: str                  # 任务描述
    inputs: Dict[str, Any]            # 输入参数
    outputs: List[str]                # 输出参数列表
    dependencies: List[str]           # 依赖任务 ID 列表
```

## 5. 主类设计

### 5.1 DecisionChainGeneratorAgent

#### 5.1.1 类定义
```python
class DecisionChainGeneratorAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str = "DecisionChainGenerator",
        intent_parser: Optional[IntentParser] = None,
        task_decomposer: Optional[TaskDecomposer] = None,
        chain_optimizer: Optional[ChainOptimizer] = None,
        task_graph_builder: Optional[TaskGraphBuilder] = None,
    )
```

#### 5.1.2 核心方法
```python
def generate_chain(
    self,
    user_input: str,
    input_type: str = "natural_language",
) -> Tuple[TaskGraph, Dict[str, Any]]

def _process(self, message: BaseMessage) -> BaseMessage

def generate_chain_with_alternatives(
    self,
    user_input: str,
    input_type: str = "natural_language",
    num_alternatives: int = 3,
) -> Tuple[TaskGraph, List[ChainAlternative], Dict[str, Any]]
```

#### 5.1.3 4 阶段处理流程
```python
def generate_chain(self, user_input, input_type):
    # 阶段 1: 意图理解
    intent = self._parse_intent(user_input, input_type)
    
    # 阶段 2: 任务分解
    task_nodes = self._decompose_tasks(intent)
    
    # 阶段 3: 链路优化
    optimized_nodes, reliability, log = self._optimize_chain(task_nodes)
    
    # 阶段 4: TaskGraph 生成
    task_graph = self._build_task_graph(optimized_nodes)
    
    return task_graph, metadata
```

### 5.2 DecisionPipeline

#### 5.2.1 功能描述
整合 DecisionChainGeneratorAgent 和 NodeSchedulerAgent，提供端到端的决策执行流程。

#### 5.2.2 执行流程
```python
def execute(self, user_input, input_type, data_pool):
    # 阶段 1: 生成决策链
    task_graph, metadata = self.chain_generator.generate_chain(...)
    
    # 阶段 2: 执行决策链
    if self.node_scheduler:
        execution_result = self.node_scheduler.execute_task_graph(...)
    
    return {
        "task_graph": task_graph,
        "generation_metadata": metadata,
        "execution_result": execution_result,
    }
```

## 6. 执行策略

### 6.1 策略类型
| 策略 | 描述 | 适用场景 |
|------|------|----------|
| no_handler | 无可用工具，返回空结果 | 任务类型无对应工具 |
| single | 执行单一工具 | 只有一个匹配工具 |
| fallback | 按优先级尝试多个工具 | 有多个候选工具 |
| ensemble | 并行执行多个工具并合并结果 | 关键决策任务 |
| parallel | 并行执行所有工具 | 数据采集类任务 |

### 6.2 策略选择逻辑
```python
def _determine_execution_strategy(self, task, candidates):
    if not candidates:
        return "no_handler"
    if len(candidates) == 1:
        return "single"
    if task.task_type in critical_task_types:
        return "ensemble"
    return "fallback"
```

## 7. 错误处理与重试机制

### 7.1 错误分类
- **可重试错误**: 网络超时、服务不可用
- **不可重试错误**: 参数错误、策略不支持

### 7.2 重试策略
```python
max_retries: int = 3
base_retry_delay: float = 1.0  # 秒
retry_delay = base_retry_delay * (2 ** retry_count) + random_jitter
```

## 8. 性能指标

### 8.1 时间复杂度
| 阶段 | 复杂度 | 说明 |
|------|--------|------|
| 意图理解 | O(1) | 模板匹配，常数时间 |
| 任务分解 | O(n) | n 为分解后的任务数 |
| 链路优化 | O(m*n) | m 为备选链数，n 为节点数 |
| 图生成 | O(n+e) | n 为节点数，e 为边数 |

### 8.2 可靠性评分标准
- **1.0**: 完美，无问题
- **0.8-1.0**: 优秀，轻微问题
- **0.6-0.8**: 良好，需要注意
- **0.4-0.6**: 一般，建议优化
- **<0.4**: 差，需要重构

## 9. 使用示例

### 9.1 基本使用
```python
from flood_decision_agent.agents.decision_chain_generator import DecisionChainGeneratorAgent

agent = DecisionChainGeneratorAgent()

task_graph, metadata = agent.generate_chain(
    user_input="三峡大坝需要将出库流量调整到19000立方米每秒",
    input_type="natural_language",
)

print(f"生成 {len(task_graph.get_all_nodes())} 个节点")
print(f"可靠性评分: {metadata['optimization']['reliability_score']}")
```

### 9.2 查看备选链
```python
task_graph, alternatives, metadata = agent.generate_chain_with_alternatives(
    user_input="三峡大坝需要将出库流量调整到19000立方米每秒",
    num_alternatives=3,
)

for alt in alternatives:
    print(f"{alt.chain_id}: 可靠性={alt.reliability_score:.2f}, 策略={alt.strategy}")
```

### 9.3 完整 Pipeline
```python
from flood_decision_agent.agents.decision_chain_generator import DecisionPipeline
from flood_decision_agent.agents.node_scheduler import NodeSchedulerAgent

pipeline = DecisionPipeline(
    node_scheduler=NodeSchedulerAgent()
)

result = pipeline.execute(
    user_input="三峡大坝需要将出库流量调整到19000立方米每秒",
    input_type="natural_language",
)

print(f"执行状态: {result['execution_result']['status']}")
```

## 10. 测试覆盖

### 10.1 单元测试
- IntentParser: 自然语言解析、结构化输入解析
- TaskDecomposer: 逆向分解、正向验证、节点结构化
- ChainOptimizer: 备选链生成、可靠性评估、迭代优化
- TaskGraphBuilder: 图构建、依赖添加、图验证
- DecisionChainGeneratorAgent: 完整流程、集成测试

### 10.2 集成测试
- 完整流程测试（洪水调度场景）
- 端到端测试（与 NodeSchedulerAgent 集成）

## 11. 与架构图的一致性

本实现与系统架构图 100% 一致：

| 架构图组件 | 实现文件 | 状态 |
|-----------|---------|------|
| 意图理解 | `intent_parser.py` | ✅ 已实现 |
| 任务分解 | `task_decomposer.py` | ✅ 已实现 |
| 链路优化 | `chain_optimizer.py` | ✅ 已实现 |
| TaskGraph 生成 | `task_graph_builder.py` | ✅ 已实现 |
| DecisionChainGeneratorAgent | `decision_chain_generator.py` | ✅ 已实现 |

## 12. 潜在技术风险分析

### 12.1 意图理解风险

| 风险项 | 风险等级 | 描述 | 缓解措施 |
|--------|----------|------|----------|
| 意图识别错误 | 高 | 用户输入模糊或多义导致意图解析错误 | 增加置信度阈值检查，低置信度时请求用户确认 |
| 参数提取失败 | 中 | 数值、时间等关键参数提取不完整 | 实现参数完整性校验，缺失时主动询问 |
| 方言/专业术语 | 中 | 地方水利术语或方言无法识别 | 建立水利专业词库，支持同义词映射 |
| 上下文丢失 | 低 | 多轮对话中上下文信息丢失 | 实现对话状态管理，维护上下文栈 |

### 12.2 任务分解风险

| 风险项 | 风险等级 | 描述 | 缓解措施 |
|--------|----------|------|----------|
| 分解粒度不当 | 高 | 任务过粗影响执行精度，过细增加复杂度 | 基于历史数据训练最优粒度模型 |
| 依赖关系遗漏 | 高 | 任务间隐性依赖未识别导致执行顺序错误 | 引入数据流分析，自动推导依赖 |
| 循环依赖 | 中 | 任务配置错误导致循环依赖 | 图验证阶段检测环并抛出异常 |
| 任务类型误判 | 中 | 任务类型识别错误导致工具匹配失败 | 增加任务类型校验规则 |

### 12.3 链路优化风险

| 风险项 | 风险等级 | 描述 | 缓解措施 |
|--------|----------|------|----------|
| 可靠性评估偏差 | 中 | 评分模型与实际执行效果不符 | 引入执行反馈，持续优化评分模型 |
| 优化过度 | 低 | 过度优化导致任务链不稳定 | 设置优化上限，保留原始链作为回退 |
| 计算资源消耗 | 低 | 大量备选链生成消耗过多资源 | 限制备选链数量，实现增量优化 |

### 12.4 图生成风险

| 风险项 | 风险等级 | 描述 | 缓解措施 |
|--------|----------|------|----------|
| 工具匹配失败 | 高 | 任务类型无对应工具或工具不可用 | 实现工具健康检查，动态更新工具注册表 |
| 执行策略不当 | 中 | 策略选择不当影响执行效果 | 基于任务关键性动态选择策略 |
| 输入输出不匹配 | 中 | 节点间数据格式不兼容 | 增加数据类型校验和转换机制 |

### 12.5 集成风险

| 风险项 | 风险等级 | 描述 | 缓解措施 |
|--------|----------|------|----------|
| 接口不兼容 | 中 | 与 NodeSchedulerAgent 接口变更 | 定义稳定接口契约，版本化管理 |
| 消息传递失败 | 中 | 消息队列阻塞或丢失 | 实现消息持久化和重试机制 |
| 状态同步问题 | 低 | 多 Agent 状态不一致 | 引入分布式状态管理 |

## 13. 后续优化建议

### 13.1 短期优化（1-2 个月）

#### 13.1.1 意图理解增强
- **语义理解升级**：引入大语言模型进行意图识别，提升模糊输入处理能力
- **多语言支持**：支持英文水利术语，便于国际交流
- **意图模板扩展**：增加更多调度场景模板（如生态调度、泥沙调度等）

#### 13.1.2 任务分解优化
- **智能粒度控制**：基于历史执行数据训练最优分解粒度
- **依赖自动推导**：通过数据流分析自动识别隐性依赖
- **分解规则学习**：从专家经验中自动学习分解规则

#### 13.1.3 可靠性提升
- **评分模型校准**：基于实际执行结果校准可靠性评分
- **异常检测增强**：增加更多异常模式识别
- **回退机制完善**：实现多级回退策略

### 13.2 中期优化（3-6 个月）

#### 13.2.1 性能优化
- **并行化处理**：任务分解和优化阶段并行执行
- **缓存机制**：缓存常见意图的分解结果
- **增量更新**：支持任务链的增量修改

#### 13.2.2 可观测性增强
- **链路追踪**：实现完整的决策链生成链路追踪
- **可视化界面**：开发 Web 界面展示任务图生成过程
- **性能监控**：集成 Prometheus 监控关键指标

#### 13.2.3 知识库建设
- **水利知识图谱**：构建水利领域知识图谱
- **历史案例库**：积累历史调度案例用于推荐
- **专家规则库**：整合专家经验规则

### 13.3 长期优化（6-12 个月）

#### 13.3.1 智能化升级
- **强化学习优化**：使用 RL 优化任务链选择
- **自适应调整**：根据执行反馈自动调整策略
- **预测性分析**：预测任务执行时间和资源需求

#### 13.3.2 系统扩展
- **多水库支持**：支持梯级水库联合调度
- **多场景适配**：适配防汛、抗旱、发电等多场景
- **API 开放**：提供标准 API 供第三方集成

#### 13.3.3 安全性增强
- **权限控制**：实现细粒度的权限管理
- **审计日志**：完整的操作审计追踪
- **数据加密**：敏感数据加密存储和传输

### 13.4 技术债务清理

| 债务项 | 优先级 | 处理方案 |
|--------|--------|----------|
| 日志级别统一 | 高 | 规范日志级别使用，增加结构化日志 |
| 配置集中管理 | 高 | 引入配置中心，支持动态配置 |
| 单元测试覆盖率 | 中 | 提升覆盖率至 90% 以上 |
| 文档完善 | 中 | 补充 API 文档和开发指南 |
| 代码重构 | 低 | 提取公共组件，消除重复代码 |

## 14. 附录

### A. 代码目录结构

```
f:\college\sophomore\academic\
├── .trae/
│   ├── rules/
│   │   └── project_rules.md              # 项目规则
│   └── specs/
│       ├── decision-chain-generator/     # 决策链生成 Agent 规格
│       │   ├── spec.md
│       │   ├── tasks.md
│       │   └── checklist.md
│       ├── node-scheduler/               # 节点调度 Agent 规格
│       │   └── ...
│       └── unit-task-executor/           # 单元任务执行 Agent 规格
│           └── ...
│
├── docs/                                 # 文档目录
│   ├── decision_chain_generator_specification.md   # 本文档
│   ├── node_scheduler_specification.md
│   └── unit_task_execution_specification.md
│
├── examples/                             # 示例代码
│   ├── quick_start.py                    # 快速开始
│   └── demo_decision_chain_generator.py  # 决策链生成演示
│
├── debug/                                # 调试工具
│   └── run_debug.py
│
├── scripts/                              # 脚本工具
│   ├── setup_env.ps1                     # 环境初始化
│   └── run_tests.ps1                     # 测试运行
│
├── src/                                  # 源代码
│   └── flood_decision_agent/
│       ├── __init__.py
│       ├── agents/                       # Agent 实现
│       │   ├── __init__.py
│       │   ├── base_agent.py             # Agent 基类
│       │   ├── decision_chain_generator.py   # 决策链生成 Agent
│       │   ├── node_scheduler.py         # 节点调度 Agent
│       │   └── unit_task_executor.py     # 单元任务执行 Agent
│       │
│       ├── core/                         # 核心模块
│       │   ├── __init__.py
│       │   ├── intent_parser.py          # 意图理解
│       │   ├── task_decomposer.py        # 任务分解
│       │   ├── chain_optimizer.py        # 链路优化
│       │   ├── task_graph_builder.py     # TaskGraph 生成
│       │   ├── tool_registry.py          # 工具注册表
│       │   ├── shared_data_pool.py       # 共享数据池
│       │   ├── message_bus.py            # 消息总线
│       │   ├── task_graph.py             # TaskGraph 定义
│       │   └── retry_handler.py          # 重试处理器
│       │
│       ├── tools/                        # 工具实现
│       │   ├── __init__.py
│       │   ├── base_tool.py              # 工具基类
│       │   ├── data_collection_tools.py  # 数据采集工具
│       │   ├── prediction_tools.py       # 预测工具
│       │   ├── calculation_tools.py      # 计算工具
│       │   ├── decision_tools.py         # 决策工具
│       │   └── execution_tools.py        # 执行工具
│       │
│       ├── utils/                        # 工具函数
│       │   ├── __init__.py
│       │   ├── logger.py                 # 日志工具
│       │   └── config.py                 # 配置管理
│       │
│       └── models/                       # 数据模型
│           ├── __init__.py
│           ├── intent_models.py          # 意图相关模型
│           ├── task_models.py            # 任务相关模型
│           └── chain_models.py           # 链路相关模型
│
├── tests/                                # 测试目录
│   ├── run_tests.py                      # 统一测试入口
│   ├── test_decision_chain_generator.py  # 决策链生成测试
│   ├── test_intent_parser.py
│   ├── test_task_decomposer.py
│   ├── test_chain_optimizer.py
│   └── test_task_graph_builder.py
│
├── requirements.txt                      # Python 依赖
├── environment.yml                       # Conda 环境配置
├── README.md                             # 项目说明
└── .pre-commit-config.yaml               # 代码提交前检查配置
```

### B. 配置文件说明

#### B.1 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `KIMI_API_KEY` | Kimi API 密钥 | 是 |
| `LOG_LEVEL` | 日志级别 (DEBUG/INFO/WARNING/ERROR) | 否，默认 INFO |
| `MAX_RETRY_COUNT` | 最大重试次数 | 否，默认 3 |
| `RELIABILITY_THRESHOLD` | 可靠性阈值 | 否，默认 0.6 |

#### B.2 关键配置项

```python
# config.py 关键配置
CONFIG = {
    "intent_parser": {
        "confidence_threshold": 0.8,
        "max_template_matches": 5,
    },
    "task_decomposer": {
        "max_decomposition_depth": 10,
        "enable_forward_verify": True,
    },
    "chain_optimizer": {
        "max_alternatives": 5,
        "reliability_threshold": 0.6,
        "enable_iterative_optimize": True,
    },
    "task_graph_builder": {
        "enable_cycle_detection": True,
        "enable_dead_node_elimination": True,
    },
}
```

### C. 术语表

| 术语 | 英文 | 说明 |
|------|------|------|
| 决策链 | Decision Chain | 从意图到执行的任务序列 |
| 任务图 | TaskGraph | 有向无环图形式的任务结构 |
| 意图 | Intent | 用户输入的语义表示 |
| 任务节点 | TaskNode | 任务图中的单个执行单元 |
| 链路优化 | Chain Optimization | 生成和选择最优任务链的过程 |
| 可靠性评分 | Reliability Score | 评估任务链可靠性的量化指标 |
| 执行策略 | Execution Strategy | 节点执行时的工具选择和调用方式 |
| 逆向分解 | Backward Decomposition | 从目标反向推导所需任务的方法 |
| 正向验证 | Forward Verification | 从输入正向验证任务链完整性的方法 |

### D. 参考资料

1. **系统设计文档**
   - 系统架构图
   - Agent 交互流程图
   - 数据流图

2. **API 文档**
   - Kimi API 文档
   - 工具注册接口
   - 消息总线接口

3. **相关论文**
   - 多 Agent 系统架构设计
   - 任务分解算法研究
   - 可靠性评估模型

## 15. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-03-21 | 初始版本，完成 3 阶段决策链生成流程 |
| 1.1 | 2026-03-21 | 补充技术风险分析、优化建议和附录 |
