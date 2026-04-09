<template>
  <div class="chat-view">
    <ChatSidebar
      v-model="sidebarCollapsed"
      @new-chat="handleNewChat"
    />

    <div class="chat-main" :class="{ 'sidebar-collapsed': sidebarCollapsed, 'panel-open': isPanelOpen }">
      <ChatHeader
        :title="headerTitle"
        :subtitle="headerSubtitle"
        :sidebar-collapsed="sidebarCollapsed"
        :has-messages="hasMessages"
        :is-streaming="isStreaming"
        @toggle-sidebar="toggleSidebar"
        @clear="handleClear"
        @new-chat="handleNewChat"
      />

      <div class="chat-content">
        <template v-if="!hasMessages && !isStreaming">
          <EmptyState
            @action-click="handleQuickAction"
            @example-click="handleExampleClick"
          />
        </template>

        <template v-else>
          <el-scrollbar ref="messagesScrollbar" class="messages-container">
            <div class="messages-wrapper">
              <!-- 断点续传提示 -->
              <el-alert
                v-if="showResumeAlert"
                title="检测到未完成的任务"
                type="warning"
                :closable="false"
                class="resume-alert"
              >
                <template #default>
                  <div class="resume-content">
                    <span>您有一个 {{ getModeLabel(sessionStore.mode) }} 任务在 {{ formatTime(sessionStore.currentDocument?.updated_at) }} 前被中断。</span>
                    <el-button type="primary" size="small" @click="handleResume">恢复任务</el-button>
                    <el-button size="small" @click="handleDiscardResume">放弃</el-button>
                  </div>
                </template>
              </el-alert>

              <!-- 消息列表 -->
              <div v-if="messages.length === 0" style="padding: 20px; color: red;">
                警告: messages 数组为空
              </div>
              <div v-else style="padding: 10px; color: green;">
                messages 数组长度: {{ messages.length }}
              </div>
              <ChatMessage
                v-for="(message, index) in messages"
                :key="index"
                :message="message"
                :is-last-message="index === messages.length - 1 && message.role === 'assistant'"
                :streaming-content="streamingContent"
                :is-streaming="isStreaming && index === messages.length - 1 && message.role === 'assistant'"
                :mode="message.mode"
                :document-data="message.documentData"
                @view-document="handleViewDocument"
              />

              <!-- 流式消息占位 -->
              <ChatMessage
                v-if="isStreaming && !hasStreamingMessage"
                :message="{ role: 'assistant', content: '', timestamp: Date.now() / 1000 }"
                :is-last-message="true"
                :streaming-content="streamingContent"
                :is-streaming="true"
              />

              <!-- 决策链执行任务列表 -->
              <TaskExecutionList
                v-if="chainExecutionStore.hasActiveExecution || chainExecutionStore.isCompleted || chainExecutionStore.isFailed"
                :execution-state="chainExecutionStore.executionState"
                :tasks="chainExecutionStore.tasks"
                :is-generating="chainExecutionStore.isGenerating"
                :is-executing="chainExecutionStore.isExecuting"
                :pending-tasks-count="chainExecutionStore.pendingTasksCount"
                :running-tasks-count="chainExecutionStore.runningTasksCount"
                :completed-tasks-count="chainExecutionStore.completedTasksCount"
                :failed-tasks-count="chainExecutionStore.failedTasksCount"
                :default-collapsed="false"
              />

              <!-- 过程性事件时间线（仅在非决策链执行期间显示） -->
              <ProcessTimeline
                v-if="(hasProcessEvents || isStreaming) && !chainExecutionStore.hasActiveExecution && !chainExecutionStore.isCompleted && !chainExecutionStore.isFailed"
                :events="currentProcessEvents"
                :loading="isStreaming && currentProcessEvents.length === 0"
                @refresh="refreshProcessEvents"
              />

              <!-- 错误提示 -->
              <el-alert
                v-if="error"
                :title="error"
                type="error"
                closable
                @close="clearError"
                class="error-alert"
              />
            </div>
          </el-scrollbar>
        </template>
      </div>

      <SmartChatInput
        :is-streaming="isStreaming"
        :current-mode="currentMode"
        @send="handleSend"
        @mode-change="handleModeChange"
      />
    </div>

    <!-- 侧边面板编辑器 -->
    <SidePanelEditor
      :is-visible="isPanelOpen"
      :mode="panelMode"
      :document-data="panelDocumentData"
      :is-generating="isGeneratingDocument"
      :generation-progress="generationProgress"
      :is-modifying="isModifying"
      @close="handlePanelClose"
      @save="handlePanelSave"
      @confirm="handlePanelConfirm"
      @cancel="handlePanelCancel"
      @modify="handlePanelModify"
    />

    <!-- 展开按钮（当面板关闭但有文档数据时显示） -->
    <div
      v-if="!isPanelOpen && panelDocumentData"
      class="panel-toggle-btn"
      @click="isPanelOpen = true"
    >
      <span class="toggle-icon">◀</span>
      <span class="toggle-text">{{ panelMode === 'plan' ? '规划' : '规格' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat.js'
import { useSessionStore } from '@/stores/session.js'
import { usePlanStore } from '@/stores/plan.js'
import { useSpecStore } from '@/stores/spec.js'
import { useWebSocketStore } from '@/stores/websocket.js'
import { useChainExecutionStore } from '@/stores/chainExecution.js'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatHeader from '@/components/ChatHeader.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import SmartChatInput from '@/components/SmartChatInput.vue'
import EmptyState from '@/components/EmptyState.vue'
import ProcessTimeline from '@/components/ProcessTimeline.vue'
import SidePanelEditor from '@/components/SidePanelEditor.vue'
import TaskExecutionList from '@/components/TaskExecutionList.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()
const sessionStore = useSessionStore()
const planStore = usePlanStore()
const specStore = useSpecStore()
const wsStore = useWebSocketStore()
const chainExecutionStore = useChainExecutionStore()

// 状态
const sidebarCollapsed = ref(false)
const messagesScrollbar = ref(null)
const isPanelOpen = ref(false)
const panelMode = ref(null)
const panelDocumentData = ref(null)
const showResumeAlert = ref(false)
const currentMode = ref('simple')
const isGeneratingDocument = ref(false)
const generationProgress = ref(0)
const isModifying = ref(false)

// 计算属性
const messages = computed(() => chatStore.currentMessages)
const hasMessages = computed(() => chatStore.hasMessages)
const isStreaming = computed(() => chatStore.isStreaming.value)
const streamingContent = computed(() => chatStore.streamingContent.value)
const currentConversation = computed(() => chatStore.currentConversation)
const currentProcessEvents = computed(() => chatStore.currentProcessEvents)
const hasProcessEvents = computed(() => chatStore.hasProcessEvents)
const error = computed(() => chatStore.error || sessionStore.error || wsStore.error)

const hasStreamingMessage = computed(() => {
  const lastMessage = messages.value[messages.value.length - 1]
  return lastMessage && lastMessage.role === 'assistant' && isStreaming.value
})

const headerTitle = computed(() => {
  return currentConversation.value?.title || '水利智脑'
})

const headerSubtitle = computed(() => {
  if (isStreaming.value) {
    return '正在思考...'
  }
  if (isGeneratingDocument.value) {
    return `正在生成: ${getModeLabel(panelMode.value)} 文档`
  }
  return currentConversation.value ? '' : '开始新对话'
})

// 生命周期
onMounted(() => {
  // 检查是否有可恢复的会话
  const resumable = sessionStore.checkResumableSession()
  if (resumable) {
    showResumeAlert.value = true
  }

  // 监听网络状态
  window.addEventListener('online', handleOnline)

  // 注册 WebSocket 消息处理器
  registerWebSocketHandlers()
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  // 断开 WebSocket
  wsStore.disconnect()
})

// 存储取消注册函数
const wsUnsubscribers = []

// 注册 WebSocket 消息处理器
const registerWebSocketHandlers = () => {
  console.log('[ChatView] 开始注册 WebSocket 处理器...')

  // 清理旧的处理器
  wsUnsubscribers.forEach(unsub => unsub())
  wsUnsubscribers.length = 0
  console.log('[ChatView] 旧处理器已清理')

  // 通配符处理器 - 捕获所有消息（用于调试）
  try {
    const unsubAll = wsStore.onMessage('*', (message) => {
      console.log('[ChatView] 收到消息:', message.type, message)
    })
    wsUnsubscribers.push(unsubAll)
    console.log('[ChatView] 通配符处理器注册成功')
  } catch (error) {
    console.error('[ChatView] 注册通配符处理器失败:', error)
  }

  // 文档生成块
  const unsubChunk = wsStore.onMessage('document_chunk', (message) => {
    console.log('[ChatView] 收到 document_chunk:', message.content?.length || 0, 'accumulated:', message.accumulated?.length || 0)
    if (panelDocumentData.value) {
      if (panelMode.value === 'plan') {
        // Plan 模式：直接更新 content
        panelDocumentData.value = {
          ...panelDocumentData.value,
          content: message.accumulated || ''
        }
      } else if (panelMode.value === 'spec') {
        // Spec 模式：更新 files.spec.content
        panelDocumentData.value = {
          ...panelDocumentData.value,
          files: {
            ...panelDocumentData.value.files,
            spec: {
              ...panelDocumentData.value.files?.spec,
              content: message.accumulated || ''
            }
          }
        }
      }
    }
    generationProgress.value = message.progress || 0
  })
  wsUnsubscribers.push(unsubChunk)

  // 文档生成完成
  const unsubComplete = wsStore.onMessage('document_complete', (message) => {
    console.log('[ChatView] 收到 document_complete:', message.content?.length || 0, 'type:', message.document_type)
    isGeneratingDocument.value = false
    generationProgress.value = 100
    if (panelDocumentData.value) {
      if (panelMode.value === 'plan' || message.document_type === 'plan') {
        // Plan 模式：直接更新 content
        panelDocumentData.value = {
          ...panelDocumentData.value,
          content: message.content || '',
          document_id: message.document_id
        }
      } else if (panelMode.value === 'spec' || message.document_type === 'spec') {
        // Spec 模式：更新 files
        const files = message.files || {
          spec: { title: '规格说明', content: message.content || '' },
          tasks: { title: '任务列表', content: '' },
          checklist: { title: '检查清单', content: '' }
        }
        panelDocumentData.value = {
          ...panelDocumentData.value,
          files: files,
          document_id: message.document_id
        }
      }
    }
    ElMessage.success('文档生成完成')
  })
  wsUnsubscribers.push(unsubComplete)

  // 修改完成
  const unsubModification = wsStore.onMessage('modification_complete', (message) => {
    console.log('[ChatView] 收到 modification_complete:', message.content?.length || 0)
    isModifying.value = false
    if (panelDocumentData.value) {
      panelDocumentData.value = {
        ...panelDocumentData.value,
        content: message.content || ''
      }
    }
    ElMessage.success('修改完成')
  })
  wsUnsubscribers.push(unsubModification)

  // ========== 决策链生成与执行事件（v2.0.0 新增）==========

  // Plan 确认成功
  const unsubPlanConfirmed = wsStore.onMessage('plan_confirmed', (message) => {
    console.log('[ChatView] 收到 plan_confirmed:', message.plan_id)
    chainExecutionStore.startGeneration('plan', null)
    ElMessage.success('规划已确认，开始生成决策链')
  })
  wsUnsubscribers.push(unsubPlanConfirmed)

  // Spec 确认成功
  const unsubSpecConfirmed = wsStore.onMessage('spec_confirmed', (message) => {
    console.log('[ChatView] 收到 spec_confirmed:', message.feature_name)
    chainExecutionStore.startGeneration('spec', null)
    ElMessage.success('规格已确认，开始生成决策链')
  })
  wsUnsubscribers.push(unsubSpecConfirmed)

  // 意图解析结果（普通模式）
  const unsubIntentParsed = wsStore.onMessage('intent_parsed', (message) => {
    console.log('[ChatView] 收到 intent_parsed:', message.intent?.task_type)
    console.log('[ChatView] 调用 startGeneration')
    chainExecutionStore.startGeneration('normal', null)
    console.log('[ChatView] startGeneration 完成，isGenerating:', chainExecutionStore.isGenerating)
    console.log('[ChatView] hasActiveExecution:', chainExecutionStore.hasActiveExecution)
  })
  wsUnsubscribers.push(unsubIntentParsed)

  // 任务提取中
  const unsubTaskExtracting = wsStore.onMessage('task_extracting', (message) => {
    console.log('[ChatView] 收到 task_extracting:', message.message)
    chainExecutionStore.updateGenerationStage({
      stage: 'task_extracting',
      message: message.message,
      progress: message.progress,
    })
  })
  wsUnsubscribers.push(unsubTaskExtracting)

  // 决策链生成阶段
  const unsubChainGenerationStage = wsStore.onMessage('chain_generation_stage', (message) => {
    console.log('[ChatView] 收到 chain_generation_stage:', message.stage_name, message.progress)
    chainExecutionStore.updateGenerationStage({
      stage: message.stage,
      message: message.message,
      progress: message.progress,
    })
  })
  wsUnsubscribers.push(unsubChainGenerationStage)

  // 任务图生成完成
  const unsubTaskGraphGenerated = wsStore.onMessage('task_graph_generated', (message) => {
    console.log('[ChatView] 收到 task_graph_generated:', message.tasks?.length || 0, 'tasks')
    chainExecutionStore.setTaskGraphGenerated({
      generation_id: message.generation_id,
      tasks: message.tasks,
      total_count: message.total_count,
    })
  })
  wsUnsubscribers.push(unsubTaskGraphGenerated)

  // 决策链生成完成
  const unsubChainGenerated = wsStore.onMessage('chain_generated', (message) => {
    console.log('[ChatView] 收到 chain_generated:', message.generation_id)
    chainExecutionStore.setChainGenerated({
      generation_id: message.generation_id,
      mode: message.mode,
    })
  })
  wsUnsubscribers.push(unsubChainGenerated)

  // 执行开始
  const unsubExecutionStarted = wsStore.onMessage('execution_started', (message) => {
    console.log('[ChatView] 收到 execution_started:', message.execution_id)
    chainExecutionStore.startExecution({
      execution_id: message.execution_id,
      generation_id: message.generation_id,
      total_tasks: message.total_tasks,
    })
    ElMessage.info('开始执行决策链任务')
  })
  wsUnsubscribers.push(unsubExecutionStarted)

  // 任务状态更新
  const unsubTaskUpdate = wsStore.onMessage('task_update', (message) => {
    console.log('[ChatView] 收到 task_update:', message.task_id, message.status)
    chainExecutionStore.updateTaskStatus({
      task_id: message.task_id,
      status: message.status,
      duration_ms: message.duration_ms,
      result: message.result,
      detail: message.detail,
    })
  })
  wsUnsubscribers.push(unsubTaskUpdate)

  // 执行进度
  const unsubExecutionProgress = wsStore.onMessage('execution_progress', (message) => {
    console.log('[ChatView] 收到 execution_progress:', message.progress)
    chainExecutionStore.updateExecutionProgress({
      progress: message.progress,
      completed_tasks: message.completed_tasks,
      total_tasks: message.total_tasks,
    })
  })
  wsUnsubscribers.push(unsubExecutionProgress)

  // 执行完成
  const unsubExecutionComplete = wsStore.onMessage('execution_complete', (message) => {
    console.log('[ChatView] 收到 execution_complete:', message.success)
    chainExecutionStore.setExecutionComplete({
      success: message.success,
      summary: message.summary,
      results: message.results,
    })
    if (message.success) {
      ElMessage.success('决策链执行完成')
    } else {
      ElMessage.error('决策链执行失败')
    }
  })
  wsUnsubscribers.push(unsubExecutionComplete)

  // 执行错误
  const unsubExecutionError = wsStore.onMessage('execution_error', (message) => {
    console.error('[ChatView] 收到 execution_error:', message.message)
    chainExecutionStore.setExecutionError({
      code: message.code,
      message: message.message,
      error: message.error,
    })
    ElMessage.error(`执行错误: ${message.message}`)
  })
  wsUnsubscribers.push(unsubExecutionError)

  // 操作取消
  const unsubOperationCancelled = wsStore.onMessage('operation_cancelled', (message) => {
    console.log('[ChatView] 收到 operation_cancelled:', message.operation_type)
    chainExecutionStore.setOperationCancelled()
    ElMessage.info('操作已取消')
  })
  wsUnsubscribers.push(unsubOperationCancelled)

  // 过程事件 - 更新 ProcessTimeline
  const unsubProcess = wsStore.onMessage('process_event', (message) => {
    console.log('[ChatView] 收到 process_event:', message.stage)
    chatStore.addProcessEvent(message)
  })
  wsUnsubscribers.push(unsubProcess)

  // AI 助手消息（决策链执行完成后返回）
  try {
    const unsubAssistantMessage = wsStore.onMessage('assistant_message', (message) => {
      console.log('[ChatView] 收到 assistant_message:', message.content?.length || 0, 'chars')

      // 添加 AI 回复到消息列表
      chatStore.addAssistantMessage(message.content)

      // 重置流式状态（决策链执行不使用流式输出）
      chatStore.isStreaming.value = false
      chatStore.streamingContent.value = ''

      console.log('[ChatView] AI 消息已添加，流式状态已重置')
    })
    wsUnsubscribers.push(unsubAssistantMessage)
    console.log('[ChatView] assistant_message 处理器注册成功')
  } catch (error) {
    console.error('[ChatView] 注册 assistant_message 处理器失败:', error)
  }

  // 错误消息
  const unsubError = wsStore.onMessage('error', (message) => {
    console.error('[ChatView] 收到 error:', message)
    isGeneratingDocument.value = false
    isModifying.value = false
    chainExecutionStore.setExecutionError({
      code: message.code,
      message: message.message,
    })
  })
  wsUnsubscribers.push(unsubError)
}

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleNewChat = async () => {
  await chatStore.createConversation()
  sessionStore.resetSession()
  isPanelOpen.value = false
  currentMode.value = 'simple'
  router.push('/')
}

const handleSend = async (message, mode) => {
  if (!message.trim()) return

  // 处理命令模式切换
  if (mode === 'plan' || message.startsWith('/plan')) {
    const userInput = message.startsWith('/plan ') ? message.slice(6) : message
    await startPlanMode(userInput)
    return
  }
  if (mode === 'spec' || message.startsWith('/spec')) {
    const userInput = message.startsWith('/spec ') ? message.slice(6) : message
    await startSpecMode(userInput)
    return
  }

  // 普通消息发送
  await chatStore.sendMessage(message)

  nextTick(() => {
    scrollToBottom()
  })
}

const handleModeChange = (mode) => {
  currentMode.value = mode
  if (mode === 'plan') {
    openPlanMode()
  } else if (mode === 'spec') {
    openSpecMode()
  }
}

// 启动 Plan 模式（通过 WebSocket）
const startPlanMode = async (userInput) => {
  currentMode.value = 'plan'
  panelMode.value = 'plan'
  isPanelOpen.value = true
  isGeneratingDocument.value = true
  generationProgress.value = 0

  // 先初始化面板数据（确保在 WebSocket 消息到达前准备好）
  panelDocumentData.value = {
    title: userInput || '新规划',
    content: '',
    sections: {},
  }
  console.log('[ChatView] Plan 模式已启动，panelDocumentData 已初始化')

  // 确保有当前对话，如果没有则创建一个
  let conversationId = currentConversation.value?.id
  if (!conversationId) {
    console.log('[ChatView] 没有当前对话，创建新对话...')
    const newConversation = await chatStore.createConversation()
    conversationId = newConversation?.id
    console.log('[ChatView] 新对话创建完成:', conversationId)
  }

  // 确保 WebSocket 已连接
  if (!wsStore.isConnected && conversationId) {
    console.log('[ChatView] 连接 WebSocket:', conversationId)
    try {
      await wsStore.connect(conversationId)
      console.log('[ChatView] WebSocket 连接成功')
    } catch (error) {
      console.error('[ChatView] WebSocket 连接失败:', error)
      ElMessage.error('无法连接到服务器，请检查后端服务是否运行')
      isGeneratingDocument.value = false
      return
    }
  }

  // 延迟一小段时间确保 WebSocket 处理器已注册
  await new Promise(resolve => setTimeout(resolve, 100))

  // 检查 WebSocket 是否真的已连接
  if (!wsStore.isConnected) {
    console.error('[ChatView] WebSocket 未连接，无法发送消息')
    ElMessage.error('连接未建立，请稍后重试')
    isGeneratingDocument.value = false
    return
  }

  // 发送 start_plan 消息
  console.log('[ChatView] 发送 start_plan 消息, WebSocket 状态:', wsStore.isConnected)
  const sendResult = wsStore.sendStartPlan(userInput)
  if (!sendResult) {
    console.error('[ChatView] 发送 start_plan 消息失败')
    ElMessage.error('发送消息失败，请稍后重试')
    isGeneratingDocument.value = false
  }
}

// 启动 Spec 模式（通过 WebSocket）
const startSpecMode = async (userInput) => {
  currentMode.value = 'spec'
  panelMode.value = 'spec'
  isPanelOpen.value = true
  isGeneratingDocument.value = true
  generationProgress.value = 0

  // 先初始化面板数据（确保在 WebSocket 消息到达前准备好）
  panelDocumentData.value = {
    display_name: userInput || '新规格',
    files: {
      spec: { title: '规格说明', content: '' },
      tasks: { title: '任务列表', content: '' },
      checklist: { title: '检查清单', content: '' },
    },
  }
  console.log('[ChatView] Spec 模式已启动，panelDocumentData 已初始化')

  // 确保有当前对话，如果没有则创建一个
  let conversationId = currentConversation.value?.id
  if (!conversationId) {
    console.log('[ChatView] 没有当前对话，创建新对话...')
    const newConversation = await chatStore.createConversation()
    conversationId = newConversation?.id
    console.log('[ChatView] 新对话创建完成:', conversationId)
  }

  // 确保 WebSocket 已连接
  if (!wsStore.isConnected && conversationId) {
    console.log('[ChatView] 连接 WebSocket:', conversationId)
    try {
      await wsStore.connect(conversationId)
      console.log('[ChatView] WebSocket 连接成功')
    } catch (error) {
      console.error('[ChatView] WebSocket 连接失败:', error)
      ElMessage.error('无法连接到服务器，请检查后端服务是否运行')
      isGeneratingDocument.value = false
      return
    }
  }

  // 延迟一小段时间确保 WebSocket 处理器已注册
  await new Promise(resolve => setTimeout(resolve, 100))

  // 检查 WebSocket 是否真的已连接
  if (!wsStore.isConnected) {
    console.error('[ChatView] WebSocket 未连接，无法发送消息')
    ElMessage.error('连接未建立，请稍后重试')
    isGeneratingDocument.value = false
    return
  }

  // 发送 start_spec 消息
  console.log('[ChatView] 发送 start_spec 消息, WebSocket 状态:', wsStore.isConnected)
  const sendResult = wsStore.sendStartSpec(userInput)
  if (!sendResult) {
    console.error('[ChatView] 发送 start_spec 消息失败')
    ElMessage.error('发送消息失败，请稍后重试')
    isGeneratingDocument.value = false
  }
}

const openPlanMode = async () => {
  panelMode.value = 'plan'
  isPanelOpen.value = true

  // 加载 Plan 列表
  if (currentConversation.value) {
    await planStore.loadPlans(currentConversation.value.id)
  }

  // 如果有当前 Plan，加载它
  if (planStore.currentPlan) {
    panelDocumentData.value = planStore.currentPlan
  } else if (planStore.planList.length > 0) {
    await planStore.loadPlan(planStore.planList[0].id)
    panelDocumentData.value = planStore.currentPlan
  }
}

const openSpecMode = async () => {
  panelMode.value = 'spec'
  isPanelOpen.value = true

  // 加载 Spec 列表
  if (currentConversation.value) {
    await specStore.loadSpecs(currentConversation.value.id)
  }

  // 如果有当前 Spec，加载它
  if (specStore.currentSpec) {
    await specStore.loadSpecFiles(specStore.currentSpec.feature_name)
    panelDocumentData.value = specStore.currentSpec
  } else if (specStore.specList.length > 0) {
    const firstSpec = specStore.specList[0]
    await specStore.loadSpec(firstSpec.feature_name)
    await specStore.loadSpecFiles(firstSpec.feature_name)
    panelDocumentData.value = specStore.currentSpec
  }
}

const handleViewDocument = (documentData) => {
  panelDocumentData.value = documentData
  panelMode.value = documentData.type
  isPanelOpen.value = true
}

const handlePanelClose = () => {
  isPanelOpen.value = false
}

const handlePanelSave = async (data) => {
  try {
    if (panelMode.value === 'plan' && panelDocumentData.value?.id) {
      await planStore.updatePlan(panelDocumentData.value.id, {
        content: data.content,
      })
      ElMessage.success('规划保存成功')
    } else if (panelMode.value === 'spec' && panelDocumentData.value?.feature_name) {
      await specStore.updateFile(
        panelDocumentData.value.feature_name,
        data.activeFile || 'spec.md',
        { content: data.fileContent[data.activeFile] }
      )
      ElMessage.success('规格保存成功')
    }
  } catch (err) {
    ElMessage.error('保存失败')
  }
}

const handlePanelConfirm = async () => {
  try {
    const conversationId = currentConversation.value?.id
    if (!conversationId) {
      ElMessage.error('未找到当前对话')
      return
    }

    if (!wsStore.isConnected) {
      ElMessage.error('WebSocket 未连接')
      return
    }

    if (panelMode.value === 'plan' && panelDocumentData.value?.document_id) {
      // 发送 confirm_plan 消息触发决策链生成和执行
      const result = wsStore.sendConfirmPlan(
        panelDocumentData.value.document_id,
        conversationId,
        'proceed'
      )
      if (!result) {
        ElMessage.error('发送确认消息失败')
        return
      }
      ElMessage.success('规划已确认，开始生成决策链')
    } else if (panelMode.value === 'spec' && panelDocumentData.value?.document_id) {
      // 发送 confirm_spec 消息触发决策链生成和执行
      const result = wsStore.sendConfirmSpec(
        panelDocumentData.value.document_id,
        conversationId,
        'proceed'
      )
      if (!result) {
        ElMessage.error('发送确认消息失败')
        return
      }
      ElMessage.success('规格已确认，开始生成决策链')
    }
    
    // 关闭面板，显示执行状态
    isPanelOpen.value = false
    currentMode.value = 'simple'
  } catch (err) {
    console.error('确认失败:', err)
    ElMessage.error('确认失败')
  }
}

const handlePanelCancel = async () => {
  try {
    if (panelMode.value === 'plan' && panelDocumentData.value?.id) {
      // 调用 Plan cancel API
      // await planStore.cancelPlan(panelDocumentData.value.id)
    } else if (panelMode.value === 'spec' && panelDocumentData.value?.feature_name) {
      await specStore.cancelSpec(panelDocumentData.value.feature_name, 'manual_cancel')
    }
    ElMessage.success('任务已取消')
    isPanelOpen.value = false
    currentMode.value = 'simple'
  } catch (err) {
    ElMessage.error('取消失败')
  }
}

const handlePanelModify = async ({ instruction, section, file }) => {
  try {
    isModifying.value = true

    if (panelMode.value === 'plan' && panelDocumentData.value?.id) {
      await planStore.modifyPlan(panelDocumentData.value.id, instruction)
    } else if (panelMode.value === 'spec' && panelDocumentData.value?.feature_name) {
      await specStore.modifySpec(panelDocumentData.value.feature_name, instruction)
    }
  } catch (err) {
    isModifying.value = false
    ElMessage.error('修改失败')
  }
}

const handleResume = async () => {
  try {
    const result = await sessionStore.resumeSession()
    if (result) {
      ElMessage.success('任务已恢复')
      showResumeAlert.value = false
      // 打开对应的面板
      if (sessionStore.mode === 'plan') {
        openPlanMode()
      } else if (sessionStore.mode === 'spec') {
        openSpecMode()
      }
    }
  } catch (err) {
    ElMessage.error('恢复失败')
  }
}

const handleDiscardResume = () => {
  sessionStore.resetSession()
  showResumeAlert.value = false
}

const handleOnline = () => {
  // 网络恢复时检查是否需要恢复会话
  if (sessionStore.canResume && !sessionStore.hasActiveSession) {
    showResumeAlert.value = true
  }
}

const handleClear = async () => {
  try {
    await chatStore.clearCurrentConversation()
    sessionStore.resetSession()
    isPanelOpen.value = false
    currentMode.value = 'simple'
    ElMessage.success('对话已清空')
  } catch (error) {
    ElMessage.error('清空失败')
  }
}

const handleQuickAction = (action) => {
  const actionMessages = {
    '洪水调度': '请帮我制定北江超标准洪水调度方案',
    '生成报告': '请生成一份洪水调度分析报告',
    '智能问答': '什么是洪水调度决策链？',
  }
  const message = actionMessages[action] || action
  handleSend(message)
}

const handleExampleClick = (example) => {
  handleSend(example)
}

const refreshProcessEvents = async () => {
  if (currentConversation.value) {
    await chatStore.selectConversation(currentConversation.value.id)
    ElMessage.success('已刷新')
  }
}

const clearError = () => {
  chatStore.error = null
  sessionStore.clearError()
  wsStore.clearError()
}

const scrollToBottom = () => {
  if (messagesScrollbar.value) {
    const wrap = messagesScrollbar.value.wrapRef
    if (wrap) {
      wrap.scrollTop = wrap.scrollHeight
    }
  }
}

const getModeLabel = (mode) => {
  const labels = {
    simple: '简单模式',
    plan: 'Plan模式',
    spec: 'Spec模式',
  }
  return labels[mode] || mode
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时`
  return `${Math.floor(diff / 86400000)}天`
}

// 监听消息变化，自动滚动
watch(
  () => messages.value.length,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

// 监听流式内容变化，自动滚动
watch(
  () => streamingContent.value,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

// 监听路由参数，加载指定对话
watch(
  () => route.params.conversationId,
  async (conversationId) => {
    if (conversationId) {
      await chatStore.selectConversation(conversationId)
      // 连接 WebSocket
      await wsStore.connect(conversationId)
    }
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.chat-view {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-white);
  transition: margin-right 0.3s ease;

  &.panel-open {
    margin-right: 480px;
  }
}

.chat-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
}

.messages-container {
  flex: 1;

  :deep(.el-scrollbar__wrap) {
    padding: 20px 0;
  }
}

.messages-wrapper {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  padding: 0 20px;
}

.resume-alert {
  margin-bottom: 16px;

  .resume-content {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
}

.error-alert {
  margin: 16px 0;
}

.panel-toggle-btn {
  position: fixed;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  background: var(--el-color-primary);
  color: white;
  padding: 12px 8px;
  border-radius: 8px 0 0 8px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 99;
  transition: all 0.3s ease;

  &:hover {
    background: var(--el-color-primary-light-3);
    padding-right: 12px;
  }

  .toggle-icon {
    font-size: 12px;
    margin-bottom: 4px;
  }

  .toggle-text {
    font-size: 12px;
    writing-mode: vertical-rl;
    text-orientation: upright;
    letter-spacing: 2px;
  }
}
</style>
