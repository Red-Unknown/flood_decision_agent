import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getConversations,
  createConversation as apiCreateConversation,
  deleteConversation as apiDeleteConversation,
  getMessages,
  getProcessEvents,
  clearMessages as apiClearMessages,
} from '@/api/chat.js'
import { useWebSocketStore } from './websocket.js'

export const useChatStore = defineStore('chat', () => {
  // State
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const processEvents = ref([])  // 过程性事件
  const isStreaming = ref(false)
  const streamingContent = ref('')
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const conversationList = computed(() => conversations.value)
  const currentMessages = computed(() => messages.value)
  const currentProcessEvents = computed(() => processEvents.value)
  const hasMessages = computed(() => messages.value.length > 0)
  const hasProcessEvents = computed(() => processEvents.value.length > 0)

  // Actions

  /**
   * 加载对话列表
   */
  const loadConversations = async () => {
    try {
      isLoading.value = true
      const data = await getConversations()
      conversations.value = data
    } catch (err) {
      error.value = err.message
      console.error('加载对话列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 创建新对话
   */
  const createConversation = async (title = null) => {
    try {
      isLoading.value = true
      const conversation = await apiCreateConversation(title)
      conversations.value.unshift(conversation)
      currentConversation.value = conversation
      messages.value = []
      processEvents.value = []
      return conversation
    } catch (err) {
      error.value = err.message
      console.error('创建对话失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 选择对话
   */
  const selectConversation = async (conversationId) => {
    try {
      isLoading.value = true
      const conversation = conversations.value.find(c => c.id === conversationId)
      if (conversation) {
        currentConversation.value = conversation
        // 加载消息历史
        const history = await getMessages(conversationId)
        messages.value = history
        // 加载过程性事件
        const events = await getProcessEvents(conversationId)
        processEvents.value = events
      }
    } catch (err) {
      error.value = err.message
      console.error('加载对话数据失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 删除对话
   */
  const deleteConversation = async (conversationId) => {
    try {
      await apiDeleteConversation(conversationId)
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      if (currentConversation.value?.id === conversationId) {
        currentConversation.value = null
        messages.value = []
        processEvents.value = []
      }
    } catch (err) {
      error.value = err.message
      console.error('删除对话失败:', err)
      throw err
    }
  }

  /**
   * 添加过程性事件
   */
  const addProcessEvent = (event) => {
    processEvents.value.push(event)
  }

  /**
   * 清空过程性事件
   */
  const clearProcessEvents = () => {
    processEvents.value = []
  }

  /**
   * 添加 AI 助手消息
   */
  const addAssistantMessage = (content) => {
    console.log('[ChatStore] addAssistantMessage 被调用, content 长度:', content?.length)

    const assistantMessage = {
      role: 'assistant',
      content: content,
      timestamp: Date.now() / 1000,
    }
    console.log('[ChatStore] 准备添加消息:', assistantMessage)

    // 使用展开运算符创建新数组，确保响应式更新
    messages.value = [...messages.value, assistantMessage]
    console.log('[ChatStore] 消息已添加, 当前 messages 长度:', messages.value.length)
    console.log('[ChatStore] 当前 messages:', messages.value)

    // 更新对话消息计数
    const conversation = conversations.value.find(c => c.id === currentConversation.value?.id)
    if (conversation) {
      conversation.message_count = messages.value.length
      conversation.updated_at = Date.now() / 1000
      console.log('[ChatStore] 对话消息计数已更新:', conversation.message_count)
    } else {
      console.log('[ChatStore] 警告: 未找到当前对话')
    }
  }

  /**
   * 发送消息（使用 WebSocket）
   */
  const sendMessage = async (content) => {
    if (!content.trim()) return

    const wsStore = useWebSocketStore()

    try {
      // 如果没有当前对话，先创建一个
      if (!currentConversation.value) {
        await createConversation()
      }

      // 确保 WebSocket 已连接
      if (!wsStore.isConnected) {
        const connected = await wsStore.connect(currentConversation.value.id)
        if (!connected) {
          throw new Error('WebSocket 连接失败')
        }
      }

      // 添加用户消息到列表
      const userMessage = {
        role: 'user',
        content: content,
        timestamp: Date.now() / 1000,
      }
      messages.value.push(userMessage)

      // 清空之前的过程性事件
      clearProcessEvents()

      // 开始流式响应
      isStreaming.value = true
      streamingContent.value = ''

      // 注册 WebSocket 消息处理器
      const unsubscribeChunk = wsStore.onMessage('chunk', (message) => {
        streamingContent.value = message.accumulated
      })

      const unsubscribeComplete = wsStore.onMessage('complete', (message) => {
        // 添加AI回复到消息列表
        const assistantMessage = {
          role: 'assistant',
          content: message.content,
          timestamp: Date.now() / 1000,
        }
        messages.value.push(assistantMessage)

        // 清空流式内容
        streamingContent.value = ''
        isStreaming.value = false

        // 更新对话消息计数
        const conversation = conversations.value.find(c => c.id === currentConversation.value.id)
        if (conversation) {
          conversation.message_count = messages.value.length
          conversation.updated_at = Date.now() / 1000
        }

        // 取消注册
        unsubscribeChunk()
        unsubscribeComplete()
      })

      const unsubscribeError = wsStore.onMessage('error', (message) => {
        console.error('发送消息失败:', message.message)
        error.value = message.message
        isStreaming.value = false
        streamingContent.value = ''

        // 添加错误消息
        const errorMsg = {
          role: 'assistant',
          content: `抱歉，处理您的消息时出错：${message.message}`,
          timestamp: Date.now() / 1000,
          isError: true,
        }
        messages.value.push(errorMsg)

        // 取消注册
        unsubscribeChunk()
        unsubscribeComplete()
        unsubscribeError()
      })

      const unsubscribeProcessEvent = wsStore.onMessage('process_event', (message) => {
        addProcessEvent({
          stage: message.stage,
          timestamp: message.timestamp,
          data: message.data
        })
      })

      // 发送消息
      wsStore.sendChatMessage(content)

    } catch (err) {
      error.value = err.message
      isStreaming.value = false
      streamingContent.value = ''
      console.error('发送消息失败:', err)
    }
  }

  /**
   * 清空当前对话
   */
  const clearCurrentConversation = async () => {
    if (currentConversation.value) {
      try {
        await apiClearMessages(currentConversation.value.id)
        messages.value = []
        processEvents.value = []
        const conversation = conversations.value.find(c => c.id === currentConversation.value.id)
        if (conversation) {
          conversation.message_count = 0
        }
      } catch (err) {
        error.value = err.message
        console.error('清空对话失败:', err)
      }
    }
  }

  /**
   * 更新对话标题
   */
  const updateConversationTitle = (conversationId, title) => {
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (conversation) {
      conversation.title = title
    }
  }

  return {
    // State
    conversations,
    currentConversation,
    messages,
    processEvents,
    isStreaming,
    streamingContent,
    isLoading,
    error,
    // Getters
    conversationList,
    currentMessages,
    currentProcessEvents,
    hasMessages,
    hasProcessEvents,
    // Actions
    loadConversations,
    createConversation,
    selectConversation,
    deleteConversation,
    sendMessage,
    clearCurrentConversation,
    updateConversationTitle,
    addProcessEvent,
    clearProcessEvents,
    addAssistantMessage,
  }
})
