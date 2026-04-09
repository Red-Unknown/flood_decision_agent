/**
 * WebSocket 服务模块
 *
 * 提供 WebSocket 连接管理和消息处理功能
 */

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8001'

class WebSocketService {
  constructor() {
    this.ws = null
    this.conversationId = null
    this.messageHandlers = new Map()
    this.connectionState = 'disconnected' // 'disconnected', 'connecting', 'connected'
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000 // 初始重连延迟 1秒
    this.heartbeatInterval = null
    this.heartbeatIntervalTime = 30000 // 30秒心跳

    // 调试信息
    console.log('[WebSocketService] 实例创建, messageHandlers:', this.messageHandlers)
  }

  /**
   * 建立 WebSocket 连接
   * @param {string} conversationId - 对话ID
   * @returns {Promise<void>}
   */
  async connect(conversationId) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      if (this.conversationId === conversationId) {
        console.log('WebSocket 已连接')
        return
      }
      // 切换到新的对话，先断开旧连接
      this.disconnect()
    }

    this.conversationId = conversationId
    this.connectionState = 'connecting'
    this.reconnectAttempts = 0

    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${WS_BASE_URL}/ws/chat/${conversationId}`
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('WebSocket 连接成功')
          this.connectionState = 'connected'
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data)
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket 错误:', error)
          this.connectionState = 'error'
          reject(error)
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket 连接关闭:', event.code, event.reason)
          this.connectionState = 'disconnected'
          this.stopHeartbeat()

          // 非主动断开，尝试重连
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect()
          }
        }
      } catch (error) {
        console.error('创建 WebSocket 连接失败:', error)
        this.connectionState = 'error'
        reject(error)
      }
    })
  }

  /**
   * 断开 WebSocket 连接
   */
  disconnect() {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close(1000, '主动断开连接')
      this.ws = null
    }
    this.connectionState = 'disconnected'
    this.conversationId = null
  }

  /**
   * 尝试重连
   */
  attemptReconnect() {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    console.log(`WebSocket ${delay}ms 后尝试第 ${this.reconnectAttempts} 次重连...`)

    setTimeout(() => {
      if (this.conversationId) {
        this.connect(this.conversationId).catch((error) => {
          console.error('WebSocket 重连失败:', error)
        })
      }
    }, delay)
  }

  /**
   * 开始心跳检测
   */
  startHeartbeat() {
    this.stopHeartbeat()
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', timestamp: Date.now() / 1000 })
      }
    }, this.heartbeatIntervalTime)
  }

  /**
   * 停止心跳检测
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 发送消息
   * @param {Object} message - 消息对象
   * @returns {boolean}
   */
  send(message) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message))
        return true
      } catch (error) {
        console.error('发送消息失败:', error)
        return false
      }
    }
    console.warn('WebSocket 未连接，无法发送消息')
    return false
  }

  /**
   * 发送聊天消息
   * @param {string} content - 消息内容
   */
  sendChatMessage(content) {
    return this.send({
      type: 'chat_message',
      content,
      timestamp: Date.now() / 1000,
    })
  }

  /**
   * 启动 Plan 模式
   * @param {string} userInput - 用户输入
   */
  sendStartPlan(userInput) {
    const message = {
      type: 'start_plan',
      user_input: userInput,
      timestamp: Date.now() / 1000,
    }
    console.log('[WebSocketService] 发送 start_plan 消息:', message)
    const result = this.send(message)
    console.log('[WebSocketService] 发送结果:', result)
    return result
  }

  /**
   * 启动 Spec 模式
   * @param {string} userInput - 用户输入
   */
  sendStartSpec(userInput) {
    return this.send({
      type: 'start_spec',
      user_input: userInput,
      timestamp: Date.now() / 1000,
    })
  }

  /**
   * 确认 Plan 并开始执行
   * @param {string} planId - 规划ID
   * @param {string} conversationId - 对话ID
   * @param {string} action - 确认动作: 'proceed' | 'upgrade_to_spec'
   */
  sendConfirmPlan(planId, conversationId, action = 'proceed') {
    return this.send({
      type: 'confirm_plan',
      plan_id: planId,
      conversation_id: conversationId,
      action,
      timestamp: Date.now() / 1000,
    })
  }

  /**
   * 确认 Spec 并开始执行
   * @param {string} featureName - 功能名称
   * @param {string} conversationId - 对话ID
   * @param {string} action - 确认动作: 'proceed'
   */
  sendConfirmSpec(featureName, conversationId, action = 'proceed') {
    return this.send({
      type: 'confirm_spec',
      feature_name: featureName,
      conversation_id: conversationId,
      action,
      timestamp: Date.now() / 1000,
    })
  }

  /**
   * 取消操作
   * @param {string} operationType - 操作类型: 'generation' | 'execution'
   * @param {string} operationId - 操作ID
   * @param {string} reason - 取消原因
   */
  sendCancelOperation(operationType, operationId, reason = '') {
    return this.send({
      type: 'cancel_operation',
      operation_type: operationType,
      operation_id: operationId,
      reason,
      timestamp: Date.now() / 1000,
    })
  }

  /**
   * 处理接收到的消息
   * @param {string} data - 消息数据
   */
  handleMessage(data) {
    try {
      const message = JSON.parse(data)
      const { type } = message

      console.log('[WebSocketService] 收到消息:', type, message)
      console.log('[WebSocketService] 当前所有处理器类型:', Array.from(this.messageHandlers.keys()))

      // 调用对应类型的处理器
      const handlers = this.messageHandlers.get(type) || []
      console.log(`[WebSocketService] 类型 ${type} 的处理器数量:`, handlers.length)
      if (handlers.length === 0) {
        console.warn(`[WebSocketService] 警告: 类型 ${type} 没有注册处理器`)
      }
      handlers.forEach((handler, index) => {
        console.log(`[WebSocketService] 调用处理器 ${index + 1}/${handlers.length} for type ${type}`)
        try {
          handler(message)
          console.log(`[WebSocketService] 处理器 ${index + 1} 完成`)
        } catch (error) {
          console.error(`处理消息类型 ${type} 时出错:`, error)
        }
      })

      // 调用通配符处理器（接收所有消息）
      const wildcardHandlers = this.messageHandlers.get('*') || []
      wildcardHandlers.forEach((handler) => {
        try {
          handler(message)
        } catch (error) {
          console.error('处理通配符消息时出错:', error)
        }
      })
    } catch (error) {
      console.error('解析 WebSocket 消息失败:', error, data)
    }
  }

  /**
   * 注册消息处理器
   * @param {string} type - 消息类型，'*' 表示所有消息
   * @param {Function} handler - 处理函数
   * @returns {Function} 取消注册的函数
   */
  on(type, handler) {
    console.log(`[WebSocketService] 注册处理器: ${type}`)
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, [])
    }
    this.messageHandlers.get(type).push(handler)
    console.log(`[WebSocketService] 类型 ${type} 的处理器数量:`, this.messageHandlers.get(type).length)

    // 返回取消注册的函数
    return () => {
      console.log(`[WebSocketService] 取消注册处理器: ${type}`)
      const handlers = this.messageHandlers.get(type)
      if (handlers) {
        const index = handlers.indexOf(handler)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    }
  }

  /**
   * 获取连接状态
   * @returns {string}
   */
  getConnectionState() {
    return this.connectionState
  }

  /**
   * 是否已连接
   * @returns {boolean}
   */
  isConnected() {
    return this.connectionState === 'connected' && this.ws?.readyState === WebSocket.OPEN
  }
}

// 创建单例实例
const websocketService = new WebSocketService()

export default websocketService
