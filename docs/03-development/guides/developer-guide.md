# Plan/Spec 模式开发者指南

## 概述

本文档为开发者提供 Plan/Spec 模式增强功能的开发指南，包括架构设计、核心组件说明和扩展方法。

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户输入层                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ 模式识别器   │    │ 断点接续    │    │ 取消处理器   │     │
│  │ ModeDetector│    │ Checkpoint  │    │ CancelHandler│     │
│  └──────┬──────┘    └─────────────┘    └─────────────┘     │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              决策链生成器 (DecisionChainGenerator)    │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐      │   │
│  │  │ 普通模式  │    │ Plan模式  │    │ Spec模式  │      │   │
│  │  │ Simple   │    │ Plan     │    │ Spec     │      │   │
│  │  └──────────┘    └──────────┘    └──────────┘      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     链路优化层                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │SimpleOptimizer│   │PlanOptimizer│    │ChainOptimizer│    │
│  │  (轻量级)    │    │ (中等优化)  │    │ (完整优化)   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 模式识别器 (ModeDetector)

**文件**: `src/flood_decision_agent/agents/decision_chain/mode_detector.py`

**职责**: 自动判断用户输入的问题复杂度，推荐合适的处理模式。

**使用示例**:

```python
from flood_decision_agent.agents.decision_chain import ModeDetector

# 创建识别器
detector = ModeDetector()

# 检测模式
mode = detector.detect("设计一个洪水预警系统")
print(mode)  # 输出: "plan"

# 获取详细指标
metrics = detector.get_metrics()
print(metrics)
```

**扩展方法**:

```python
# 自定义阈值
class CustomModeDetector(ModeDetector):
    def __init__(self):
        super().__init__()
        self.thresholds = {
            "simple": 30,   # 更严格
            "plan": 150,
        }

# 添加新的复杂度指标
def detect(self, user_input: str) -> str:
    # 添加自定义逻辑
    if self._has_specific_keyword(user_input):
        return "spec"
    return super().detect(user_input)
```

### 2. 断点接续 Agent (CheckpointResumptionAgent)

**文件**: `src/flood_decision_agent/agents/decision_chain/checkpoint_agent.py`

**职责**: 保存和恢复任务状态，处理各种中断场景。

**使用示例**:

```python
from flood_decision_agent.agents.decision_chain import CheckpointResumptionAgent

# 创建 Agent
agent = CheckpointResumptionAgent()

# 保存断点
checkpoint = agent.save_checkpoint(
    session_id="session_123",
    state={
        "mode": "plan",
        "stage": "generating",
        "plan_id": "plan_001",
    },
    reason="manual_cancel"
)

# 恢复断点
state = agent.resume_checkpoint("session_123")
```

**存储扩展**:

```python
# 自定义存储后端
from flood_decision_agent.agents.decision_chain.checkpoint_agent import CheckpointStorage

class RedisCheckpointStorage(CheckpointStorage):
    def __init__(self, redis_client):
        self.redis = redis_client

    def save(self, checkpoint_id: str, data: dict):
        self.redis.setex(
            f"checkpoint:{checkpoint_id}",
            3600,  # TTL
            json.dumps(data)
        )

    def load(self, checkpoint_id: str) -> dict:
        data = self.redis.get(f"checkpoint:{checkpoint_id}")
        return json.loads(data) if data else None
```

### 3. 取消处理器 (CancelHandler)

**文件**: `src/flood_decision_agent/agents/decision_chain/cancel_handler.py`

**职责**: 处理用户取消命令，支持模式切换和需求修改。

**使用示例**:

```python
from flood_decision_agent.agents.decision_chain import CancelHandler

handler = CancelHandler()

# 识别取消命令
if handler.is_cancel_command("取消当前任务"):
    result = handler.handle_cancel(
        session_id="session_123",
        current_state={"mode": "plan"},
        reason="user_request"
    )

# 模式切换
new_state = handler.switch_mode(
    session_id="session_123",
    from_mode="plan",
    to_mode="simple"
)

# 解析修改指令
modification = handler.parse_modification(
    "把目标改成提升准确率到98%"
)
print(modification)
# 输出: {"type": "change", "target": "目标", "new_value": "提升准确率到98%"}
```

### 4. 链路优化器

**文件**: `src/flood_decision_agent/agents/decision_chain/unified_optimizer.py`

#### SimpleOptimizer（轻量级）


**特点**:
- 1个备用链路
- 可靠性阈值: 0.6
- 无迭代优化

**使用场景**: 普通模式，快速响应

#### PlanOptimizer（中等优化）

**特点**:
- 2-3个备选方案
- 可靠性阈值: 0.75
- 2次迭代优化

**使用场景**: Plan 模式，平衡质量和速度

#### SpecOptimizer（详细优化）

**特点**:
- 4-6个备选方案
- 可靠性阈值: 0.85
- 3次迭代优化

**使用场景**: Spec 模式，确保功能完善


## 常见问题

### Q: 如何添加新的取消命令？

A: 在 `CancelHandler` 中添加：

```python
CANCEL_KEYWORDS = [
    "取消", "停止", "abort", "cancel",
    "换个思路", "重新开始", "重来",
    "换个方式", "重新来",  # 新增
]
```

### Q: 如何修改模式识别阈值？

A: 在配置文件中修改：

```yaml
# configs/app.yaml
mode_detector:
  thresholds:
    simple: 50    # 修改此值
    plan: 200     # 修改此值
```

### Q: 如何扩展断点存储？

A: 实现 `CheckpointStorage` 接口：

```python
class MyStorage(CheckpointStorage):
    def save(self, checkpoint_id: str, data: dict):
        # 实现保存逻辑
        pass

    def load(self, checkpoint_id: str) -> dict:
        # 实现加载逻辑
        pass
```

然后在初始化时使用：

```python
agent = CheckpointResumptionAgent(storage=MyStorage())
```


