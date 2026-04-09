### REST API

本文档提供水利智脑 Web 服务的完整 API 接口规范。所有 API 均基于 HTTP/REST 协议，数据格式为 JSON。

**重要变更说明（v2.0.0）**:
- **决策链执行完全迁移到 WebSocket**：Plan/Spec 确认接口改为通过 WebSocket 流式返回完整执行流程
- **复用现有 WebSocket 连接**：复用 `WS /ws/chat/{conversation_id}` 连接
- **移除状态检查、执行接口**：获取执行状态改为一次调用，后端 yield 状态而不是轮询
- **暂停、取消、恢复标记为后续扩展**

**基础信息**

- **Base URL**: `http://localhost:8000`
- **协议**: HTTP/1.1 或 HTTP/2
- **字符编码**: UTF-8
- **Content-Type**: `application/json`

***

## 通用规范

### 请求格式

所有 POST/PUT/PATCH 请求的请求体必须为 JSON 格式，并设置请求头：

```http
Content-Type: application/json
```

### 响应格式

#### 成功响应

```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

#### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": { ... }
  }
}
```

### HTTP 状态码

| 状态码 | 说明      |
| --- | ------- |
| 200 | 请求成功    |
| 201 | 创建成功    |
| 400 | 请求参数错误  |
| 404 | 资源不存在   |
| 500 | 服务器内部错误 |

***

## 基础接口

### 健康检查

检查服务运行状态。

```http
GET /api/health
```

**请求参数**: 无

**响应示例**:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "水利智脑 Web服务"
}
```

**错误响应**:

- `500`: 服务异常

***

## 对话管理 API

### 获取对话列表

获取所有对话列表，按更新时间倒序排列。

```http
GET /api/conversations
```

**请求参数**: 无

**响应示例**:

```json
[
  {
    "id": "conv_123456",
    "title": "洪水预警系统咨询",
    "created_at": 1704067200.0,
    "updated_at": 1704153600.0,
    "message_count": 5
  }
]
```

**字段说明**:

| 字段             | 类型      | 说明             |
| -------------- | ------- | -------------- |
| id             | string  | 对话唯一标识         |
| title          | string  | 对话标题           |
| created\_at    | number  | 创建时间戳（Unix时间戳） |
| updated\_at    | number  | 更新时间戳（Unix时间戳） |
| message\_count | integer | 消息数量           |

***

### 创建新对话

创建一个新的对话会话。

```http
POST /api/conversations
```

**请求体**:

```json
{
  "title": "可选的自定义标题"
}
```

**字段说明**:

| 字段    | 类型     | 必填  | 说明           |
| ----- | ------ | --- | ------------ |
| title | string | 否   | 对话标题，不传则自动生成 |

**响应示例**:

```json
{
  "id": "conv_789012",
  "title": "新对话 3",
  "created_at": 1704153600.0,
  "updated_at": 1704153600.0,
  "message_count": 0
}
```

**错误响应**:

- `500`: 创建失败

***

### 获取对话详情

获取指定对话的详细信息。

```http
GET /api/conversations/{conversation_id}
```

**路径参数**:

| 参数               | 类型     | 必填  | 说明   |
| ---------------- | ------ | --- | ---- |
| conversation\_id | string | 是   | 对话ID |

**响应示例**:

```json
{
  "id": "conv_123456",
  "title": "洪水预警系统咨询",
  "created_at": 1704067200.0,
  "updated_at": 1704153600.0,
  "message_count": 5
}
```

**错误响应**:

- `404`: 对话不存在

```json
{
  "detail": "对话不存在"
}
```

***

### 删除对话

删除指定的对话及其所有消息。

```http
DELETE /api/conversations/{conversation_id}
```

**路径参数**:

| 参数               | 类型     | 必填  | 说明   |
| ---------------- | ------ | --- | ---- |
| conversation\_id | string | 是   | 对话ID |

**响应示例**:

```json
{
  "success": true,
  "message": "对话已删除"
}
```

**错误响应**:

- `404`: 对话不存在

***

### 获取对话消息历史

获取指定对话的所有消息。

```http
GET /api/conversations/{conversation_id}/messages
```

**路径参数**:

| 参数               | 类型     | 必填  | 说明   |
| ---------------- | ------ | --- | ---- |
| conversation\_id | string | 是   | 对话ID |

**响应示例**:

```json
[
  {
    "role": "user",
    "content": "设计一个洪水预警系统",
    "timestamp": 1704153600.0
  },
  {
    "role": "assistant",
    "content": "## 任务分析\n\n**用户输入**: 设计一个洪水预警系统...",
    "timestamp": 1704153660.0
  }
]
```

**字段说明**:

| 字段        | 类型     | 说明                        |
| --------- | ------ | ------------------------- |
| role      | string | 消息角色：`user` 或 `assistant` |
| content   | string | 消息内容                      |
| timestamp | number | 消息时间戳                     |

***

### 获取对话过程事件

获取对话执行过程中的详细事件记录（用于展示执行流程）。

```http
GET /api/conversations/{conversation_id}/process-events
```

**路径参数**:

| 参数               | 类型     | 必填  | 说明   |
| ---------------- | ------ | --- | ---- |
| conversation\_id | string | 是   | 对话ID |

**响应示例**:

```json
[
  {
    "stage": "task_accepted",
    "timestamp": 1704153600.0,
    "data": {
      "message": "📋 任务分析",
      "user_input": "设计一个洪水预警系统",
      "task_type": "natural_language"
    }
  },
  {
    "stage": "task_list_generated",
    "timestamp": 1704153601.0,
    "data": {
      "message": "📋 决策链任务列表",
      "tasks": [
        {
          "task_id": "task_1",
          "task_name": "需求分析",
          "task_type": "analysis",
          "dependencies": [],
          "status": "pending"
        }
      ],
      "total_count": 1
    }
  },
  {
    "stage": "node_started",
    "timestamp": 1704153602.0,
    "data": {
      "message": "▶️ 开始执行任务: 需求分析",
      "node_id": "task_1",
      "agent_id": "analysis_agent",
      "task_name": "需求分析"
    }
  },
  {
    "stage": "node_completed",
    "timestamp": 1704153605.0,
    "data": {
      "message": "✅ 任务完成: 需求分析",
      "node_id": "task_1",
      "agent_id": "analysis_agent",
      "duration_ms": 3000,
      "output_summary": "完成需求分析"
    }
  }
]
```

**事件类型说明**:

| stage                 | 说明       |
| --------------------- | -------- |
| task\_accepted        | 任务已接收    |
| task\_list\_generated | 任务列表已生成  |
| node\_started         | 节点开始执行   |
| node\_completed       | 节点执行完成   |
| node\_failed          | 节点执行失败   |
| agent\_called         | Agent被调用 |
| pipeline\_completed   | 流程执行完成   |

***

### 清空对话消息

清空指定对话的所有消息和过程事件。

```http
POST /api/conversations/{conversation_id}/clear
```

**路径参数**:

| 参数               | 类型     | 必填  | 说明   |
| ---------------- | ------ | --- | ---- |
| conversation\_id | string | 是   | 对话ID |

**响应示例**:

```json
{
  "success": true,
  "message": "对话已清空"
}
```

***

## 聊天 API

### 发送消息

发送消息并获取 AI 回复。支持流式和非流式两种模式。

```http
POST /api/chat
```

**请求体**:

```json
{
  "message": "设计一个洪水预警系统",
  "conversation_id": "conv_123456",
  "stream": true
}
```

**字段说明**:

| 字段               | 类型      | 必填  | 说明               |
| ---------------- | ------- | --- | ---------------- |
| message          | string  | 是   | 用户消息内容           |
| conversation\_id | string  | 否   | 对话ID，不传则创建新对话    |
| stream           | boolean | 否   | 是否流式返回，默认 `true` |

#### 流式响应（SSE）

当 `stream: true` 时，返回 Server-Sent Events 流：

```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**事件类型**:

1. **用户消息确认**:

```
data: {"type": "user_message", "content": "设计一个洪水预警系统", "conversation_id": "conv_123456"}
```

1. **过程事件**:

```
data: {"type": "process_event", "stage": "task_accepted", "data": {...}, "timestamp": 1704153600.0}
```

1. **内容块**:

```
data: {"type": "chunk", "content": "## 任务分析\n", "accumulated": "## 任务分析\n"}
```

1. **完成事件**:

```
data: {"type": "complete", "content": "完整的回复内容...", "conversation_id": "conv_123456"}
```

1. **错误事件**:

```
data: {"type": "error", "content": "处理出错: 错误详情"}
```

#### 非流式响应

当 `stream: false` 时，返回完整响应：

```json
{
  "content": "## 任务分析\n\n**用户输入**: 设计一个洪水预警系统...",
  "conversation_id": "conv_123456"
}
```

**错误响应**:

- `500`: 处理出错

```json
{
  "detail": "处理出错: 具体错误信息"
}
```

***

## 模式识别 API

### 检测问题复杂度模式

分析用户输入，推荐合适的处理模式。

```http
POST /api/mode/detect
```

**触发时机**: 用户点击发送或按 Enter 发送时。如果模式识别 API 返回的推荐结果与用户选择的不同，弹窗给出原因并询问用户是否采用推荐模式。

**请求体**:

```json
{
  "user_input": "设计一个洪水预警系统"
}
```

**字段说明**:

| 字段          | 类型     | 必填  | 说明     |
| ----------- | ------ | --- | ------ |
| user\_input | string | 是   | 用户输入文本 |

**响应示例**:

```json
{
  "recommended_mode": "plan",
  "confidence": 0.85,
  "metrics": {
    "trigger": "keyword",
    "plan_score": 3,
    "spec_score": 1,
    "length_score": 0.6
  }
}
```

**字段说明**:

| 字段                | 类型     | 说明                              |
| ----------------- | ------ | ------------------------------- |
| recommended\_mode | string | 推荐模式：`simple` / `plan` / `spec` |
| confidence        | number | 置信度，范围 0-1                      |
| metrics           | object | 检测指标详情                          |

**模式说明**:

| 模式     | 说明   | 触发条件                 |
| ------ | ---- | -------------------- |
| simple | 简单模式 | 默认模式，适用于一般问答         |
| plan   | 规划模式 | 包含"计划"、"规划"、"方案"等关键词 |
| spec   | 规格模式 | 包含"规格"、"规范"、"需求"等关键词 |

**特殊命令**:

- `/plan` - 强制使用规划模式
- `/spec` - 强制使用规格模式

**错误响应**:

- `500`: 模式检测失败

```json
{
  "detail": "模式检测失败: 错误详情"
}
```

***

## 数据获取服务 API

数据获取服务提供多模态数据解析、确认、请求等功能。

### 解析输入数据

解析自然语言、表格、文件等多种输入格式。

```http
POST /data/parse
```

**请求体**:

```json
{
  "input_data": "河道断面数据...",
  "input_type": "text",
  "schema_type": "river_cross_section"
}
```

**字段说明**:

| 字段           | 类型     | 必填  | 说明                                            |
| ------------ | ------ | --- | --------------------------------------------- |
| input\_data  | string | 是   | 输入数据内容                                        |
| input\_type  | string | 否   | 输入类型：`text` / `csv` / `tsv` / `excel`，不传则自动检测 |
| schema\_type | string | 否   | Schema类型，默认 `river_cross_section`             |

**支持的 Schema 类型**:

| 类型                     | 说明     |
| ---------------------- | ------ |
| river\_cross\_section  | 河道断面数据 |
| roughness\_coefficient | 糙率系数数据 |

**响应示例**:

```json
{
  "success": true,
  "parsed_data": {
    "river_name": "示例河道",
    "section_points": [...]
  },
  "confidence": 0.92,
  "missing_fields": [],
  "warnings": [],
  "source": "text"
}
```

**字段说明**:

| 字段              | 类型      | 说明     |
| --------------- | ------- | ------ |
| success         | boolean | 解析是否成功 |
| parsed\_data    | object  | 解析后的数据 |
| confidence      | number  | 解析置信度  |
| missing\_fields | array   | 缺失字段列表 |
| warnings        | array   | 警告信息列表 |
| source          | string  | 输入类型来源 |

**错误响应**:

- `400`: 未知的 schema 类型
- `500`: 解析失败

***

### 确认数据

提交数据确认结果（确认、修改或拒绝）。

```http
POST /data/confirm
```

**请求体**:

```json
{
  "confirmation_id": "conf_123456",
  "status": "confirmed",
  "modified_data": null,
  "user_notes": ""
}
```

**字段说明**:

| 字段               | 类型     | 必填  | 说明                                         |
| ---------------- | ------ | --- | ------------------------------------------ |
| confirmation\_id | string | 是   | 确认ID                                       |
| status           | string | 是   | 确认状态：`confirmed` / `rejected` / `modified` |
| modified\_data   | object | 否   | 修改后的数据（status为modified时必填）                 |
| user\_notes      | string | 否   | 用户备注                                       |

**响应示例**:

```json
{
  "success": true,
  "data_key": "river_section_001",
  "stored_value": { ... },
  "message": "数据已确认"
}
```

**错误响应**:

- `500`: 确认失败

***

### 请求特定数据

请求特定数据，系统返回数据值及默认值建议。

```http
POST /data/request
```

**请求体**:

```json
{
  "data_key": "roughness_coefficient",
  "description": "河道糙率系数",
  "required": true,
  "context": {
    "river_type": "山区河道"
  }
}
```

**字段说明**:

| 字段          | 类型      | 必填  | 说明               |
| ----------- | ------- | --- | ---------------- |
| data\_key   | string  | 是   | 数据键名             |
| description | string  | 否   | 数据描述             |
| required    | boolean | 否   | 是否必需，默认 `true`   |
| context     | object  | 否   | 上下文信息，用于获取更准确的建议 |

**响应示例**:

```json
{
  "value": 0.035,
  "source": "default",
  "confidence": 0.85,
  "suggestions": [
    {
      "value": 0.035,
      "source_type": "standard",
      "description": "山区河道默认糙率",
      "confidence": 0.85
    },
    {
      "value": 0.04,
      "source_type": "historical",
      "description": "历史数据平均值",
      "confidence": 0.75
    }
  ]
}
```

**字段说明**:

| 字段          | 类型     | 说明      |
| ----------- | ------ | ------- |
| value       | any    | 数据值     |
| source      | string | 数据来源    |
| confidence  | number | 置信度     |
| suggestions | array  | 默认值建议列表 |

**建议项字段说明**:

| 字段           | 类型     | 说明     |
| ------------ | ------ | ------ |
| value        | any    | 建议值    |
| source\_type | string | 建议来源类型 |
| description  | string | 建议描述   |
| confidence   | number | 建议置信度  |

**错误响应**:

- `500`: 请求数据失败

***

### 获取默认值选项

根据数据键名和条件返回默认值建议列表。

```http
GET /data/defaults
```

**查询参数**:

| 参数         | 类型     | 必填  | 说明        |
| ---------- | ------ | --- | --------- |
| data\_key  | string | 是   | 数据键名      |
| conditions | string | 否   | 条件JSON字符串 |

**响应示例**:

```json
{
  "suggestions": [
    {
      "value": 0.035,
      "source_type": "standard",
      "description": "山区河道默认糙率",
      "confidence": 0.85,
      "source_reference": "《水文手册》第3章"
    }
  ]
}
```

**错误响应**:

- `500`: 获取默认值失败

***

### 获取数据血缘

获取数据的完整获取路径和历史记录。

```http
GET /data/lineage/{data_key}
```

**路径参数**:

| 参数        | 类型     | 必填  | 说明   |
| --------- | ------ | --- | ---- |
| data\_key | string | 是   | 数据键名 |

**响应示例**:

```json
{
  "data_key": "roughness_coefficient_001",
  "acquisition_path": [
    {
      "step": 1,
      "source": "user_input",
      "timestamp": "2026-03-26T10:00:00Z"
    },
    {
      "step": 2,
      "source": "confirmation",
      "timestamp": "2026-03-26T10:05:00Z"
    }
  ],
  "history": [
    {
      "record_id": "rec_001",
      "timestamp": "2026-03-26T10:00:00Z",
      "source": "user_input"
    }
  ]
}
```

**错误响应**:

- `500`: 获取数据血缘失败

***

### 创建澄清会话

创建数据澄清会话，用于执行中数据请求的管理。

```http
POST /data/clarification/session
```

**请求体**:

```json
{
  "task_id": "task_123456",
  "data_dependencies": [
    {
      "data_key": "river_width",
      "description": "河道宽度",
      "required": true
    }
  ]
}
```

**字段说明**:

| 字段                 | 类型     | 必填  | 说明     |
| ------------------ | ------ | --- | ------ |
| task\_id           | string | 是   | 任务ID   |
| data\_dependencies | array  | 否   | 数据依赖列表 |

**数据依赖项字段说明**:

| 字段          | 类型      | 必填  | 说明   |
| ----------- | ------- | --- | ---- |
| data\_key   | string  | 是   | 数据键名 |
| description | string  | 否   | 数据描述 |
| required    | boolean | 否   | 是否必需 |

**响应示例**:

```json
{
  "session_id": "session_789012",
  "pending_requests": [
    {
      "request_id": "req_001",
      "data_key": "river_width",
      "description": "河道宽度",
      "request_type": "required"
    }
  ]
}
```

**错误响应**:

- `500`: 创建会话失败

***

### 解决数据请求

解决数据澄清会话中的数据请求。

```http
POST /data/clarification/resolve
```

**请求体**:

```json
{
  "session_id": "session_789012",
  "request_id": "req_001",
  "resolution_type": "user_input",
  "value": 100.5
}
```

**字段说明**:

| 字段               | 类型     | 必填  | 说明                                      |
| ---------------- | ------ | --- | --------------------------------------- |
| session\_id      | string | 是   | 会话ID                                    |
| request\_id      | string | 是   | 请求ID                                    |
| resolution\_type | string | 是   | 解决类型：`default` / `user_input` / `skip`  |
| value            | any    | 否   | 用户提供的值（resolution\_type为user\_input时必填） |

**解决类型说明**:

| 类型          | 说明          |
| ----------- | ----------- |
| default     | 使用系统推荐的默认值  |
| user\_input | 使用用户提供的自定义值 |
| skip        | 跳过此数据请求     |

**响应示例**:

```json
{
  "success": true,
  "can_resume": true,
  "message": "数据请求已解决，可以继续执行"
}
```

**字段说明**:

| 字段          | 类型      | 说明                 |
| ----------- | ------- | ------------------ |
| success     | boolean | 是否成功解决             |
| can\_resume | boolean | 是否可以恢复执行（所有请求都已解决） |
| message     | string  | 提示消息               |

**错误响应**:

- `400`: 未知的解决类型
- `500`: 解决请求失败

***

### 上传文件并解析

上传 CSV 或 Excel 文件并解析。

```http
POST /data/upload
Content-Type: multipart/form-data
```

**请求参数**:

| 参数           | 类型     | 必填  | 说明                                |
| ------------ | ------ | --- | --------------------------------- |
| file         | file   | 是   | 文件（支持 .csv, .xlsx, .xls）          |
| schema\_type | string | 否   | Schema类型，默认 `river_cross_section` |

**响应示例**:

```json
{
  "success": true,
  "parsed_data": { ... },
  "filename": "river_data.csv"
}
```

**错误响应**:

- `400`: 不支持的文件格式
- `500`: 文件解析失败

***

## WebSocket API

WebSocket 提供实时双向通信，支持流式消息传输。

### 聊天 WebSocket

```
WS /ws/chat/{conversation_id}
```

**路径参数**:

| 参数               | 类型     | 必填  | 说明   |
| ---------------- | ------ | --- | ---- |
| conversation\_id | string | 是   | 对话ID |

**客户端消息格式**:

1. **发送消息**:

```json
{
  "type": "message",
  "content": "用户消息内容"
}
```

1. **心跳检测**:

```json
{
  "type": "ping"
}
```

1. **打字状态**:

```json
{
  "type": "typing",
  "is_typing": true
}
```

**服务端消息格式**:

1. **连接成功**:

```json
{
  "type": "connected",
  "conversation_id": "conv_123456",
  "timestamp": 1704153600.0
}
```

1. **用户消息确认**:

```json
{
  "type": "user_message",
  "content": "用户消息内容",
  "timestamp": 1704153600.0
}
```

1. **开始标记**:

```json
{
  "type": "start",
  "timestamp": 1704153600.0
}
```

1. **内容块（流式）**:

```json
{
  "type": "chunk",
  "content": "内容片段",
  "accumulated": "累计内容",
  "timestamp": 1704153600.0
}
```

1. **完成标记**:

```json
{
  "type": "complete",
  "content": "完整回复内容",
  "timestamp": 1704153600.0
}
```

1. **文档生成块（Plan/Spec模式）**:

```json
{
  "type": "document_chunk",
  "document_id": "plan_abc123",
  "content": "生成的内容片段",
  "accumulated": "累计生成的内容",
  "progress": 0.45,
  "timestamp": 1704153600.0
}
```

1. **文档生成完成（Plan/Spec模式）**:

```json
{
  "type": "document_complete",
  "document_id": "plan_abc123",
  "content": "完整文档内容",
  "document_type": "plan",
  "files": {
    "spec": {
      "title": "规格说明",
      "content": "spec.md 内容"
    },
    "tasks": {
      "title": "任务列表",
      "content": "tasks.md 内容"
    },
    "checklist": {
      "title": "检查清单",
      "content": "checklist.md 内容"
    }
  },
  "timestamp": 1704153600.0
}
```

1. **心跳响应**:

```json
{
  "type": "pong",
  "timestamp": 1704153600.0
}
```

1. **错误消息**:

```json
{
  "type": "error",
  "content": "错误信息",
  "timestamp": 1704153600.0
}
```

***

## 架构设计规范

### 通信协议

**WebSocket 统一通信**

所有实时通信统一使用 WebSocket，按对话维度建立连接：

```
WS /ws/chat/{conversation_id}
```

**设计决策**:

- 每个对话一个独立的 WebSocket 连接
- 消息按功能类型区分格式
- 替代原有的 SSE 流式返回

### 文档生成策略

**LLM 流式生成**

- 后端通过 LLM 生成完整文档内容
- 通过 WebSocket 流式返回生成过程
- 不规定具体文档格式，由 LLM 自由生成

### 任务执行策略

**状态钩子 + 实时推送**

```
执行流程:
1. 拓扑排序任务（DAG依赖）
2. 逐个执行任务（带1次自动重试）
3. 每完成一个任务 → WebSocket推送状态更新
4. 失败任务标记为failed，继续执行独立任务
5. 最终返回：成功任务结果 + 失败任务详情
```

**任务状态持久化**

- 存储方式：文件存储（JSON格式）
- 存储路径：`data/sessions/{session_id}/`
- 历史记录：暂时保留所有记录（管理方式待扩展）

### Plan/Spec 交互流程

```
用户输入需求
    ↓
LLM生成完整文档 → WebSocket流式返回
    ↓
用户操作（三选一）:
  ├─ 直接编辑文档内容 → 保存 → 确认
  ├─ 自然语言指令修改 → LLM全量重新生成 → 流式返回
  └─ 确认文档 → 进入执行阶段
    ↓
执行决策链任务
```

**设计要点**:

- 不支持按章节生成，一次性生成完整文档
- 自然语言修改时全量重新生成（非增量修改）
- 文档只保留当前版本（不保留历史版本）
- 不存在多用户协作场景

***

## Plan 模式 API

Plan 模式用于处理中等复杂度的规划类任务，生成结构化的项目规划文档。

### 数据模型

#### PlanDocument 规划文档

```json
{
  "plan_id": "plan_abc123",
  "conversation_id": "conv_abc123",
  "title": "水库调度规划",
  "content": "# 水库调度规划\n\n## 概述\n...",
  "sections": [
    {
      "name": "概述",
      "content": "项目背景...",
      "editable": true
    },
    {
      "name": "目标",
      "content": "- 目标1...",
      "editable": true
    }
  ],
  "status": "draft",
  "version": 1,
  "created_at": 1704153600.0,
  "updated_at": 1704153600.0
}
```

**字段说明**:

| 字段                   | 类型      | 必填  | 说明                                                                                      |
| -------------------- | ------- | --- | --------------------------------------------------------------------------------------- |
| plan\_id             | string  | 是   | 规划唯一标识，格式：`plan_{uuid}`                                                                 |
| conversation\_id     | string  | 是   | 关联对话ID                                                                                  |
| title                | string  | 是   | 规划标题，长度限制：1-200字符                                                                       |
| content              | string  | 是   | 完整文档内容，Markdown格式                                                                       |
| sections             | array   | 是   | 文档章节列表                                                                                  |
| sections\[\].name     | string  | 是   | 章节名称，枚举：概述、目标、实施步骤、验收标准、风险与应对、备注                                                        |
| sections\[\].content  | string  | 是   | 章节内容                                                                                    |
| sections\[\].editable | boolean | 是   | 是否可编辑，默认：`true`                                                                         |
| status               | string  | 是   | 文档状态，枚举：`draft`（草稿）、`confirmed`（已确认）、`executing`（执行中）、`completed`（已完成）、`cancelled`（已取消） |
| version              | integer | 是   | 版本号，从1开始递增                                                                              |
| created\_at          | number  | 是   | 创建时间戳（Unix时间戳）                                                                          |
| updated\_at          | number  | 是   | 更新时间戳（Unix时间戳）                                                                          |

***

### 更新规划文档

手动更新规划文档内容（用户直接编辑）。

```http
PUT /api/plans/{plan_id}
```

**路径参数**:

| 参数       | 类型     | 必填  | 说明   |
| -------- | ------ | --- | ---- |
| plan\_id | string | 是   | 规划ID |

**请求体**:

```json
{
  "title": "更新后的标题",
  "content": "# 更新后的内容\n...",
  "sections": [
    {
      "name": "概述",
      "content": "更新后的概述内容...",
      "editable": true
    }
  ],
  "update_type": "manual"
}
```

**字段说明**:

| 字段           | 类型     | 必填  | 说明     | 验证规则                                               |
| ------------ | ------ | --- | ------ | -------------------------------------------------- |
| title        | string | 否   | 新标题    | 长度：1-200字符                                         |
| content      | string | 否   | 完整文档内容 | Markdown格式，长度：1-50000字符                            |
| sections     | array  | 否   | 章节列表   | 章节名称必须在预定义列表中                                      |
| update\_type | string | 否   | 更新类型   | 枚举：`manual`（手动编辑）、`ai_generated`（AI生成），默认：`manual` |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "plan_id": "plan_abc123",
    "version": 2,
    "updated_at": 1704153700.0
  },
  "message": "规划文档更新成功"
}
```

**错误响应**:

| HTTP状态码 | 错误码               | 说明            |
| ------- | ----------------- | ------------- |
| 404     | PLAN\_NOT\_FOUND  | 规划文档不存在       |
| 400     | INVALID\_CONTENT  | 内容格式错误或长度超出限制 |
| 400     | INVALID\_SECTIONS | 章节数据无效        |
| 409     | PLAN\_LOCKED      | 规划文档已确认，无法修改  |

***

### AI生成规划内容

使用AI生成或重新生成规划文档内容，通过WebSocket流式返回。

```http
POST /api/plans/{plan_id}/generate
```

**路径参数**:

| 参数       | 类型     | 必填  | 说明   |
| -------- | ------ | --- | ---- |
| plan\_id | string | 是   | 规划ID |

**请求体**:

```json
{
  "user_input": "请帮我制定一个水库调度计划...",
  "constraints": {
    "max_steps": 10,
    "time_limit": "3个月"
  },
  "references": ["相关文档1", "相关文档2"],
  "regenerate": false
}
```

**字段说明**:

| 字段          | 类型      | 必填  | 说明     | 验证规则                            |
| ----------- | ------- | --- | ------ | ------------------------------- |
| user\_input | string  | 是   | 用户需求描述 | 长度：10-10000字符                   |
| constraints | object  | 否   | 约束条件   | 键值对形式，值类型：string/number/boolean |
| references  | array   | 否   | 参考资料列表 | 每项为字符串，最多10项                    |
| regenerate  | boolean | 否   | 是否重新生成 | 默认：`false`，`true`表示基于现有内容优化     |

**响应说明**:

此接口返回WebSocket连接信息，实际内容通过WebSocket流式传输。

```json
{
  "success": true,
  "data": {
    "websocket_url": "ws://localhost:8000/ws/plans/plan_abc123/generate",
    "plan_id": "plan_abc123",
    "estimated_duration": "30-60秒"
  },
  "message": "请通过WebSocket连接接收生成内容"
}
```

**WebSocket消息格式**:

1. **连接成功**:
   
   ```json
   {
   "type": "connected",
   "plan_id": "plan_abc123",
   "timestamp": 1704153600.0
   }
   ```
2. **生成开始**:
   
   ```json
   {
   "type": "generation_started",
   "stage": "analyzing",
   "message": "正在分析需求...",
   "timestamp": 1704153600.0
   }
   ```
3. **内容块（流式）**:
   
   ```json
   {
   "type": "content_chunk",
   "section": "概述",
   "content": "生成的内容片段...",
   "accumulated": "累计生成的内容...",
   "progress": 0.35,
   "timestamp": 1704153600.0
   }
   ```
4. **章节完成**:
   
   ```json
   {
   "type": "section_completed",
   "section": "概述",
   "timestamp": 1704153600.0
   }
   ```
5. **生成完成**:
   
   ```json
   {
   "type": "generation_complete",
   "plan_id": "plan_abc123",
   "content": "完整文档内容",
   "sections": [...],
   "version": 2,
   "timestamp": 1704153600.0
   }
   ```
6. **生成错误**:
   
   ```json
   {
   "type": "generation_error",
   "code": "GENERATION_FAILED",
   "message": "生成过程中发生错误",
   "details": {...},
   "timestamp": 1704153600.0
   }
   ```

**错误响应**:

| HTTP状态码 | 错误码                      | 说明             |
| ------- | ------------------------ | -------------- |
| 404     | PLAN\_NOT\_FOUND         | 规划文档不存在        |
| 400     | INVALID\_USER\_INPUT     | 用户输入无效         |
| 409     | PLAN\_LOCKED             | 规划文档已确认，无法重新生成 |
| 503     | AI\_SERVICE\_UNAVAILABLE | AI服务暂时不可用      |

***

### 自然语言修改规划

使用自然语言指令修改规划文档，AI全量重新生成。

```http
POST /api/plans/{plan_id}/modify
```

**路径参数**:

| 参数       | 类型     | 必填  | 说明   |
| -------- | ------ | --- | ---- |
| plan\_id | string | 是   | 规划ID |

**请求体**:

```json
{
  "modification_request": "请增加关于应急预案的章节",
  "preserve_sections": ["概述", "目标"],
  "section_to_modify": "风险与应对"
}
```

**字段说明**:

| 字段                    | 类型     | 必填  | 说明          | 验证规则        |
| --------------------- | ------ | --- | ----------- | ----------- |
| modification\_request | string | 是   | 修改请求描述      | 长度：5-2000字符 |
| preserve\_sections    | array  | 否   | 需要保留的章节名称列表 | 最多6个章节      |
| section\_to\_modify   | string | 否   | 指定修改的章节     | 如不提供则全量重新生成 |

**响应说明**:

与 `/generate` 接口相同，通过WebSocket流式返回修改后的内容。

**错误响应**:

| HTTP状态码 | 错误码                            | 说明           |
| ------- | ------------------------------ | ------------ |
| 404     | PLAN\_NOT\_FOUND               | 规划文档不存在      |
| 400     | INVALID\_MODIFICATION\_REQUEST | 修改请求无效       |
| 409     | PLAN\_LOCKED                   | 规划文档已确认，无法修改 |

***

### 确认规划文档

确认规划文档，进入执行阶段。

**重要变更（v2.0.0）**：确认后立即触发决策链生成和执行，通过 WebSocket 流式返回完整流程。

```http
POST /api/plans/{plan_id}/confirm
```

**路径参数**:

| 参数       | 类型     | 必填  | 说明   |
| -------- | ------ | --- | ---- |
| plan\_id | string | 是   | 规划ID |

**请求体**:

```json
{
  "action": "proceed"
}
```

**字段说明**:

| 字段     | 类型     | 必填  | 说明                                       |
| -------- | -------- | ----- | ------------------------------------------ |
| action   | string   | 是    | 确认动作：`proceed`（继续执行）或 `upgrade_to_spec`（升级为Spec） |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "plan_id": "plan_abc123",
    "status": "confirmed",
    "websocket_url": "ws://localhost:8000/ws/chat/{conversation_id}",
    "message": "规划已确认，请通过 WebSocket 接收执行状态"
  }
}
```

**WebSocket 事件流**（复用现有连接 `WS /ws/chat/{conversation_id}`）：

确认成功后，客户端需要通过 WebSocket 发送 `confirm_plan` 消息开始执行：

```json
{
  "type": "confirm_plan",
  "plan_id": "plan_abc123",
  "conversation_id": "conv_abc123",
  "action": "proceed",
  "timestamp": 1704153600.0
}
```

服务端返回的事件流详见 [chain-generation-api.md](chain-generation-api.md) 中的 **Plan 模式事件流**：

```
plan_confirmed → task_extracting → chain_generation_stage → task_graph_generated → 
chain_generated → execution_started → task_update(with detail) → execution_progress → 
execution_complete → assistant_message
```

**错误响应**:

| HTTP状态码 | 错误码                      | 说明            |
| ------- | ------------------------ | ------------- |
| 404     | PLAN\_NOT\_FOUND         | 规划文档不存在       |
| 400     | INCOMPLETE\_PLAN         | 规划内容不完整，无法确认  |
| 409     | PLAN\_ALREADY\_CONFIRMED | 规划已确认，不能重复确认  |
| 422     | VALIDATION\_FAILED       | 规划验证失败，存在逻辑错误 |

***

### 取消规划任务

取消正在进行的规划生成或执行。

```http
POST /api/plans/{plan_id}/cancel
```

**路径参数**:

| 参数       | 类型     | 必填  | 说明   |
| -------- | ------ | --- | ---- |
| plan\_id | string | 是   | 规划ID |

**请求体**:

```json
{
  "reason": "用户主动取消",
  "cancel_type": "soft"
}
```

**字段说明**:

| 字段           | 类型     | 必填  | 说明   | 验证规则                                           |
| ------------ | ------ | --- | ---- | ---------------------------------------------- |
| reason       | string | 否   | 取消原因 | 长度：1-500字符                                     |
| cancel\_type | string | 否   | 取消类型 | 枚举：`soft`（软取消，保留文档）、`hard`（硬取消，删除文档），默认：`soft` |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "plan_id": "plan_abc123",
    "status": "cancelled",
    "cancelled_at": 1704153700.0,
    "message": "规划任务已取消"
  }
}
```

**错误响应**:

| HTTP状态码 | 错误码                      | 说明           |
| ------- | ------------------------ | ------------ |
| 404     | PLAN\_NOT\_FOUND         | 规划文档不存在      |
| 409     | PLAN\_ALREADY\_COMPLETED | 规划已执行完成，无法取消 |

***

### 获取规划列表

获取指定对话的所有规划文档列表。

```http
GET /api/conversations/{conversation_id}/plans
```

**路径参数**:

| 参数               | 类型     | 必填  | 说明   |
| ---------------- | ------ | --- | ---- |
| conversation\_id | string | 是   | 对话ID |

**查询参数**:

| 参数         | 类型      | 必填  | 说明                                    |
| ---------- | ------- | --- | ------------------------------------- |
| status     | string  | 否   | 状态过滤，支持多值：`draft,confirmed,executing` |
| page       | integer | 否   | 页码，默认：1                               |
| page\_size | integer | 否   | 每页数量，默认：10，最大：50                      |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "plan_id": "plan_abc123",
        "title": "水库调度规划",
        "status": "draft",
        "version": 1,
        "created_at": 1704153600.0,
        "updated_at": 1704153600.0
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

***

## Spec 模式 API

Spec 模式用于处理高复杂度的规格设计任务，生成完整的技术规格文档套装（spec.md、tasks.md、checklist.md）。

### 数据模型

#### SpecDocument 规格文档

```json
{
  "spec_id": "spec_abc123",
  "conversation_id": "conv_abc123",
  "feature_name": "flood-dispatch-system",
  "display_name": "洪水调度系统",
  "files": {
    "spec": {
      "title": "规格说明",
      "content": "# 洪水调度系统 - 规格文档\n..."
    },
    "tasks": {
      "title": "任务列表",
      "content": "# 洪水调度系统 - 任务列表\n..."
    },
    "checklist": {
      "title": "检查清单",
      "content": "# 洪水调度系统 - 检查清单\n..."
    }
  },
  "status": "draft",
  "version": 1,
  "metadata": {
    "complexity_score": 0.85,
    "estimated_effort": "2周",
    "tech_stack": ["Python", "FastAPI", "PostgreSQL"]
  },
  "created_at": 1704153600.0,
  "updated_at": 1704153600.0
}
```

**字段说明**:

| 字段                         | 类型      | 必填  | 说明                                                            |
| -------------------------- | ------- | --- | ------------------------------------------------------------- |
| spec\_id                   | string  | 是   | 规格唯一标识，格式：`spec_{uuid}`                                       |
| conversation\_id           | string  | 是   | 关联对话ID                                                        |
| feature\_name              | string  | 是   | 功能标识名，用于URL，格式：小写字母+连字符                                       |
| display\_name              | string  | 是   | 显示名称，长度：1-100字符                                               |
| files                      | object  | 是   | 三个文档的内容集合                                                    |
| files.spec                 | object  | 是   | 规格说明文档，对应 spec.md                                              |
| files.tasks                | object  | 是   | 任务列表文档，对应 tasks.md                                             |
| files.checklist            | object  | 是   | 检查清单文档，对应 checklist.md                                         |
| files.\*.title             | string  | 是   | 文档标题                                                          |
| files.\*.content           | string  | 是   | 文档内容（Markdown格式）                                              |
| status                     | string  | 是   | 状态，枚举：`draft`、`confirmed`、`executing`、`completed`、`cancelled` |
| version                    | integer | 是   | 版本号                                                           |
| metadata                   | object  | 否   | 元数据信息                                                         |
| metadata.complexity\_score | number  | 否   | 复杂度评分，范围：0-1                                                  |
| metadata.estimated\_effort | string  | 否   | 预估工作量                                                         |
| metadata.tech\_stack       | array   | 否   | 技术栈列表                                                         |
| created\_at                | number  | 是   | 创建时间戳                                                         |
| updated\_at                | number  | 是   | 更新时间戳                                                         |

### 更新规格文档

更新规格文档内容。

```http
PUT /api/specs/{feature_name}
```

**路径参数**:

| 参数            | 类型     | 必填  | 说明    |
| ------------- | ------ | --- | ----- |
| feature\_name | string | 是   | 功能标识名 |

**请求体**:

```json
{
  "display_name": "新显示名称",
  "files": {
    "spec": {
      "title": "规格说明",
      "content": "# 新内容..."
    },
    "tasks": {
      "title": "任务列表",
      "content": "# 任务列表内容..."
    },
    "checklist": {
      "title": "检查清单",
      "content": "# 检查清单内容..."
    }
  },
  "document_type": "spec"
}
```

**字段说明**:

| 字段             | 类型     | 必填  | 说明                |
| -------------- | ------ | --- | ----------------- |
| display\_name  | string | 否   | 新显示名称             |
| files          | object | 否   | 三个文档的内容          |
| files.spec     | object | 否   | 规格说明文档            |
| files.tasks    | object | 否   | 任务列表文档            |
| files.checklist| object | 否   | 检查清单文档            |
| document\_type | string | 否   | 指定更新的文档类型，不传则更新全部 |

**错误响应**:

| HTTP状态码 | 错误码          | 说明         |
| ------- | ------------ | ---------- |
| 409     | SPEC\_LOCKED | 规格已确认，无法修改 |

***

### AI生成规格内容

使用AI生成规格文档内容，通过WebSocket流式返回。

```http
POST /api/specs/{feature_name}/generate
```

**路径参数**:

| 参数            | 类型     | 必填  | 说明    |
| ------------- | ------ | --- | ----- |
| feature\_name | string | 是   | 功能标识名 |

**请求体**:

```json
{
  "user_input": "请设计洪水调度系统...",
  "based_on_plan": "plan_abc123",
  "documents_to_generate": ["spec", "tasks", "checklist"],
  "tech_preferences": {
    "language": "Python",
    "framework": "FastAPI"
  }
}
```

**字段说明**:

| 字段                      | 类型     | 必填  | 说明            |
| ----------------------- | ------ | --- | ------------- |
| user\_input             | string | 是   | 需求描述          |
| based\_on\_plan         | string | 否   | 基于的规划ID       |
| documents\_to\_generate | array  | 否   | 要生成的文档类型，默认全部 |
| tech\_preferences       | object | 否   | 技术偏好          |

**WebSocket消息格式**:

1. **文档开始生成**:
   
   ```json
   {
   "type": "document_started",
   "document_type": "spec",
   "timestamp": 1704153600.0
   }
   ```
2. **内容块（流式）**:
   
   ```json
   {
   "type": "content_chunk",
   "document_type": "spec",
   "section": "功能需求",
   "content": "...",
   "progress": 0.45,
   "timestamp": 1704153600.0
   }
   ```
3. **文档完成**:
   
   ```json
   {
   "type": "document_completed",
   "document_type": "spec",
   "timestamp": 1704153600.0
   }
   ```
4. **全部完成**:
   
   ```json
   {
   "type": "generation_complete",
   "spec_id": "spec_abc123",
   "documents": ["spec", "tasks", "checklist"],
   "files": {
     "spec": {
       "title": "规格说明",
       "content": "# 规格文档内容..."
     },
     "tasks": {
       "title": "任务列表",
       "content": "# 任务列表内容..."
     },
     "checklist": {
       "title": "检查清单",
       "content": "# 检查清单内容..."
     }
   },
   "version": 2,
   "timestamp": 1704153600.0
   }
   ```
   
   **字段说明**:
   
   | 字段 | 类型 | 说明 |
   |------|------|------|
   | files | object | 三个文档的内容 |
   | files.spec | object | 规格说明文档 |
   | files.tasks | object | 任务列表文档 |
   | files.checklist | object | 检查清单文档 |
   | files.*.title | string | 文档标题 |
   | files.*.content | string | 文档内容（Markdown格式） |

***

### 自然语言修改规格

使用自然语言修改规格文档。

```http
POST /api/specs/{feature_name}/modify
```

**请求体**:

```json
{
  "modification_request": "请在技术方案中增加缓存设计",
  "target_document": "spec",
  "target_section": "技术方案"
}
```

***

### 确认规格文档

确认规格文档，进入执行阶段。

**重要变更（v2.0.0）**：确认后立即触发决策链生成和执行，通过 WebSocket 流式返回完整流程。

```http
POST /api/specs/{feature_name}/confirm
```

**路径参数**:

| 参数            | 类型     | 必填  | 说明    |
| ------------- | ------ | --- | ----- |
| feature\_name | string | 是   | 功能标识名 |

**请求体**:

```json
{
  "action": "proceed"
}
```

**字段说明**:

| 字段     | 类型     | 必填  | 说明                                       |
| -------- | -------- | ----- | ------------------------------------------ |
| action   | string   | 是    | 确认动作：`proceed`（继续执行） |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "spec_id": "spec_abc123",
    "feature_name": "flood-warning-system",
    "status": "confirmed",
    "websocket_url": "ws://localhost:8000/ws/chat/{conversation_id}",
    "message": "规格已确认，请通过 WebSocket 接收执行状态"
  }
}
```

**WebSocket 事件流**（复用现有连接 `WS /ws/chat/{conversation_id}`）：

确认成功后，客户端需要通过 WebSocket 发送 `confirm_spec` 消息开始执行：

```json
{
  "type": "confirm_spec",
  "feature_name": "flood-warning-system",
  "conversation_id": "conv_abc123",
  "action": "proceed",
  "timestamp": 1704153600.0
}
```

服务端返回的事件流详见 [chain-generation-api.md](chain-generation-api.md) 中的 **Spec 模式事件流**：

```
spec_confirmed → task_extracting → chain_generation_stage → task_graph_generated → 
chain_generated → execution_started → task_update(with detail) → execution_progress → 
execution_complete → assistant_message
```

**错误响应**:

| HTTP状态码 | 错误码          | 说明         |
| ------- | ------------ | ---------- |
| 404     | SPEC\_NOT\_FOUND | 规格文档不存在 |
| 400     | INCOMPLETE\_SPEC | 规格内容不完整 |
| 409     | SPEC\_ALREADY\_CONFIRMED | 规格已确认 |
| 422     | VALIDATION\_FAILED | 规格验证失败 |

***

### 取消规格任务

取消规格生成或执行。

```http
POST /api/specs/{feature_name}/cancel
```

**请求体**:

```json
{
  "reason": "需求变更",
  "cancel_type": "soft"
}
```

***

## WebSocket 消息类型（按功能区分）

### 1. 聊天消息

```json
{
  "type": "chat_message",
  "role": "user",
  "content": "用户消息内容",
  "conversation_id": "conv_123",
  "timestamp": 1704153600.0
}
```

### 2. Plan/Spec 文档生成消息

**连接建立**:

```json
{
  "type": "connected",
  "document_id": "plan_abc123",
  "document_type": "plan",
  "timestamp": 1704153600.0
}
```

**生成阶段通知**:

```json
{
  "type": "generation_stage",
  "stage": "analyzing_requirements",
  "stage_name": "需求分析",
  "progress": 0.1,
  "message": "正在分析用户需求...",
  "timestamp": 1704153600.0
}
```

**内容块（流式）**:

```json
{
  "type": "content_chunk",
  "document_type": "plan",
  "document_id": "plan_abc123",
  "section": "概述",
  "section_index": 0,
  "content": "生成的内容片段...",
  "accumulated": "累计生成的内容...",
  "progress": 0.35,
  "timestamp": 1704153600.0
}
```

**章节完成**:

```json
{
  "type": "section_completed",
  "document_type": "plan",
  "document_id": "plan_abc123",
  "section": "概述",
  "section_index": 0,
  "timestamp": 1704153600.0
}
```

**文档完成（单个）**:

```json
{
  "type": "document_completed",
  "document_type": "plan",
  "document_id": "plan_abc123",
  "section_count": 6,
  "timestamp": 1704153600.0
}
```

**全部生成完成**:

```json
{
  "type": "generation_complete",
  "document_id": "plan_abc123",
  "document_type": "plan",
  "content": "完整文档内容",
  "sections": [
    {"name": "概述", "content": "..."},
    {"name": "目标", "content": "..."}
  ],
  "version": 2,
  "generation_stats": {
    "duration_ms": 45678,
    "total_tokens": 2500,
    "section_count": 6
  },
  "timestamp": 1704153600.0
}
```

**生成错误**:

```json
{
  "type": "generation_error",
  "code": "GENERATION_FAILED",
  "message": "生成过程中发生错误",
  "details": {
    "stage": "generating_steps",
    "error_type": "timeout",
    "retryable": true
  },
  "timestamp": 1704153600.0
}
```

**生成取消**:

```json
{
  "type": "generation_cancelled",
  "document_id": "plan_abc123",
  "reason": "用户主动取消",
  "cancelled_at": 1704153600.0,
  "timestamp": 1704153600.0
}
```

### 3. 任务执行消息（Plan/Spec确认后）

**重要变更（v2.0.0）**：决策链执行消息已迁移到 [chain-generation-api.md](chain-generation-api.md)，本文档不再重复定义。

复用 WebSocket 连接 `WS /ws/chat/{conversation_id}`，发送以下消息类型：
- `confirm_plan` - 确认 Plan 并开始执行
- `confirm_spec` - 确认 Spec 并开始执行
- `cancel_operation` - 取消操作

接收的事件类型包括：
- `plan_confirmed` / `spec_confirmed`
- `task_extracting`
- `chain_generation_stage`
- `task_graph_generated`
- `chain_generated`
- `execution_started`
- `task_update`（包含 detail 字段）
- `execution_progress`
- `execution_complete`
- `execution_error`
- `operation_cancelled`

详见 [chain-generation-api.md](chain-generation-api.md) 完整定义。

### 4. 过程事件

```json
{
  "type": "process_event",
  "stage": "node_started",
  "data": {
    "message": "开始执行任务",
    "node_id": "task_001",
    "task_name": "需求分析"
  },
  "timestamp": 1704153600.0
}
```

### 5. 错误消息

```json
{
  "type": "error",
  "code": "TASK_FAILED",
  "message": "任务执行失败",
  "details": {...},
  "timestamp": 1704153600.0
}
```

### 6. 心跳检测

**客户端发送**:

```json
{
  "type": "ping",
  "timestamp": 1704153600.0
}
```

**服务端响应**:

```json
{
  "type": "pong",
  "timestamp": 1704153600.0
}
```

### 7. 客户端控制消息

**取消生成**:

```json
{
  "type": "cancel_generation",
  "document_id": "plan_abc123",
  "reason": "用户主动取消",
  "timestamp": 1704153600.0
}
```

**暂停执行**（后续扩展）:

```json
{
  "type": "pause_execution",
  "execution_id": "exec_abc123",
  "timestamp": 1704153600.0
}
```

**恢复执行**（后续扩展）:

```json
{
  "type": "resume_execution",
  "execution_id": "exec_abc123",
  "timestamp": 1704153600.0
}
```

***

## 附录

### 数据模型

#### 对话模型

```json
{
  "id": "conv_001",
  "title": "对话标题",
  "created_at": 1704067200.0,
  "updated_at": 1704153600.0,
  "message_count": 10
}
```

#### 消息模型

```json
{
  "role": "user",
  "content": "消息内容",
  "timestamp": 1704153600.0
}
```

**角色类型**:

| 角色        | 说明     |
| --------- | ------ |
| user      | 用户消息   |
| assistant | AI助手消息 |

#### 任务状态

| 状态        | 说明  |
| --------- | --- |
| pending   | 待处理 |
| running   | 执行中 |
| completed | 已完成 |
| failed    | 失败  |
| cancelled | 已取消 |

### 枚举类型

#### 处理阶段（ProcessStage）

| 值                     | 说明       |
| --------------------- | -------- |
| task\_accepted        | 任务已接收    |
| task\_list\_generated | 任务列表已生成  |
| node\_started         | 节点开始执行   |
| node\_completed       | 节点执行完成   |
| node\_failed          | 节点执行失败   |
| agent\_called         | Agent被调用 |
| pipeline\_completed   | 流程执行完成   |

#### 数据来源（DataSource）

| 值             | 说明    |
| ------------- | ----- |
| user\_input   | 用户输入  |
| default       | 默认值   |
| calculated    | 计算得出  |
| external\_api | 外部API |
| file\_upload  | 文件上传  |

#### 规划文档状态（PlanStatus）

| 值         | 说明         | 可转移状态                |
| --------- | ---------- | -------------------- |
| draft     | 草稿状态，可编辑   | confirmed, cancelled |
| confirmed | 已确认，进入执行阶段 | executing, cancelled |
| executing | 执行中        | completed, cancelled |
| completed | 执行完成       | -                    |
| cancelled | 已取消        | -                    |

#### 规格文档状态（SpecStatus）

| 值         | 说明   | 可转移状态                |
| --------- | ---- | -------------------- |
| draft     | 草稿状态 | confirmed, cancelled |
| confirmed | 已确认  | executing, cancelled |
| executing | 执行中  | completed, cancelled |
| completed | 执行完成 | -                    |
| cancelled | 已取消  | -                    |

#### 任务状态（TaskStatus）

| 值         | 说明  |
| --------- | --- |
| pending   | 待处理 |
| running   | 执行中 |
| completed | 已完成 |
| failed    | 失败  |
| cancelled | 已取消 |
| retrying  | 重试中 |

#### 生成阶段（GenerationStage）

| 值                       | 说明   |
| ----------------------- | ---- |
| analyzing\_requirements | 分析需求 |
| generating\_outline     | 生成大纲 |
| generating\_content     | 生成内容 |
| optimizing\_content     | 优化内容 |
| validating\_content     | 验证内容 |
| completed               | 完成   |
| failed                  | 失败   |

#### 取消类型（CancelType）

| 值    | 说明       |
| ---- | -------- |
| soft | 软取消，保留文档 |
| hard | 硬取消，删除文档 |

#### 更新类型（UpdateType）

| 值             | 说明   |
| ------------- | ---- |
| manual        | 手动编辑 |
| ai\_generated | AI生成 |
| imported      | 导入   |

#### 确认状态（ConfirmationStatus）

| 值         | 说明  |
| --------- | --- |
| confirmed | 已确认 |
| rejected  | 已拒绝 |
| modified  | 已修改 |
| pending   | 待确认 |

### 错误码参考

#### 通用错误码

| 错误场景        | HTTP状态码 | 错误码                       | 错误信息                      |
| ----------- | ------- | ------------------------- | ------------------------- |
| 对话不存在       | 404     | CONVERSATION\_NOT\_FOUND  | "对话不存在"                   |
| 解析失败        | 500     | PARSE\_FAILED             | "解析失败: {详情}"              |
| 确认失败        | 500     | CONFIRM\_FAILED           | "确认失败: {详情}"              |
| 请求数据失败      | 500     | DATA\_REQUEST\_FAILED     | "请求数据失败: {详情}"            |
| 模式检测失败      | 500     | MODE\_DETECTION\_FAILED   | "模式检测失败: {详情}"            |
| 不支持的文件格式    | 400     | UNSUPPORTED\_FILE\_FORMAT | "不支持的文件格式，请上传CSV或Excel文件" |
| 未知的schema类型 | 400     | UNKNOWN\_SCHEMA\_TYPE     | "未知的schema类型: {类型}"       |
| 未知的解决类型     | 400     | UNKNOWN\_RESOLUTION\_TYPE | "未知的解决类型: {类型}"           |

#### Plan/Spec 模式错误码

| 错误场景     | HTTP状态码 | 错误码                            | 错误信息            | 处理建议                               |
| -------- | ------- | ------------------------------ | --------------- | ---------------------------------- |
| 规划不存在    | 404     | PLAN\_NOT\_FOUND               | "规划文档不存在"       | 检查plan\_id是否正确                     |
| 规划ID格式无效 | 400     | INVALID\_PLAN\_ID              | "规划ID格式无效"      | plan\_id格式应为`plan_{uuid}`          |
| 规格不存在    | 404     | SPEC\_NOT\_FOUND               | "规格文档不存在"       | 检查feature\_name是否正确                |
| 功能名格式无效  | 400     | INVALID\_FEATURE\_NAME         | "功能名格式无效或已存在"   | 使用小写字母、数字和连字符                      |
| 规划已锁定    | 409     | PLAN\_LOCKED                   | "规划文档已确认，无法修改"  | 创建新的规划版本                           |
| 规格已锁定    | 409     | SPEC\_LOCKED                   | "规格文档已确认，无法修改"  | 创建新的规格版本                           |
| 规划已确认    | 409     | PLAN\_ALREADY\_CONFIRMED       | "规划已确认，不能重复确认"  | 检查当前状态                             |
| 规划已完成    | 409     | PLAN\_ALREADY\_COMPLETED       | "规划已执行完成，无法取消"  | 无法操作已完成规划                          |
| 内容生成失败   | 500     | GENERATION\_FAILED             | "内容生成失败"        | 重试或检查输入                            |
| AI服务不可用  | 503     | AI\_SERVICE\_UNAVAILABLE       | "AI服务暂时不可用"     | 稍后重试                               |
| 规划内容不完整  | 400     | INCOMPLETE\_PLAN               | "规划内容不完整，无法确认"  | 补充缺失章节                             |
| 验证失败     | 422     | VALIDATION\_FAILED             | "规划验证失败，存在逻辑错误" | 检查规划逻辑                             |
| 修改请求无效   | 400     | INVALID\_MODIFICATION\_REQUEST | "修改请求无效"        | 提供更清晰的修改指令                         |
| 无效的用户输入  | 400     | INVALID\_USER\_INPUT           | "用户输入长度不符合要求"   | Plan: 10-10000字符, Spec: 20-20000字符 |
| 无效的标题    | 400     | INVALID\_TITLE                 | "标题长度超出限制"      | 标题长度1-200字符                        |
| 无效的内容    | 400     | INVALID\_CONTENT               | "内容格式错误或长度超出限制" | 检查Markdown格式                       |
| 无效的章节    | 400     | INVALID\_SECTIONS              | "章节数据无效"        | 使用预定义的章节名称                         |

#### WebSocket 错误码

| 错误场景  | 错误码                   | 说明                |
| ----- | --------------------- | ----------------- |
| 连接被拒绝 | CONNECTION\_REFUSED   | 文档正在处理中，无法建立新连接   |
| 文档不存在 | DOCUMENT\_NOT\_FOUND  | WebSocket连接时文档不存在 |
| 生成已取消 | GENERATION\_CANCELLED | 生成过程被用户取消         |
| 生成超时  | GENERATION\_TIMEOUT   | 内容生成超时            |
| 执行已暂停 | EXECUTION\_PAUSED     | 任务执行已暂停（后续扩展）       |
| 执行已停止 | EXECUTION\_STOPPED    | 任务执行已停止（后续扩展）       |

### 文件存储结构

```
data/
├── sessions/                          # 会话数据（任务状态持久化）
│   └── {session_id}/
│       ├── tasks.json                 # 任务列表及状态
│       ├── events.json                # 执行事件记录
│       └── context.json               # 执行上下文
│
├── conversations/                     # 对话数据
│   └── {conversation_id}/
│       ├── messages.json              # 消息历史
│       └── metadata.json              # 对话元数据
│
└── documents/                         # Plan/Spec 文档
    └── {document_id}/
        ├── content.md                 # 当前文档内容
        └── metadata.json              # 文档元数据
```

**说明**:

- 所有数据以 JSON 格式存储
- 历史记录管理方式待扩展
- 文档只保留当前版本，不保留历史

***

## 决策链生成 API（已迁移）

**重要变更（v2.0.0）**：决策链生成与执行 API 已完全迁移到 WebSocket，详见 [chain-generation-api.md](chain-generation-api.md)。

### 变更摘要

| 变更项 | 旧版本（v1.x） | 新版本（v2.0） |
|--------|---------------|---------------|
| 通信协议 | REST API + WebSocket | 纯 WebSocket |
| 普通模式 | `POST /api/chain-generation/generate` | `WS: chat_message` |
| Plan模式 | `POST /api/chain-generation/generate-from-plan` | `WS: confirm_plan` |
| Spec模式 | `POST /api/chain-generation/generate-from-spec` | `WS: confirm_spec` |
| 状态检查 | `GET /api/chain-generation/{id}/status` | WebSocket 流式推送 |
| 执行接口 | `POST /api/chain-generation/{id}/execute` | 合并到确认接口 |
| 暂停/恢复/取消 | REST API | 标记为后续扩展 |

***

## WebSocket 消息类型（决策链生成）

**已迁移**：详见 [chain-generation-api.md](chain-generation-api.md)。

### 1. 普通模式生成

**已迁移**：使用 `chat_message` 消息类型触发。

### 2. Plan/Spec 模式生成

**已迁移**：使用 `confirm_plan` 和 `confirm_spec` 消息类型触发。

### 3. 执行决策链

**已迁移**：合并到确认接口，自动触发执行。

***

## 决策链生成错误码

**已迁移**：详见 [chain-generation-api.md](chain-generation-api.md)。

***

## 版本历史

### v2.0.0 (2026-04-01)

**重大变更**:
- **决策链执行迁移到 WebSocket**：Plan/Spec 确认接口改为通过 WebSocket 流式返回
- **移除 REST API**：移除状态检查、执行接口等 REST API
- **复用连接**：复用现有 WebSocket 连接 `WS /ws/chat/{conversation_id}`
- **暂停/取消/恢复**：标记为后续扩展

### v1.2.0 (2026-04-01)

- **新增**: 决策链生成 API，支持普通模式、Plan 模式、Spec 模式三种生成方式
- **新增**: WebSocket 消息类型 `generate_chain_normal`、`generate_chain`、`execute_chain` 等
- **新增**: 决策链执行 API，支持启动执行、查询状态、取消执行等操作
- **新增**: 决策链生成错误码定义

### v1.1.0 (2026-04-01)

- **新增**: WebSocket 消息类型 `document_chunk` 和 `document_complete`，用于 Plan/Spec 模式的流式文档生成
- **修改**: SpecDocument 数据模型，将 `documents` 字段重命名为 `files`，简化结构（移除 `filename` 和 `sections`，只保留 `title` 和 `content`）
- **修改**: Spec 模式生成完成消息，新增 `files` 字段包含三个文档（spec、tasks、checklist）的完整内容

***

*文档版本: 2.0.0*  
*最后更新: 2026-04-01*
