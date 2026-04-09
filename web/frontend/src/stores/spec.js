import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getSpecs as apiGetSpecs,
  getSpec as apiGetSpec,
  getSpecFiles as apiGetSpecFiles,
  getSpecFile as apiGetSpecFile,
  createSpec as apiCreateSpec,
  updateSpecFile as apiUpdateSpecFile,
  updateSpecSection as apiUpdateSpecSection,
  deleteSpec as apiDeleteSpec,
  generateSpecContent as apiGenerateSpecContent,
  approveSpec as apiApproveSpec,
  modifySpec as apiModifySpec,
  confirmSpec as apiConfirmSpec,
  cancelSpec as apiCancelSpec,
} from '@/api/spec.js'

export const useSpecStore = defineStore('spec', () => {
  // State
  const specs = ref([])
  const currentSpec = ref(null)
  const currentFiles = ref([])
  const currentFileContent = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const specList = computed(() => specs.value)
  const hasSpecs = computed(() => specs.value.length > 0)

  // Actions

  /**
   * 加载规格列表
   * @param {string} conversation_id - 对话ID
   */
  const loadSpecs = async (conversation_id) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiGetSpecs(conversation_id)
      specs.value = data
    } catch (err) {
      error.value = err.message
      console.error('加载规格列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 获取规格详情
   */
  const loadSpec = async (featureName) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiGetSpec(featureName)
      currentSpec.value = data
      return data
    } catch (err) {
      error.value = err.message
      console.error('加载规格详情失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 获取规格文件列表
   */
  const loadSpecFiles = async (featureName) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiGetSpecFiles(featureName)
      currentFiles.value = data
      return data
    } catch (err) {
      error.value = err.message
      console.error('加载文件列表失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 获取规格文件内容
   */
  const loadSpecFile = async (featureName, file) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiGetSpecFile(featureName, file)
      currentFileContent.value = data
      return data
    } catch (err) {
      error.value = err.message
      console.error('加载文件内容失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 创建规格
   */
  const createSpec = async (specData) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiCreateSpec(specData)
      specs.value.unshift(data)
      currentSpec.value = data
      return data
    } catch (err) {
      error.value = err.message
      console.error('创建规格失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新规格文件
   */
  const updateFile = async (featureName, file, fileData) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiUpdateSpecFile(featureName, file, fileData)
      if (currentSpec.value?.feature_name === featureName) {
        currentSpec.value = data
      }
      return data
    } catch (err) {
      error.value = err.message
      console.error('更新文件失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新规格章节
   */
  const updateSection = async (featureName, file, section, content) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiUpdateSpecSection(featureName, file, section, content)
      if (currentFileContent.value && currentSpec.value?.feature_name === featureName) {
        currentFileContent.value = data
      }
      return data
    } catch (err) {
      error.value = err.message
      console.error('更新章节失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 删除规格
   */
  const deleteSpec = async (featureName) => {
    try {
      isLoading.value = true
      error.value = null
      await apiDeleteSpec(featureName)
      specs.value = specs.value.filter(s => s.feature_name !== featureName)
      if (currentSpec.value?.feature_name === featureName) {
        currentSpec.value = null
        currentFiles.value = []
        currentFileContent.value = null
      }
    } catch (err) {
      error.value = err.message
      console.error('删除规格失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * AI生成规格内容
   */
  const generateContent = async (featureName) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiGenerateSpecContent(featureName)
      if (currentSpec.value?.feature_name === featureName) {
        currentSpec.value = data
      }
      return data
    } catch (err) {
      error.value = err.message
      console.error('生成内容失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 审批通过规格
   */
  const approveSpec = async (featureName) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiApproveSpec(featureName)
      if (currentSpec.value?.feature_name === featureName) {
        currentSpec.value = data
      }
      // 更新列表中的状态
      const index = specs.value.findIndex(s => s.feature_name === featureName)
      if (index !== -1) {
        specs.value[index] = data
      }
      return data
    } catch (err) {
      error.value = err.message
      console.error('审批规格失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 修改规格
   */
  const modifySpec = async (featureName, instruction) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiModifySpec(featureName, instruction)
      if (currentSpec.value?.feature_name === featureName) {
        currentSpec.value = data
      }
      // 更新列表中的状态
      const index = specs.value.findIndex(s => s.feature_name === featureName)
      if (index !== -1) {
        specs.value[index] = data
      }
      return data
    } catch (err) {
      error.value = err.message
      console.error('修改规格失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 确认规格
   */
  const confirmSpec = async (featureName, action) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiConfirmSpec(featureName, action)
      if (currentSpec.value?.feature_name === featureName) {
        currentSpec.value = data
      }
      // 更新列表中的状态
      const index = specs.value.findIndex(s => s.feature_name === featureName)
      if (index !== -1) {
        specs.value[index] = data
      }
      return data
    } catch (err) {
      error.value = err.message
      console.error('确认规格失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取消规格
   */
  const cancelSpec = async (featureName, reason) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiCancelSpec(featureName, reason)
      if (currentSpec.value?.feature_name === featureName) {
        currentSpec.value = data
      }
      // 更新列表中的状态
      const index = specs.value.findIndex(s => s.feature_name === featureName)
      if (index !== -1) {
        specs.value[index] = data
      }
      return data
    } catch (err) {
      error.value = err.message
      console.error('取消规格失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    specs,
    currentSpec,
    currentFiles,
    currentFileContent,
    isLoading,
    error,
    // Getters
    specList,
    hasSpecs,
    // Actions
    loadSpecs,
    loadSpec,
    loadSpecFiles,
    loadSpecFile,
    createSpec,
    updateFile,
    updateSection,
    deleteSpec,
    generateContent,
    approveSpec,
    modifySpec,
    confirmSpec,
    cancelSpec,
  }
})
