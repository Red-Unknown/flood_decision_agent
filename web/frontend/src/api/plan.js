import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 获取规划列表
 * @param {string} conversationId - 对话ID
 * @returns {Promise<Array>} 规划列表
 */
export const getPlans = async (conversationId) => {
  const response = await apiClient.get(`/api/conversations/${conversationId}/plans`)
  return response.data
}

/**
 * 获取规划详情
 * @param {string} planId - 规划ID
 * @returns {Promise<Object>} 规划详情
 */
export const getPlan = async (planId) => {
  const response = await apiClient.get(`/api/plans/${planId}`)
  return response.data
}

/**
 * 创建规划
 * @param {Object} data - 规划数据
 * @returns {Promise<Object>} 创建的规划
 */
export const createPlan = async (data) => {
  const response = await apiClient.post('/api/plans', data)
  return response.data
}

/**
 * 更新规划
 * @param {string} planId - 规划ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>} 更新后的规划
 */
export const updatePlan = async (planId, data) => {
  const response = await apiClient.put(`/api/plans/${planId}`, data)
  return response.data
}

/**
 * 删除规划
 * @param {string} planId - 规划ID
 * @returns {Promise<Object>} 删除结果
 */
export const deletePlan = async (planId) => {
  const response = await apiClient.delete(`/api/plans/${planId}`)
  return response.data
}

/**
 * 更新规划章节
 * @param {string} planId - 规划ID
 * @param {string} section - 章节名称
 * @param {string} content - 章节内容
 * @returns {Promise<Object>} 更新结果
 */
export const updatePlanSection = async (planId, section, content) => {
  const response = await apiClient.patch(`/api/plans/${planId}/section`, {
    section,
    content,
  })
  return response.data
}

/**
 * AI生成规划内容
 * @param {string} planId - 规划ID
 * @returns {Promise<Object>} 生成结果
 */
export const generatePlanContent = async (planId) => {
  const response = await apiClient.post(`/api/plans/${planId}/generate`)
  return response.data
}
