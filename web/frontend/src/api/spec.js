import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 获取规格列表
 * @param {string} conversation_id - 对话ID
 * @returns {Promise<Array>} 规格列表
 */
export const getSpecs = async (conversation_id) => {
  const response = await apiClient.get(`/api/conversations/${conversation_id}/specs`)
  return response.data
}

/**
 * 获取规格详情
 * @param {string} featureName - 功能名称
 * @returns {Promise<Object>} 规格详情
 */
export const getSpec = async (featureName) => {
  const response = await apiClient.get(`/api/specs/${featureName}`)
  return response.data
}

/**
 * 获取规格文件列表
 * @param {string} featureName - 功能名称
 * @returns {Promise<Array>} 文件列表
 */
export const getSpecFiles = async (featureName) => {
  const response = await apiClient.get(`/api/specs/${featureName}/files`)
  return response.data
}

/**
 * 获取规格文件内容
 * @param {string} featureName - 功能名称
 * @param {string} file - 文件名
 * @returns {Promise<Object>} 文件内容
 */
export const getSpecFile = async (featureName, file) => {
  const response = await apiClient.get(`/api/specs/${featureName}/${file}`)
  return response.data
}

/**
 * 创建规格
 * @param {Object} data - 规格数据
 * @returns {Promise<Object>} 创建的规格
 */
export const createSpec = async (data) => {
  const response = await apiClient.post('/api/specs', data)
  return response.data
}

/**
 * 更新规格文件
 * @param {string} featureName - 功能名称
 * @param {string} file - 文件名
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>} 更新结果
 */
export const updateSpecFile = async (featureName, file, data) => {
  const response = await apiClient.put(`/api/specs/${featureName}/${file}`, data)
  return response.data
}

/**
 * 更新规格章节
 * @param {string} featureName - 功能名称
 * @param {string} file - 文件名
 * @param {string} section - 章节名称
 * @param {string} content - 章节内容
 * @returns {Promise<Object>} 更新结果
 */
export const updateSpecSection = async (featureName, file, section, content) => {
  const response = await apiClient.patch(`/api/specs/${featureName}/${file}/section`, {
    section,
    content,
  })
  return response.data
}

/**
 * 删除规格
 * @param {string} featureName - 功能名称
 * @returns {Promise<Object>} 删除结果
 */
export const deleteSpec = async (featureName) => {
  const response = await apiClient.delete(`/api/specs/${featureName}`)
  return response.data
}

/**
 * AI生成规格内容
 * @param {string} featureName - 功能名称
 * @returns {Promise<Object>} 生成结果
 */
export const generateSpecContent = async (featureName) => {
  const response = await apiClient.post(`/api/specs/${featureName}/generate`)
  return response.data
}

/**
 * 审批通过规格
 * @param {string} featureName - 功能名称
 * @returns {Promise<Object>} 审批结果
 */
export const approveSpec = async (featureName) => {
  const response = await apiClient.post(`/api/specs/${featureName}/approve`)
  return response.data
}

/**
 * 修改规格
 * @param {string} featureName - 功能名称
 * @param {string} instruction - 修改指令
 * @returns {Promise<Object>} 修改结果
 */
export const modifySpec = async (featureName, instruction) => {
  const response = await apiClient.post(`/api/specs/${featureName}/modify`, {
    instruction,
  })
  return response.data
}

/**
 * 确认规格
 * @param {string} featureName - 功能名称
 * @param {string} action - 确认动作
 * @returns {Promise<Object>} 确认结果
 */
export const confirmSpec = async (featureName, action) => {
  const response = await apiClient.post(`/api/specs/${featureName}/confirm`, {
    action,
  })
  return response.data
}

/**
 * 取消规格
 * @param {string} featureName - 功能名称
 * @param {string} reason - 取消原因
 * @returns {Promise<Object>} 取消结果
 */
export const cancelSpec = async (featureName, reason) => {
  const response = await apiClient.post(`/api/specs/${featureName}/cancel`, {
    reason,
  })
  return response.data
}
