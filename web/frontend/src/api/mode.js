import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 检测用户输入的模式
 * @param {string} userInput - 用户输入文本
 * @returns {Promise<Object>} 模式检测结果
 */
export const detectMode = async (userInput) => {
  const response = await apiClient.post('/api/mode/detect', {
    user_input: userInput,
  })
  return response.data
}

/**
 * 获取会话状态
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Object>} 会话状态
 */
export const getSessionStatus = async (sessionId) => {
  const response = await apiClient.get(`/api/sessions/${sessionId}/status`)
  return response.data
}

/**
 * 恢复会话
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Object>} 恢复结果
 */
export const resumeSession = async (sessionId) => {
  const response = await apiClient.post('/api/resume', {
    session_id: sessionId,
  })
  return response.data
}

/**
 * 取消 Plan 任务
 * @param {string} planId - 规划ID
 * @param {string} reason - 取消原因
 * @returns {Promise<Object>} 取消结果
 */
export const cancelPlan = async (planId, reason = 'manual_cancel') => {
  const response = await apiClient.post(`/api/plans/${planId}/cancel`, {
    reason,
    preserve_state: true,
  })
  return response.data
}

/**
 * 确认 Plan 文档
 * @param {string} planId - 规划ID
 * @param {string} action - 确认动作 (proceed | upgrade_to_spec)
 * @returns {Promise<Object>} 确认结果
 */
export const confirmPlan = async (planId, action = 'proceed') => {
  const response = await apiClient.post(`/api/plans/${planId}/confirm`, {
    action,
  })
  return response.data
}

/**
 * 自然语言修改 Plan
 * @param {string} planId - 规划ID
 * @param {string} instruction - 修改指令
 * @param {string} section - 可选的章节名称
 * @returns {Promise<Object>} 修改结果
 */
export const modifyPlan = async (planId, instruction, section = null) => {
  const response = await apiClient.post(`/api/plans/${planId}/modify`, {
    instruction,
    section,
  })
  return response.data
}
