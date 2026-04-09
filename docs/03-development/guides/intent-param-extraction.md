# 意图解析与参数提取问题

## 问题描述

当用户查询"查询金坛天气"时，系统应该：
1. 解析用户意图 → 获取天气信息
2. 提取参数 → 城市="金坛"
3. 调用 rainfall 工具时传递参数 → `get_current_rainfall(city="金坛")`

但实际上：
- 系统成功调用了 `get_current_rainfall` 工具
- **但没有传递城市参数**，导致使用默认参数 "北京"

## 问题根因分析

### 当前流程

```
用户查询: "查询金坛天气"
        ↓
意图解析: 识别为 weather_forecast 任务
        ↓
选择工具: get_current_rainfall, get_hourly_rainfall
        ↓
调用工具: (没有传递 city 参数!)
        ↓
MCP Server 使用默认参数: city="北京"
```

### 问题位置

在 `src/flood_decision_agent/agents/task_executor/executor.py` 中：

```python
def _select_tools(self, tools_spec, task_type, context, use_mcp=False):
    """选择工具"""
    # ... 省略 ...

    # 查找 MCP 工具
    mcp_tools = self._find_mcp_tools_for_task(task_type, context)
    
    # 问题在这里：只选择了工具，没有提取和传递参数
    # 应该从用户查询或 context 中提取参数（如 city）
    # 并将这些参数传递给 MCP 工具
```

### 期望的流程

```
用户查询: "查询金坛天气"
        ↓
意图解析 (IntentParser): 
  - 识别任务类型: weather_forecast
  - 提取实体: 城市="金坛"
  - 生成结构化输出: {task_type: "weather_forecast", entities: {city: "金坛"}}
        ↓
任务分解: weather_forecast_000 节点
        ↓
工具选择: 
  - 选择工具: get_current_rainfall, get_hourly_rainfall
  - **传递参数**: {city: "金坛"}
        ↓
MCP 工具调用:
  - get_current_rainfall(city="金坛") ✓
  - get_hourly_rainfall(city="金坛") ✓
```

## 解决方案

### 方案 1: 在 TaskExecutor 中提取参数（推荐）

在 `_select_tools` 方法中添加参数提取逻辑：

```python
def _select_tools(self, tools_spec, task_type, context, use_mcp=False):
    """选择工具"""
    # ... 现有逻辑 ...

    # 新增: 从 context 中提取参数
    extracted_params = self._extract_params_from_context(context)
    
    # 为 MCP 工具注入参数
    for tool in mcp_tools:
        tool["arguments"] = extracted_params  # 注入参数
    
    return selected_tools

def _extract_params_from_context(self, context: Dict) -> Dict:
    """从 context 中提取参数"""
    params = {}
    
    # 从 user_query 中提取
    user_query = context.get("user_query", "")
    if "金坛" in user_query:
        params["city"] = "金坛"
    elif "常州" in user_query:
        params["city"] = "常州"
    # ... 更多城市映射
    
    # 从 entities 中提取（如果意图解析已提取）
    entities = context.get("entities", {})
    if "city" in entities:
        params["city"] = entities["city"]
    
    return params
```

### 方案 2: 在意图解析时提取实体

在 `DecisionChainGeneratorAgent` 中增强意图解析：

```python
def _parse_intent(self, user_message: str) -> Dict[str, Any]:
    """解析用户意图 - 增强版"""
    # ... 现有 LLM 调用 ...
    
    # 提取实体
    entities = self._extract_entities(user_message)
    
    return {
        "task_type": task_type,
        "entities": entities,  # 新增: 实体信息
        "original_query": user_message,
    }

def _extract_entities(self, text: str) -> Dict[str, Any]:
    """提取实体信息"""
    entities = {}
    
    # 城市实体
    cities = ["金坛", "常州", "北京", "上海", "南京"]
    for city in cities:
        if city in text:
            entities["city"] = city
            break
    
    # 时间实体
    # ... 
    
    return entities
```

### 方案 3: 使用工具 schema 自动提取参数

定义工具的参数 schema，让系统自动从用户查询中提取：

```python
# rainfall_server.py
TOOL_SCHEMAS = {
    "get_current_rainfall": {
        "parameters": {
            "city": {
                "type": "string",
                "description": "城市名称",
                "examples": ["金坛", "常州", "北京"]
            }
        }
    }
}

# 参数提取器
def extract_params_for_tool(tool_name: str, user_query: str) -> Dict:
    schema = TOOL_SCHEMAS.get(tool_name, {})
    params = {}
    
    for param_name, param_info in schema.get("parameters", {}).items():
        examples = param_info.get("examples", [])
        for example in examples:
            if example in user_query:
                params[param_name] = example
    
    return params
```

## 实现建议

### 优先级

1. **方案 1（推荐）**：在 TaskExecutor 中添加参数提取
   - 改动最小
   - 可以在现有架构下快速实现
   - 不影响意图解析模块

2. **方案 2**：增强意图解析
   - 更完整的解决方案
   - 需要修改 DecisionChainGeneratorAgent
   - 可以提取更多类型实体

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `executor.py` | 添加 `_extract_params_from_context` 方法 |
| `generator.py` | 可选：增强 `_parse_intent` 提取实体 |

## 测试用例

```python
# 测试参数提取
def test_extract_city_param():
    executor = UnitTaskExecutor()
    
    # 测试用例
    test_cases = [
        ("查询金坛天气", {"city": "金坛"}),
        ("查询常州天气", {"city": "常州"}),
        ("北京天气怎么样", {"city": "北京"}),
        ("看看上海的天气", {"city": "上海"}),
    ]
    
    for query, expected in test_cases:
        context = {"user_query": query}
        params = executor._extract_params_from_context(context)
        assert params == expected, f"Failed for: {query}"
```

## 相关文件

- `src/flood_decision_agent/agents/task_executor/executor.py` - 任务执行器
- `src/flood_decision_agent/agents/decision_chain/generator.py` - 决策链生成器
- `src/flood_decision_agent/agents/intent_parser/` - 意图解析器
- `configs/mcp/servers.yaml` - MCP 服务配置
