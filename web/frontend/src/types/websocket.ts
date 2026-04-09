/**
 * WebSocket 消息类型定义
 * 
 * 根据 chain-generation-api.md 和 input_plan_spec.md 定义
 */

// ==================== 客户端 → 服务端消息类型 ====================

/** 发送聊天消息（普通模式） */
export interface ChatMessageRequest {
  type: 'chat_message'
  content: string
  conversation_id?: string
  options?: {
    enable_chain_generation?: boolean
    auto_execute?: boolean
  }
  timestamp: number
}

/** 确认 Plan（Plan模式） */
export interface ConfirmPlanRequest {
  type: 'confirm_plan'
  plan_id: string
  conversation_id: string
  action?: 'proceed' | 'upgrade_to_spec'
  timestamp: number
}

/** 确认 Spec（Spec模式） */
export interface ConfirmSpecRequest {
  type: 'confirm_spec'
  feature_name: string
  conversation_id: string
  action?: 'proceed'
  timestamp: number
}

/** 取消操作 */
export interface CancelOperationRequest {
  type: 'cancel_operation'
  operation_type: 'generation' | 'execution'
  operation_id: string
  reason?: string
  timestamp: number
}

/** 心跳检测 */
export interface PingRequest {
  type: 'ping'
  timestamp: number
}

// ==================== 服务端 → 客户端消息类型 ====================

/** 连接成功 */
export interface ConnectedMessage {
  type: 'connected'
  conversation_id: string
  timestamp: number
}

/** 用户消息确认 */
export interface UserMessageConfirmMessage {
  type: 'user_message_confirm'
  content: string
  conversation_id: string
  timestamp: number
}

/** 意图解析结果（普通模式特有） */
export interface IntentParsedMessage {
  type: 'intent_parsed'
  intent: {
    task_type: string
    goal: {
      description: string
      keywords: string[]
    }
    confidence: number
    complexity_score: number
  }
  timestamp: number
}

/** Plan 确认成功（Plan模式特有） */
export interface PlanConfirmedMessage {
  type: 'plan_confirmed'
  plan_id: string
  action: string
  timestamp: number
}

/** Spec 确认成功（Spec模式特有） */
export interface SpecConfirmedMessage {
  type: 'spec_confirmed'
  feature_name: string
  action: string
  timestamp: number
}

/** 任务提取中（Plan/Spec模式特有） */
export interface TaskExtractingMessage {
  type: 'task_extracting'
  source: 'plan' | 'spec'
  source_id: string
  progress: number
  message: string
  timestamp: number
}

/** 决策链生成阶段（三种模式共有） */
export interface ChainGenerationStageMessage {
  type: 'chain_generation_stage'
  stage: 'intent_understanding' | 'task_decomposition' | 'chain_optimization' | 'task_graph_building'
  stage_name: string
  progress: number
  message: string
  timestamp: number
}

/** 任务 */
export interface Task {
  task_id: string
  task_name: string
  task_type: string
  dependencies: string[]
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
}

/** 任务图生成完成（三种模式共有） */
export interface TaskGraphGeneratedMessage {
  type: 'task_graph_generated'
  generation_id: string
  mode: 'normal' | 'plan' | 'spec'
  tasks: Task[]
  total_count: number
  reliability_score: number
  timestamp: number
}

/** 决策链生成完成（三种模式共有） */
export interface ChainGeneratedMessage {
  type: 'chain_generated'
  generation_id: string
  mode: 'normal' | 'plan' | 'spec'
  task_graph: {
    nodes: any[]
    edges: any[]
  }
  reliability_score: number
  metadata: {
    intent?: any
    decomposition?: any
    optimization?: any
  }
  timestamp: number
}

/** 执行开始（三种模式共有） */
export interface ExecutionStartedMessage {
  type: 'execution_started'
  execution_id: string
  generation_id: string
  total_tasks: number
  timestamp: number
}

/** 多模态内容 */
export interface TaskDetailModalities {
  text?: { content: string }
  image?: { url: string; description: string }
  chart?: { type: string; data: any }
  table?: { headers: string[]; rows: any[][] }
}

/** 任务详情 */
export interface TaskDetail {
  stage: string
  message: string
  progress: number
  modalities?: TaskDetailModalities
}

/** 任务结果 */
export interface TaskResult {
  summary: string
  output_keys: string[]
  output_preview: string
}

/** 任务状态更新（三种模式共有） */
export interface TaskUpdateMessage {
  type: 'task_update'
  execution_id: string
  task_id: string
  task_name: string
  task_type: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  previous_status?: string
  detail?: TaskDetail
  result?: TaskResult
  duration_ms?: number
  timestamp: number
}

/** 执行进度（三种模式共有） */
export interface ExecutionProgressMessage {
  type: 'execution_progress'
  execution_id: string
  completed_tasks: number
  total_tasks: number
  progress: number
  current_task: {
    task_id: string
    task_name: string
    status: string
  }
  task_status_summary: {
    pending: number
    running: number
    completed: number
    failed: number
  }
  timestamp: number
}

/** 执行完成（三种模式共有） */
export interface ExecutionCompleteMessage {
  type: 'execution_complete'
  execution_id: string
  generation_id: string
  success: boolean
  summary: {
    total_tasks: number
    completed_tasks: number
    failed_tasks: number
    total_duration_ms: number
  }
  results: {
    data_pool_snapshot?: any
    task_results?: any[]
  }
  timestamp: number
}

/** 执行错误（三种模式共有） */
export interface ExecutionErrorMessage {
  type: 'execution_error'
  execution_id: string
  task_id?: string
  code: string
  message: string
  error: string
  retry_count?: number
  max_retries?: number
  timestamp: number
}

/** 操作取消 */
export interface OperationCancelledMessage {
  type: 'operation_cancelled'
  operation_type: string
  operation_id: string
  reason: string
  timestamp: number
}

/** AI 回复 */
export interface AssistantMessage {
  type: 'assistant_message'
  content: string
  conversation_id: string
  timestamp: number
}

/** 错误消息 */
export interface ErrorMessage {
  type: 'error'
  code: string
  message: string
  details?: any
  timestamp: number
}

/** 心跳响应 */
export interface PongMessage {
  type: 'pong'
  timestamp: number
}

/** 文档生成块（Plan/Spec模式） */
export interface DocumentChunkMessage {
  type: 'document_chunk'
  document_id: string
  document_type?: 'plan' | 'spec'
  content: string
  accumulated?: string
  progress?: number
  timestamp: number
}

/** 文档生成完成（Plan/Spec模式） */
export interface DocumentCompleteMessage {
  type: 'document_complete'
  document_id: string
  document_type: 'plan' | 'spec'
  content: string
  files?: {
    spec?: { title: string; content: string }
    tasks?: { title: string; content: string }
    checklist?: { title: string; content: string }
    plan?: { title: string; content: string }
  }
  timestamp: number
}

/** 生成开始 */
export interface GenerationStartedMessage {
  type: 'generation_started'
  document_id: string
  document_type: 'plan' | 'spec'
  timestamp: number
}

/** 生成错误 */
export interface GenerationErrorMessage {
  type: 'generation_error'
  code: string
  message: string
  timestamp: number
}

/** 修改完成 */
export interface ModificationCompleteMessage {
  type: 'modification_complete'
  content: string
  timestamp: number
}

/** 过程事件 */
export interface ProcessEventMessage {
  type: 'process_event'
  stage: string
  data: any
  timestamp: number
}

/** 流式内容块 */
export interface ChunkMessage {
  type: 'chunk'
  content: string
  accumulated: string
  timestamp: number
}

/** 完成消息 */
export interface CompleteMessage {
  type: 'complete'
  content: string
  conversation_id: string
  timestamp: number
}

/** 开始消息 */
export interface StartMessage {
  type: 'start'
  timestamp: number
}

// ==================== 联合类型 ====================

export type WebSocketMessage =
  | ConnectedMessage
  | UserMessageConfirmMessage
  | IntentParsedMessage
  | PlanConfirmedMessage
  | SpecConfirmedMessage
  | TaskExtractingMessage
  | ChainGenerationStageMessage
  | TaskGraphGeneratedMessage
  | ChainGeneratedMessage
  | ExecutionStartedMessage
  | TaskUpdateMessage
  | ExecutionProgressMessage
  | ExecutionCompleteMessage
  | ExecutionErrorMessage
  | OperationCancelledMessage
  | AssistantMessage
  | ErrorMessage
  | PongMessage
  | DocumentChunkMessage
  | DocumentCompleteMessage
  | GenerationStartedMessage
  | GenerationErrorMessage
  | ModificationCompleteMessage
  | ProcessEventMessage
  | ChunkMessage
  | CompleteMessage
  | StartMessage

// ==================== 任务执行状态 ====================

export interface TaskExecutionState {
  executionId: string | null
  generationId: string | null
  tasks: TaskWithDetail[]
  currentProgress: number
  status: 'idle' | 'generating' | 'executing' | 'completed' | 'failed' | 'cancelled'
}

export interface TaskWithDetail extends Task {
  durationMs?: number
  result?: TaskResult
  detail?: TaskDetail
}
