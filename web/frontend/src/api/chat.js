import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 获取对话列表
 * @returns {Promise<Array>} 对话列表
 */
export const getConversations = async () => {
  const response = await apiClient.get('/api/conversations')
  return response.data
}

/**
 * 创建新对话
 * @param {string} title - 对话标题
 * @returns {Promise<Object>} 创建的对话
 */
export const createConversation = async (title = null) => {
  const response = await apiClient.post('/api/conversations', { title })
  return response.data
}

/**
 * 获取对话详情
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 对话详情
 */
export const getConversation = async (conversationId) => {
  const response = await apiClient.get(`/api/conversations/${conversationId}`)
  return response.data
}

/**
 * 删除对话
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 删除结果
 */
export const deleteConversation = async (conversationId) => {
  const response = await apiClient.delete(`/api/conversations/${conversationId}`)
  return response.data
}

/**
 * 获取对话消息历史
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Array>} 消息列表
 */
export const getMessages = async (conversationId) => {
  const response = await apiClient.get(`/api/conversations/${conversationId}/messages`)
  return response.data
}

/**
 * 获取对话过程性事件
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Array>} 过程性事件列表
 */
export const getProcessEvents = async (conversationId) => {
  const response = await apiClient.get(`/api/conversations/${conversationId}/process-events`)
  return response.data
}

/**
 * 清空对话消息
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 操作结果
 */
export const clearMessages = async (conversationId) => {
  const response = await apiClient.post(`/api/conversations/${conversationId}/clear`)
  return response.data
}

/**
 * 发送消息（非流式）
 * @param {string} message - 用户消息
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Object>} 响应内容
 */
export const sendMessage = async (message, conversationId = null) => {
  const response = await apiClient.post('/api/chat', {
    message,
    conversation_id: conversationId,
    stream: false,
  })
  return response.data
}

/**
 * 发送消息（流式）
 * @param {string} message - 用户消息
 * @param {string} conversationId - 对话ID
 * @param {Object} callbacks - 回调函数
 * @param {Function} callbacks.onProcessEvent - 过程性事件回调
 * @param {Function} callbacks.onChunk - 收到数据块时的回调
 * @param {Function} callbacks.onComplete - 完成时的回调
 * @param {Function} callbacks.onError - 错误时的回调
 */
export const sendMessageStream = async (
  message,
  conversationId = null,
  callbacks = {}
) => {
  const { onProcessEvent, onChunk, onComplete, onError } = callbacks

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        stream: true,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let accumulatedContent = ''
    let conversationIdFromResponse = null

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            switch (data.type) {
              case 'process_event':
                // 过程性事件
                if (onProcessEvent) {
                  onProcessEvent({
                    stage: data.stage,
                    timestamp: data.timestamp,
                    data: data.data
                  })
                }
                break

              case 'chunk':
                // 内容块
                accumulatedContent = data.accumulated
                if (onChunk) {
                  onChunk(data.content, accumulatedContent)
                }
                break

              case 'complete':
                // 完成
                conversationIdFromResponse = data.conversation_id
                if (onComplete) {
                  onComplete(data.content, data.conversation_id)
                }
                break

              case 'error':
                // 错误
                if (onError) {
                  onError(data.content)
                }
                break

              case 'user_message':
                // 用户消息确认
                conversationIdFromResponse = data.conversation_id
                break
            }
          } catch (e) {
            console.error('Parse SSE data error:', e)
          }
        }
      }
    }

    return {
      content: accumulatedContent,
      conversationId: conversationIdFromResponse
    }
  } catch (error) {
    console.error('Stream error:', error)
    if (onError) {
      onError(error.message)
    }
    throw error
  }
}

/**
 * 健康检查
 * @returns {Promise<Object>} 健康状态
 */
export const healthCheck = async () => {
  const response = await apiClient.get('/api/health')
  return response.data
}
