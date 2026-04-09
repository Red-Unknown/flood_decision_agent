import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import websocketService from '@/services/websocket.js'

export const useWebSocketStore = defineStore('websocket', () => {
  // State
  const connectionState = ref('disconnected') // 'disconnected', 'connecting', 'connected', 'error'
  const conversationId = ref(null)
  const lastMessage = ref(null)
  const error = ref(null)
  const messageCallbacks = ref(new Map())

  // Getters
  const isConnected = computed(() => connectionState.value === 'connected')
  const isConnecting = computed(() => connectionState.value === 'connecting')
  const canSend = computed(() => isConnected.value)

  // Actions

  /**
   * 建立 WebSocket 连接
   * @param {string} cid - 对话ID
   */
  const connect = async (cid) => {
    if (!cid) {
      error.value = '对话ID不能为空'
      return false
    }

    try {
      connectionState.value = 'connecting'
      conversationId.value = cid
      await websocketService.connect(cid)
      connectionState.value = 'connected'
      error.value = null

      // 注册消息处理器
      registerMessageHandlers()

      return true
    } catch (err) {
      connectionState.value = 'error'
      error.value = err.message
      console.error('WebSocket 连接失败:', err)
      return false
    }
  }

  /**
   * 断开 WebSocket 连接
   */
  const disconnect = () => {
    websocketService.disconnect()
    connectionState.value = 'disconnected'
    conversationId.value = null
    messageCallbacks.value.clear()
  }

  /**
   * 发送聊天消息
   * @param {string} content - 消息内容
   */
  const sendChatMessage = (content) => {
    if (!isConnected.value) {
      error.value = 'WebSocket 未连接'
      return false
    }
    return websocketService.sendChatMessage(content)
  }

  /**
   * 启动 Plan 模式
   * @param {string} userInput - 用户输入
   */
  const sendStartPlan = (userInput) => {
    if (!isConnected.value) {
      error.value = 'WebSocket 未连接'
      return false
    }
    return websocketService.sendStartPlan(userInput)
  }

  /**
   * 启动 Spec 模式
   * @param {string} userInput - 用户输入
   */
  const sendStartSpec = (userInput) => {
    if (!isConnected.value) {
      error.value = 'WebSocket 未连接'
      return false
    }
    return websocketService.sendStartSpec(userInput)
  }

  /**
   * 确认 Plan 并开始执行
   * @param {string} planId - 规划ID
   * @param {string} conversationId - 对话ID
   * @param {string} action - 确认动作
   */
  const sendConfirmPlan = (planId, conversationId, action = 'proceed') => {
    if (!isConnected.value) {
      error.value = 'WebSocket 未连接'
      return false
    }
    return websocketService.sendConfirmPlan(planId, conversationId, action)
  }

  /**
   * 确认 Spec 并开始执行
   * @param {string} featureName - 功能名称
   * @param {string} conversationId - 对话ID
   * @param {string} action - 确认动作
   */
  const sendConfirmSpec = (featureName, conversationId, action = 'proceed') => {
    if (!isConnected.value) {
      error.value = 'WebSocket 未连接'
      return false
    }
    return websocketService.sendConfirmSpec(featureName, conversationId, action)
  }

  /**
   * 取消操作
   * @param {string} operationType - 操作类型
   * @param {string} operationId - 操作ID
   * @param {string} reason - 取消原因
   */
  const sendCancelOperation = (operationType, operationId, reason = '') => {
    if (!isConnected.value) {
      error.value = 'WebSocket 未连接'
      return false
    }
    return websocketService.sendCancelOperation(operationType, operationId, reason)
  }

  /**
   * 注册消息回调
   * @param {string} type - 消息类型
   * @param {Function} callback - 回调函数
   * @returns {Function} 取消注册的函数
   */
  const onMessage = (type, callback) => {
    console.log('[WebSocketStore] 注册消息处理器:', type)
    
    // 检查是否已存在相同的处理器
    const existingHandlers = messageCallbacks.value.get(type) || []
    const isDuplicate = existingHandlers.some(h => h.callback === callback)
    if (isDuplicate) {
      console.warn('[WebSocketStore] 处理器已存在，跳过注册:', type)
      return () => {}
    }
    
    const unsubscribe = websocketService.on(type, (message) => {
      console.log('[WebSocketStore] 收到消息:', type, message)
      callback(message)
    })

    // 保存回调引用
    if (!messageCallbacks.value.has(type)) {
      messageCallbacks.value.set(type, [])
    }
    messageCallbacks.value.get(type).push({ callback, unsubscribe })

    return () => {
      unsubscribe()
      const handlers = messageCallbacks.value.get(type)
      if (handlers) {
        const index = handlers.findIndex(h => h.callback === callback)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    }
  }

  /**
   * 注册所有消息处理器
   */
  const registerMessageHandlers = () => {
    // 连接成功
    websocketService.on('connected', (message) => {
      console.log('WebSocket 连接成功:', message)
    })

    // 心跳响应
    websocketService.on('pong', (message) => {
      // 心跳响应，可用于检测连接状态
    })

    // 错误消息
    websocketService.on('error', (message) => {
      error.value = message.message || 'WebSocket 错误'
      console.error('WebSocket 错误:', message)
    })
  }

  /**
   * 清除错误
   */
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    connectionState,
    conversationId,
    lastMessage,
    error,
    // Getters
    isConnected,
    isConnecting,
    canSend,
    // Actions
    connect,
    disconnect,
    sendChatMessage,
    sendStartPlan,
    sendStartSpec,
    sendConfirmPlan,
    sendConfirmSpec,
    sendCancelOperation,
    onMessage,
    clearError,
  }
})
