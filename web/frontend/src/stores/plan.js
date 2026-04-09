import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getPlans as apiGetPlans,
  getPlan as apiGetPlan,
  createPlan as apiCreatePlan,
  updatePlan as apiUpdatePlan,
  deletePlan as apiDeletePlan,
  updatePlanSection as apiUpdatePlanSection,
  generatePlanContent as apiGeneratePlanContent,
} from '@/api/plan.js'

export const usePlanStore = defineStore('plan', () => {
  // State
  const plans = ref([])
  const currentPlan = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const planList = computed(() => plans.value)
  const hasPlans = computed(() => plans.value.length > 0)

  // Actions

  /**
   * 加载规划列表
   * @param {string} conversationId - 对话ID
   */
  const loadPlans = async (conversationId) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiGetPlans(conversationId)
      plans.value = data
    } catch (err) {
      error.value = err.message
      console.error('加载规划列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 获取规划详情
   */
  const loadPlan = async (planId) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiGetPlan(planId)
      currentPlan.value = data
      return data
    } catch (err) {
      error.value = err.message
      console.error('加载规划详情失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 创建规划
   */
  const createPlan = async (planData) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiCreatePlan(planData)
      plans.value.unshift(data)
      currentPlan.value = data
      return data
    } catch (err) {
      error.value = err.message
      console.error('创建规划失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新规划
   */
  const updatePlan = async (planId, planData) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiUpdatePlan(planId, planData)
      const index = plans.value.findIndex(p => p.id === planId)
      if (index !== -1) {
        plans.value[index] = data
      }
      if (currentPlan.value?.id === planId) {
        currentPlan.value = data
      }
      return data
    } catch (err) {
      error.value = err.message
      console.error('更新规划失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 删除规划
   */
  const deletePlan = async (planId) => {
    try {
      isLoading.value = true
      error.value = null
      await apiDeletePlan(planId)
      plans.value = plans.value.filter(p => p.id !== planId)
      if (currentPlan.value?.id === planId) {
        currentPlan.value = null
      }
    } catch (err) {
      error.value = err.message
      console.error('删除规划失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新规划章节
   */
  const updateSection = async (planId, section, content) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiUpdatePlanSection(planId, section, content)
      if (currentPlan.value?.id === planId) {
        currentPlan.value = data
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
   * AI生成规划内容
   */
  const generateContent = async (planId) => {
    try {
      isLoading.value = true
      error.value = null
      const data = await apiGeneratePlanContent(planId)
      if (currentPlan.value?.id === planId) {
        currentPlan.value = data
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

  return {
    // State
    plans,
    currentPlan,
    isLoading,
    error,
    // Getters
    planList,
    hasPlans,
    // Actions
    loadPlans,
    loadPlan,
    createPlan,
    updatePlan,
    deletePlan,
    updateSection,
    generateContent,
  }
})
