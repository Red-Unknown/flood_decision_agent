# 工具定义文档

## 概述

本文档描述 flood_decision_agent 系统中可用的工具定义和使用方法。

工具分为两类：
1. **执行工具** - 用于处理具体的业务任务
2. **LLM 工具** - 用于与 LLM 交互的官方工具和自定义工具

---

## 执行工具

执行工具位于 `src/flood_decision_agent/tools/execution_tools.py`，为每种执行类型提供具体的实现。

### 工具注册

```python
from flood_decision_agent.tools.execution_tools import register_execution_tools
from flood_decision_agent.tools.registry import ToolRegistry

# 创建注册表
registry = ToolRegistry()

# 注册所有执行工具
register_execution_tools(registry)
```

### 工具列表

#### 1. data_collection - 数据采集

**描述**: 采集实时水情、雨情、气象等数据

**支持任务类型**: `data_collection`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| station | str | 否 | 站点名称，默认"未知站点" |
| data_type | str | 否 | 数据类型，可选：水位、流量、降雨，默认"水位" |

**输出示例**:
```json
{
  "station": "宜昌站",
  "data_type": "水位",
  "value": 145.32,
  "unit": "米",
  "timestamp": "2024-07-15 08:00:00",
  "status": "正常"
}
```

---

#### 2. data_processing - 数据处理

**描述**: 处理和分析原始数据

**支持任务类型**: `data_processing`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| process_type | str | 否 | 处理类型，可选：统计分析、趋势分析，默认"统计分析" |

**输出示例**:
```json
{
  "process_type": "统计分析",
  "result": {
    "mean": 148.5,
    "max": 155.2,
    "min": 142.1,
    "count": 24
  },
  "status": "完成"
}
```

---

#### 3. prediction - 预测预报

**描述**: 进行洪水、降雨、流量等预测预报

**支持任务类型**: `prediction`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| forecast_type | str | 否 | 预报类型，可选：水位预报、流量预报，默认"水位预报" |
| horizon | str | 否 | 预报时段，默认"24小时" |

**输出示例**:
```json
{
  "forecast_type": "水位预报",
  "horizon": "24小时",
  "predictions": [
    {"time": "+4小时", "value": 146.5, "unit": "米"},
    {"time": "+8小时", "value": 147.2, "unit": "米"},
    {"time": "+12小时", "value": 147.8, "unit": "米"},
    {"time": "+16小时", "value": 148.1, "unit": "米"},
    {"time": "+20小时", "value": 147.9, "unit": "米"},
    {"time": "+24小时", "value": 147.5, "unit": "米"}
  ],
  "confidence": 0.85,
  "status": "完成"
}
```

---

#### 4. calculation - 计算分析

**描述**: 进行水文水力计算分析

**支持任务类型**: `calculation`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| calc_type | str | 否 | 计算类型，可选：洪水频率分析、调洪演算，默认"洪水频率分析" |

**输出示例**:
```json
{
  "calc_type": "洪水频率分析",
  "result": {
    "p_50": 142.5,
    "p_20": 147.3,
    "p_10": 152.1,
    "p_5": 157.8,
    "p_1": 165.2
  },
  "status": "完成"
}
```

---

#### 5. simulation - 模拟仿真

**描述**: 进行洪水演进、调度方案等模拟仿真

**支持任务类型**: `simulation`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sim_type | str | 否 | 仿真类型，可选：洪水演进、调度方案仿真，默认"洪水演进" |

**输出示例**:
```json
{
  "sim_type": "洪水演进",
  "result": {
    "peak_time": "+36小时",
    "peak_flow": 45000,
    "affected_area": 520,
    "evacuation_needed": true
  },
  "status": "完成"
}
```

---

#### 6. optimization - 优化计算

**描述**: 进行水库调度优化计算

**支持任务类型**: `optimization`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| opt_type | str | 否 | 优化类型，默认"水库群联合优化" |

**输出示例**:
```json
{
  "opt_type": "水库群联合优化",
  "result": {
    "optimal_outflows": {
      "三峡": 20000,
      "葛洲坝": 15000,
      "丹江口": 12000
    },
    "target_levels": {
      "三峡": 165.5,
      "葛洲坝": 64.2,
      "丹江口": 162.8
    },
    "benefit": {
      "flood_control": 0.88,
      "power_generation": 0.82,
      "navigation": 0.90
    }
  },
  "convergence": true,
  "iterations": 128,
  "status": "完成"
}
```

---

#### 7. decision - 决策生成

**描述**: 生成调度决策方案

**支持任务类型**: `decision`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| decision_type | str | 否 | 决策类型，可选：调度决策、预警决策，默认"调度决策" |

**输出示例**:
```json
{
  "decision_type": "调度决策",
  "result": {
    "decision": "加大出库",
    "target_outflow": 25000,
    "reason": "基于当前水情和预报结果，为平衡防洪安全和发电效益",
    "urgency": "中"
  },
  "status": "完成"
}
```

---

#### 8. execution - 执行操作

**描述**: 执行具体的调度操作

**支持任务类型**: `execution`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| action | str | 否 | 操作类型，默认"调整出库流量" |
| target | str | 否 | 目标对象，默认"三峡大坝" |
| value | float | 否 | 目标值，默认随机生成 |

**输出示例**:
```json
{
  "action": "调整出库流量",
  "result": {
    "action": "调整出库流量",
    "target": "三峡大坝",
    "value": 22000,
    "unit": "立方米每秒",
    "executed": true,
    "execution_time": "2024-07-15 08:30:00",
    "operator": "系统自动"
  },
  "status": "执行成功"
}
```

---

#### 9. verification - 验证检查

**描述**: 验证方案的可行性和安全性

**支持任务类型**: `verification`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| check_type | str | 否 | 检查类型，默认"方案可行性检查" |

**输出示例**:
```json
{
  "check_type": "方案可行性检查",
  "checks": [
    {"item": "防洪安全", "passed": true, "score": 0.92},
    {"item": "发电效益", "passed": true, "score": 0.85},
    {"item": "航运保障", "passed": true, "score": 0.88},
    {"item": "生态影响", "passed": true, "score": 0.82}
  ],
  "all_passed": true,
  "overall_score": 0.87,
  "status": "通过"
}
```

---

#### 10. reporting - 报告生成

**描述**: 生成分析报告和决策建议

**支持任务类型**: `reporting`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| report_type | str | 否 | 报告类型，默认"调度分析报告" |

**输出示例**:
```json
{
  "report_type": "调度分析报告",
  "report": {
    "title": "调度分析报告",
    "summary": "本次调度方案综合考虑了防洪、发电、航运等多方面因素，总体效果良好。",
    "key_findings": [
      "水位控制在安全范围内",
      "出库流量满足下游防洪要求",
      "发电效益达到预期的92%"
    ],
    "recommendations": [
      "继续加强水情监测",
      "根据预报及时调整调度方案",
      "做好应急准备工作"
    ],
    "generated_at": "2024-07-15 09:00:00"
  },
  "status": "完成"
}
```

---

#### 11. universal_query - 通用查询

**描述**: 使用LLM直接回答通用问题，支持流式输出。不局限于水利调度领域，可以回答任何类型的问题。

**支持任务类型**: `universal_query`

**输入参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| question | str | 否 | 用户问题，如未提供则从数据池获取 |
| task_context | dict | 否 | 任务上下文信息 |

**输出示例**:
```json
{
  "answer": "河海大学是中国一所以水利为特色的全国重点大学...",
  "question": "河海大学怎么样？",
  "source": "llm_direct",
  "status": "完成",
  "task_type": "general"
}
```

**特点**:
- 支持流式输出，实时显示AI回答
- 自动从数据池获取用户原始输入
- 可处理水利专业问题和通用知识问题
- 使用Kimi API进行智能问答

---

## LLM 工具

LLM 工具位于 `src/flood_decision_agent/tools/llm_tools.py`，支持与 LLM 交互的官方工具和自定义工具。

### 基础类

#### BaseTool

所有工具的基类。

```python
class BaseTool(ABC):
    def __init__(self, name: str, description: str)
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]
    
    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> ToolResult
```

#### FunctionTool

自定义 Function 工具，兼容 OpenAI API。

```python
class FunctionTool(BaseTool):
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
    )
```

#### OfficialTool

Kimi 官方工具基类，通过 formula URI 调用。

```python
class OfficialTool(BaseTool):
    def __init__(self, name: str, description: str, formula_uri: str)
```

### 官方工具

#### WebSearchTool

**Formula URI**: `moonshot/web-search:latest`

**描述**: 搜索互联网获取实时信息

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| query | str | 是 | 搜索关键词 |

### 工具管理器

```python
from flood_decision_agent.tools.llm_tools import LLMToolManager, create_default_tool_manager
from openai import OpenAI

# 创建客户端
client = OpenAI(api_key="your_key", base_url="https://api.moonshot.cn/v1")

# 创建工具管理器
tool_manager = create_default_tool_manager(client)

# 带工具的对话
messages = [
    {"role": "system", "content": "你是一个助手"},
    {"role": "user", "content": "搜索今天的天气"},
]

response = tool_manager.chat_with_tools(messages)
```

---

## 工具注册表

工具注册表位于 `src/flood_decision_agent/tools/registry.py`。

### ToolMetadata

```python
@dataclass
class ToolMetadata:
    name: str                          # 工具名称
    description: str                   # 工具描述
    task_types: Set[str]              # 支持的任务类型
    priority: int = 100               # 优先级
    config_schema: Dict[str, Any]     # 配置参数 schema
    required_keys: Set[str]           # 需要的输入数据 key
    output_keys: Set[str]             # 输出的数据 key
```

### 使用示例

```python
from flood_decision_agent.tools.registry import ToolRegistry, ToolMetadata

# 创建注册表
registry = ToolRegistry()

# 定义工具处理器
def my_handler(data_pool, config):
    return {"result": "success"}

# 注册工具
registry.register(
    name="my_tool",
    handler=my_handler,
    metadata=ToolMetadata(
        name="my_tool",
        description="我的工具",
        task_types={"my_task_type"},
    ),
)

# 执行工具
result = registry.execute("my_tool", data_pool, {"param": "value"})
```

---

## 扩展工具

### 添加新的执行工具

1. 在 `execution_tools.py` 中添加处理器函数
2. 在 `register_execution_tools()` 中注册工具

示例:

```python
def _my_new_tool_handler(data_pool: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """我的新工具处理器"""
    return {
        "result": "success",
        "data": {...},
    }

# 在 register_execution_tools 中添加
registry.register(
    name="my_new_tool",
    handler=_my_new_tool_handler,
    metadata=ToolMetadata(
        name="my_new_tool",
        description="我的新工具",
        task_types={"my_task_type"},
    ),
)
```

### 添加新的 LLM 工具

1. 继承 `BaseTool` 或 `OfficialTool`
2. 实现 `get_tool_definition()` 和 `execute()`
3. 注册到 `ToolRegistry`

示例:

```python
class MyTool(BaseTool):
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {...},
            },
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        # 执行逻辑
        return ToolResult(success=True, output={...})
```
