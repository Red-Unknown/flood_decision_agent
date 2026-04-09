# 决策链生成与执行 API 设计文档

## 概述

本文档定义决策链生成与执行的 WebSocket 接口规范。决策链是水利智脑系统的核心执行单元，由一系列相互依赖的任务节点组成。

**重要变更说明（v2.0.0）**:
- **完全迁移到 WebSocket**：移除所有 REST API，统一使用 WebSocket 通信
- **接口合并**：决策链生成与执行合并到确认/发送消息接口
- **生成器模式**：后端通过 WebSocket 流式推送所有状态和结果
- **复用连接**：复用现有 WebSocket 连接 `WS /ws/chat/{conversation_id}`

## 基础信息

- **WebSocket URL**: `ws://localhost:8000/ws/chat/{conversation_id}`
- **协议**: WebSocket
- **字符编码**: UTF-8
- **消息格式**: JSON

***

## 架构说明

### 决策链生成流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        决策链生成流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   用户输入    │────▶│  意图解析     │────▶│  任务分解     │    │
│  │  User Input  │     │Intent Parser │     │Decomposer    │    │
│  └──────────────┘     └──────────────┘     └──────┬───────┘    │
│                                                   │             │
│                          ┌────────────────────────┘             │
│                          ▼                                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  决策链执行   │◀────│  任务图构建   │◀────│  链路优化     │    │
│  │  Execution   │     │ TaskGraph    │     │ Optimizer    │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 三种生成模式

| 模式 | 说明 | 触发方式 | 适用场景 |
|------|------|----------|----------|
| **普通模式** | 直接从用户输入生成决策链 | 发送 `chat_message` 消息 | 简单查询、快速执行 |
| **Plan模式** | 基于已确认的Plan文档生成 | 发送 `confirm_plan` 消息 | 需要规划确认的中等复杂度任务 |
| **Spec模式** | 基于已确认的Spec文档生成 | 发送 `confirm_spec` 消息 | 复杂系统开发任务 |

### 事件流总览

```
【普通模式事件流】
chat_message → user_message_confirm → intent_parsed → chain_generation_stage → 
task_graph_generated → chain_generated → execution_started → task_update(with detail) → 
execution_progress → execution_complete → assistant_message

【Plan模式事件流】
confirm_plan → plan_confirmed → task_extracting → chain_generation_stage → 
task_graph_generated → chain_generated → execution_started → task_update(with detail) → 
execution_progress → execution_complete → assistant_message

【Spec模式事件流】
confirm_spec → spec_confirmed → task_extracting → chain_generation_stage → 
task_graph_generated → chain_generated → execution_started → task_update(with detail) → 
execution_progress → execution_complete → assistant_message
```

**重要说明**:
- `execution_complete` 事件在 `assistant_message` 之前发送，包含执行结果汇总
- `assistant_message` 为最终 AI 回复，包含执行结果的友好展示

***

## WebSocket 消息类型

### 客户端 → 服务端

#### 1. 发送消息（普通模式）

触发决策链生成与执行。

```json
{
  "type": "chat_message",
  "content": "设计一个洪水预警系统",
  "conversation_id": "conv_abc123",
  "options": {
    "enable_chain_generation": true,
    "auto_execute": true
  },
  "timestamp": 1704153600.0
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 固定值: `chat_message` |
| content | string | 是 | 用户输入的自然语言描述 |
| conversation_id | string | 否 | 关联的对话ID，不传则创建新对话 |
| options | object | 否 | 选项配置 |
| options.enable_chain_generation | boolean | 否 | 是否生成决策链，默认 `true` |
| options.auto_execute | boolean | 否 | 是否自动执行，默认 `true` |
| timestamp | number | 是 | Unix时间戳 |

***

#### 2. 确认 Plan（Plan模式）

确认规划文档并开始执行。

```json
{
  "type": "confirm_plan",
  "plan_id": "plan_abc123",
  "conversation_id": "conv_abc123",
  "action": "proceed",
  "timestamp": 1704153600.0
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 固定值: `confirm_plan` |
| plan_id | string | 是 | 规划文档ID |
| conversation_id | string | 是 | 关联的对话ID |
| action | string | 否 | 确认动作: `proceed`（继续执行）或 `upgrade_to_spec`（升级为Spec），默认 `proceed` |
| timestamp | number | 是 | Unix时间戳 |

***

#### 3. 确认 Spec（Spec模式）

确认规格文档并开始执行。

```json
{
  "type": "confirm_spec",
  "feature_name": "flood-warning-system",
  "conversation_id": "conv_abc123",
  "action": "proceed",
  "timestamp": 1704153600.0
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 固定值: `confirm_spec` |
| feature_name | string | 是 | 规格功能名称 |
| conversation_id | string | 是 | 关联的对话ID |
| action | string | 否 | 确认动作: `proceed`，默认 `proceed` |
| timestamp | number | 是 | Unix时间戳 |

***

#### 4. 取消操作

取消正在进行的生成或执行。

```json
{
  "type": "cancel_operation",
  "operation_type": "generation",
  "operation_id": "gen_abc123",
  "reason": "用户取消",
  "timestamp": 1704153600.0
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 固定值: `cancel_operation` |
| operation_type | string | 是 | 操作类型: `generation` 或 `execution` |
| operation_id | string | 是 | 操作ID |
| reason | string | 否 | 取消原因 |
| timestamp | number | 是 | Unix时间戳 |

***

#### 5. 心跳检测

```json
{
  "type": "ping",
  "timestamp": 1704153600.0
}
```

***

### 服务端 → 客户端

#### 1. 连接成功

```json
{
  "type": "connected",
  "conversation_id": "conv_abc123",
  "timestamp": 1704153600.0
}
```

***

#### 2. 用户消息确认

```json
{
  "type": "user_message_confirm",
  "content": "设计一个洪水预警系统",
  "conversation_id": "conv_abc123",
  "timestamp": 1704153600.0
}
```

***

#### 3. 意图解析结果（普通模式特有）

```json
{
  "type": "intent_parsed",
  "intent": {
    "task_type": "flood_warning",
    "goal": {
      "description": "设计一个洪水预警系统",
      "keywords": ["洪水", "预警", "系统"]
    },
    "confidence": 0.92,
    "complexity_score": 0.75
  },
  "timestamp": 1704153600.0
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| intent.task_type | string | 任务类型 |
| intent.goal.description | string | 目标描述 |
| intent.goal.keywords | array | 关键词列表 |
| intent.confidence | number | 置信度，范围 0-1 |
| intent.complexity_score | number | 复杂度评分，范围 0-1 |

***

#### 4. Plan 确认成功（Plan模式特有）

```json
{
  "type": "plan_confirmed",
  "plan_id": "plan_abc123",
  "action": "proceed",
  "timestamp": 1704153600.0
}
```

***

#### 5. Spec 确认成功（Spec模式特有）

```json
{
  "type": "spec_confirmed",
  "feature_name": "flood-warning-system",
  "action": "proceed",
  "timestamp": 1704153600.0
}
```

***

#### 6. 任务提取中（Plan/Spec模式特有）

从文档中提取任务的过程通知。

```json
{
  "type": "task_extracting",
  "source": "plan",
  "source_id": "plan_abc123",
  "progress": 0.3,
  "message": "正在从规划文档提取任务...",
  "timestamp": 1704153600.0
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| source | string | 来源类型: `plan` 或 `spec` |
| source_id | string | 来源ID |
| progress | number | 进度，范围 0-1 |
| message | string | 状态描述 |

***

#### 7. 决策链生成阶段（三种模式共有）

```json
{
  "type": "chain_generation_stage",
  "stage": "task_decomposition",
  "stage_name": "任务分解",
  "progress": 0.3,
  "message": "正在分解任务...",
  "timestamp": 1704153600.0
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| stage | string | 阶段标识符（内部使用） |
| stage_name | string | 阶段中文名称（前端展示用） |
| progress | number | 进度，范围 0-1 |
| message | string | 状态描述 |

**阶段列表**:

| 阶段 (stage) | 阶段名称 (stage_name) | 说明 | 进度范围 |
|------|------|------|----------|
| `intent_parsing` | 意图解析 | 意图理解（普通模式） | 0.0 - 0.2 |
| `task_extracting` | 任务提取 | 从文档提取任务（Plan/Spec模式） | 0.0 - 0.2 |
| `task_decomposition` | 任务分解 | 任务分解 | 0.2 - 0.5 |
| `chain_optimization` | 决策链优化 | 链路优化 | 0.5 - 0.8 |
| `task_graph_building` | 任务图构建 | 任务图构建 | 0.8 - 1.0 |

**注意**: `stage_name` 为前端展示用，始终返回中文名称。`stage` 为内部标识符。

***

#### 8. 任务图生成完成（三种模式共有）

```json
{
  "type": "task_graph_generated",
  "generation_id": "gen_a1b2c3d4e5f6",
  "mode": "normal",
  "tasks": [
    {
      "task_id": "flood_warning_000",
      "task_name": "需求分析",
      "task_type": "data_collection",
      "dependencies": [],
      "status": "pending"
    },
    {
      "task_id": "flood_warning_001",
      "task_name": "数据采集",
      "task_type": "data_collection",
      "dependencies": ["flood_warning_000"],
      "status": "pending"
    }
  ],
  "total_count": 5,
  "reliability_score": 0.92,
  "timestamp": 1704153600.0
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| generation_id | string | 生成任务ID |
| mode | string | 生成模式: `normal` / `plan` / `spec` |
| tasks | array | 任务列表 |
| tasks[].task_id | string | 任务ID |
| tasks[].task_name | string | 任务名称 |
| tasks[].task_type | string | 任务类型 |
| tasks[].dependencies | array | 依赖任务ID列表 |
| tasks[].status | string | 任务状态: `pending` |
| total_count | number | 任务总数 |
| reliability_score | number | 可靠性评分，范围 0-1 |

***

#### 9. 决策链生成完成（三种模式共有）

```json
{
  "type": "chain_generated",
  "generation_id": "gen_a1b2c3d4e5f6",
  "mode": "normal",
  "task_graph": {
    "nodes": [...],
    "edges": [...]
  },
  "reliability_score": 0.92,
  "metadata": {
    "intent": {...},
    "decomposition": {...},
    "optimization": {...}
  },
  "timestamp": 1704153600.0
}
```

***

#### 10. 执行开始（三种模式共有）

```json
{
  "type": "execution_started",
  "execution_id": "exec_d4e5f6g7h8i9",
  "generation_id": "gen_a1b2c3d4e5f6",
  "total_tasks": 5,
  "timestamp": 1704153600.0
}
```

***

#### 11. 任务状态更新（三种模式共有）

包含 `detail` 字段支持流式详细信息，为多模态预留扩展空间。

```json
{
  "type": "task_update",
  "execution_id": "exec_d4e5f6g7h8i9",
  "task_id": "flood_warning_001",
  "task_name": "数据采集",
  "task_type": "data_collection",
  "status": "completed",
  "previous_status": "running",
  "detail": {
    "stage": "llm_generating",
    "message": "正在生成分析结果...",
    "progress": 0.5,
    "modalities": {
      "text": {
        "content": "部分生成的文本内容..."
      }
    }
  },
  "result": {
    "summary": "成功采集水位数据",
    "output_keys": ["water_level_data"],
    "output_preview": "水位数据预览..."
  },
  "duration_ms": 2345,
  "timestamp": 1704153600.0
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| execution_id | string | 执行ID |
| task_id | string | 任务ID |
| task_name | string | 任务名称 |
| task_type | string | 任务类型 |
| status | string | 当前状态: `pending` / `running` / `completed` / `failed` / `cancelled` |
| previous_status | string | 之前的状态 |
| detail | object | **流式详细信息（支持多模态预留）** |
| detail.stage | string | 任务内部阶段 |
| detail.message | string | 状态描述 |
| detail.progress | number | 任务内部进度，范围 0-1 |
| detail.modalities | object | **多模态预留字段** |
| detail.modalities.text | object | 文本模态 |
| detail.modalities.image | object | 图片模态（预留） |
| detail.modalities.chart | object | 图表模态（预留） |
| detail.modalities.table | object | 表格模态（预留） |
| result | object | 任务结果（仅 completed 状态） |
| result.summary | string | 结果摘要 |
| result.output_keys | array | 输出数据键列表 |
| result.output_preview | string | 输出预览 |
| duration_ms | number | 执行耗时（毫秒） |

***

#### 12. 执行进度（三种模式共有）

```json
{
  "type": "execution_progress",
  "execution_id": "exec_d4e5f6g7h8i9",
  "completed_tasks": 3,
  "total_tasks": 5,
  "progress": 0.6,
  "current_task": {
    "task_id": "flood_warning_003",
    "task_name": "模型预测",
    "status": "running"
  },
  "task_status_summary": {
    "pending": 1,
    "running": 1,
    "completed": 3,
    "failed": 0
  },
  "timestamp": 1704153600.0
}
```

***

#### 13. 执行完成（三种模式共有）

```json
{
  "type": "execution_complete",
  "execution_id": "exec_d4e5f6g7h8i9",
  "generation_id": "gen_a1b2c3d4e5f6",
  "success": true,
  "summary": {
    "total_tasks": 5,
    "completed_tasks": 5,
    "failed_tasks": 0,
    "total_duration_ms": 45678
  },
  "results": {
    "data_pool_snapshot": {...},
    "task_results": [...]
  },
  "timestamp": 1704153600.0
}
```

***

#### 14. 执行错误（三种模式共有）

```json
{
  "type": "execution_error",
  "execution_id": "exec_d4e5f6g7h8i9",
  "task_id": "flood_warning_002",
  "code": "TASK_FAILED",
  "message": "任务执行失败",
  "error": "数据源连接超时",
  "retry_count": 1,
  "max_retries": 2,
  "timestamp": 1704153600.0
}
```

***

#### 15. 操作取消

```json
{
  "type": "operation_cancelled",
  "operation_type": "generation",
  "operation_id": "gen_a1b2c3d4e5f6",
  "reason": "用户取消",
  "timestamp": 1704153600.0
}
```

***

#### 16. AI 回复

```json
{
  "type": "assistant_message",
  "content": "## 任务执行结果\n\n...",
  "conversation_id": "conv_abc123",
  "timestamp": 1704153600.0
}
```

***

#### 17. 错误消息

```json
{
  "type": "error",
  "code": "GENERATION_FAILED",
  "message": "生成决策链失败",
  "details": {
    "stage": "task_decomposition"
  },
  "timestamp": 1704153600.0
}
```

***

#### 18. 心跳响应

```json
{
  "type": "pong",
  "timestamp": 1704153600.0
}
```

***

## 数据模型

### TaskGraph 模型

```json
{
  "task_graph": {
    "nodes": [
      {
        "task_id": "string",
        "task_type": "string",
        "description": "string",
        "inputs": ["string"],
        "outputs": ["string"],
        "dependencies": ["string"],
        "metadata": {
          "business_type": "string",
          "execution_type": "string",
          "mcp_tools": [
            {
              "tool_name": "string",
              "server_name": "string"
            }
          ]
        }
      }
    ],
    "edges": [
      {
        "from": "string",
        "to": "string"
      }
    ]
  }
}
```

### ExecutionSummary 模型

```json
{
  "summary": {
    "total_tasks": 5,
    "completed_tasks": 5,
    "failed_tasks": 0,
    "skipped_tasks": 0,
    "total_duration_ms": 45678,
    "success_rate": 1.0
  }
}
```

***

## 错误码

### WebSocket 错误码

| 错误场景 | 错误码 | 说明 |
|----------|--------|------|
| 生成失败 | `GENERATION_FAILED` | 决策链生成失败 |
| 执行失败 | `EXECUTION_FAILED` | 决策链执行失败 |
| 任务失败 | `TASK_FAILED` | 单个任务执行失败 |
| 文档未确认 | `PLAN_NOT_CONFIRMED` | Plan 文档未确认 |
| 文档未确认 | `SPEC_NOT_CONFIRMED` | Spec 文档未确认 |
| 文档不存在 | `PLAN_NOT_FOUND` | Plan 文档不存在 |
| 文档不存在 | `SPEC_NOT_FOUND` | Spec 文档不存在 |
| 连接被拒绝 | `CONNECTION_REFUSED` | 任务正在处理中 |
| 生成已取消 | `GENERATION_CANCELLED` | 生成过程被用户取消 |
| 生成超时 | `GENERATION_TIMEOUT` | 内容生成超时 |
| 未知消息类型 | `UNKNOWN_MESSAGE_TYPE` | 客户端发送了未知类型的消息 |
| 无效JSON | `INVALID_JSON` | 消息格式错误 |

***

## 使用示例

### 普通模式完整示例

```javascript
// 建立 WebSocket 连接
const ws = new WebSocket('ws://localhost:8000/ws/chat/conv_001');

ws.onopen = () => {
  // 发送消息触发决策链生成
  ws.send(JSON.stringify({
    type: 'chat_message',
    content: '设计一个洪水预警系统',
    conversation_id: 'conv_001',
    options: {
      enable_chain_generation: true,
      auto_execute: true
    },
    timestamp: Date.now() / 1000
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'user_message_confirm':
      console.log('✓ 用户消息已确认');
      break;
      
    case 'intent_parsed':
      console.log('✓ 意图解析完成:', data.intent.task_type);
      break;
      
    case 'chain_generation_stage':
      console.log(`⏳ ${data.stage_name}: ${Math.round(data.progress * 100)}%`);
      break;
      
    case 'task_graph_generated':
      console.log(`✓ 任务图生成完成，共 ${data.total_count} 个任务`);
      // 初始化下拉链表
      initTaskList(data.tasks);
      break;
      
    case 'execution_started':
      console.log('▶️ 执行开始');
      break;
      
    case 'task_update':
      // 更新下拉链表
      updateTaskStatus(data);
      // 显示流式详细信息
      if (data.detail) {
        showTaskDetail(data.task_id, data.detail);
      }
      break;
      
    case 'execution_progress':
      updateProgressBar(data.progress);
      break;
      
    case 'execution_complete':
      console.log('✅ 执行完成');
      showExecutionSummary(data.summary);
      break;
      
    case 'assistant_message':
      displayAssistantMessage(data.content);
      break;
      
    case 'error':
      console.error('❌ 错误:', data.message);
      break;
  }
};
```

### Plan 模式完整示例

```javascript
// 确认 Plan 并开始执行
ws.send(JSON.stringify({
  type: 'confirm_plan',
  plan_id: 'plan_abc123',
  conversation_id: 'conv_001',
  action: 'proceed',
  timestamp: Date.now() / 1000
}));

// 事件处理（复用普通模式的处理器）
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'plan_confirmed':
      console.log('✓ Plan 已确认');
      break;
      
    case 'task_extracting':
      console.log('⏳ 正在从 Plan 提取任务...');
      break;
      
    // ... 复用普通模式的事件处理
    case 'chain_generation_stage':
    case 'task_graph_generated':
    case 'execution_started':
    case 'task_update':
    case 'execution_complete':
      // 相同处理逻辑
      break;
  }
};
```

### 取消操作示例

```javascript
// 取消正在进行的生成
ws.send(JSON.stringify({
  type: 'cancel_operation',
  operation_type: 'generation',
  operation_id: 'gen_abc123',
  reason: '用户取消',
  timestamp: Date.now() / 1000
}));

// 接收取消确认
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'operation_cancelled') {
    console.log('✓ 操作已取消:', data.reason);
  }
};
```

***

## 前端下拉链表展示指南

### 数据结构

```typescript
interface TaskExecutionState {
  executionId: string;
  generationId: string;
  tasks: Task[];
  currentProgress: number;
  status: 'idle' | 'generating' | 'executing' | 'completed' | 'failed' | 'cancelled';
}

interface Task {
  taskId: string;
  taskName: string;
  taskType: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  dependencies: string[];
  durationMs?: number;
  result?: TaskResult;
  detail?: TaskDetail;  // 流式详细信息
}

interface TaskDetail {
  stage: string;
  message: string;
  progress: number;
  modalities?: {
    text?: { content: string };
    image?: { url: string; description: string };
    chart?: { type: string; data: any };
    table?: { headers: string[]; rows: any[][] };
  };
}
```

### 更新逻辑

```javascript
// 初始化任务列表
function initTaskList(tasks) {
  taskState.tasks = tasks.map(t => ({
    ...t,
    detail: null
  }));
}

// 更新任务状态
function updateTaskStatus(data) {
  const task = taskState.tasks.find(t => t.taskId === data.task_id);
  if (task) {
    task.status = data.status;
    task.durationMs = data.duration_ms;
    task.result = data.result;
    task.detail = data.detail;  // 保存流式详细信息
  }
}
```

***

## 版本历史

### v2.0.0 (2026-04-01)

**重大变更**:
- **完全迁移到 WebSocket**：移除所有 REST API
- **接口合并**：决策链生成与执行合并到确认/消息接口
- **生成器模式**：后端流式推送所有状态
- **复用连接**：复用现有 WebSocket 连接
- **detail 字段**：支持单元任务流式详细信息，预留多模态扩展

### v1.0.0 (2026-04-01)

- 初始版本
- 支持三种生成模式（普通/Plan/Spec）
- REST API + WebSocket 混合架构

***

*文档版本: 2.0.0*  
*最后更新: 2026-04-01*
