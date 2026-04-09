import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  detectMode as apiDetectMode,
  getSessionStatus as apiGetSessionStatus,
  resumeSession as apiResumeSession,
  cancelPlan as apiCancelPlan,
  confirmPlan as apiConfirmPlan,
  modifyPlan as apiModifyPlan,
} from '@/api/mode.js'

export const useSessionStore = defineStore('session', () => {
  // State
  const sessionId = ref(null)
  const mode = ref(null) // 'simple' | 'plan' | 'spec' | null
  const stage = ref('') // 'simple_answer' | 'planning' | 'spec_design' | 'executing' | 'awaiting_confirmation'
  const status = ref('idle') // 'idle' | 'processing' | 'awaiting_confirmation' | 'completed' | 'cancelled'
  const currentDocument = ref(null) // { type: 'plan' | 'spec', id: string, data: object }
  const canResume = ref(false)
  const isLoading = ref(false)
  const error = ref(null)

  // 模式检测相关
  const detectedMode = ref(null)
  const detectionConfidence = ref(0)
  const detectionMetrics = ref(null)

  // Getters
  const isInPlanMode = computed(() => mode.value === 'plan')
  const isInSpecMode = computed(() => mode.value === 'spec')
  const isInSimpleMode = computed(() => mode.value === 'simple')
  const isProcessing = computed(() => status.value === 'processing')
  const isAwaitingConfirmation = computed(() => status.value === 'awaiting_confirmation')
  const hasActiveSession = computed(() => sessionId.value !== null)
  const currentPlanId = computed(() =>
    currentDocument.value?.type === 'plan' ? currentDocument.value.id : null
  )
  const currentSpecId = computed(() =>
    currentDocument.value?.type === 'spec' ? currentDocument.value.id : null
  )

  // Actions

  /**
   * 检测用户输入的模式
   */
  const detectMode = async (userInput) => {
    try {
      const result = await apiDetectMode(userInput)
      detectedMode.value = result.recommended_mode
      detectionConfidence.value = result.confidence
      detectionMetrics.value = result.metrics
      return result
    } catch (err) {
      console.error('模式检测失败:', err)
      // 失败时默认使用 simple 模式
      detectedMode.value = 'simple'
      detectionConfidence.value = 0
      return { recommended_mode: 'simple', confidence: 0 }
    }
  }

  /**
   * 设置模式（手动覆盖）
   */
  const setMode = (newMode) => {
    mode.value = newMode
  }

  /**
   * 开始新会话
   */
  const startSession = (newSessionId, sessionMode, sessionData = null) => {
    sessionId.value = newSessionId
    mode.value = sessionMode
    status.value = 'processing'
    if (sessionData) {
      currentDocument.value = sessionData
    }
    // 保存到 localStorage 用于断点续传
    saveSessionToStorage()
  }

  /**
   * 更新会话状态
   */
  const updateSessionState = (newState) => {
    if (newState.session_id) sessionId.value = newState.session_id
    if (newState.mode) mode.value = newState.mode
    if (newState.stage) stage.value = newState.stage
    if (newState.status) status.value = newState.status
    if (newState.current_document) currentDocument.value = newState.current_document
    if (newState.can_resume !== undefined) canResume.value = newState.can_resume
    saveSessionToStorage()
  }

  /**
   * 获取会话状态
   */
  const fetchSessionStatus = async (sid = null) => {
    const id = sid || sessionId.value
    if (!id) return null

    try {
      isLoading.value = true
      const result = await apiGetSessionStatus(id)
      updateSessionState(result)
      return result
    } catch (err) {
      error.value = err.message
      console.error('获取会话状态失败:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 恢复会话
   */
  const resumeSession = async (sid = null) => {
    const id = sid || sessionId.value
    if (!id) {
      // 尝试从 localStorage 恢复
      const savedSession = loadSessionFromStorage()
      if (savedSession?.session_id) {
        return resumeSession(savedSession.session_id)
      }
      return null
    }

    try {
      isLoading.value = true
      const result = await apiResumeSession(id)
      updateSessionState({
        session_id: id,
        mode: result.resumed_from?.mode || mode.value,
        stage: result.resumed_from?.stage || stage.value,
        status: 'awaiting_confirmation',
        current_document: result.current_data,
        can_resume: true,
      })
      return result
    } catch (err) {
      error.value = err.message
      console.error('恢复会话失败:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 检查是否有可恢复的会话
   */
  const checkResumableSession = () => {
    const saved = loadSessionFromStorage()
    if (saved?.session_id && saved?.can_resume) {
      sessionId.value = saved.session_id
      mode.value = saved.mode
      stage.value = saved.stage
      status.value = saved.status
      currentDocument.value = saved.current_document
      canResume.value = true
      return saved
    }
    return null
  }

  /**
   * 取消当前任务
   */
  const cancelTask = async (reason = 'manual_cancel') => {
    if (!currentDocument.value) return

    try {
      isLoading.value = true
      if (currentDocument.value.type === 'plan') {
        await apiCancelPlan(currentDocument.value.id, reason)
      }
      // Spec 取消类似...

      status.value = 'cancelled'
      canResume.value = true
      saveSessionToStorage()
    } catch (err) {
      error.value = err.message
      console.error('取消任务失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 确认 Plan 文档
   */
  const confirmPlanDocument = async (action = 'proceed') => {
    if (!currentPlanId.value) return

    try {
      isLoading.value = true
      const result = await apiConfirmPlan(currentPlanId.value, action)
      status.value = 'completed'
      stage.value = 'executing'
      canResume.value = false
      saveSessionToStorage()
      return result
    } catch (err) {
      error.value = err.message
      console.error('确认规划失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 自然语言修改 Plan
   */
  const modifyPlanByInstruction = async (instruction, section = null) => {
    if (!currentPlanId.value) return

    try {
      isLoading.value = true
      const result = await apiModifyPlan(currentPlanId.value, instruction, section)
      // 更新当前文档内容
      if (currentDocument.value && result.updated_content) {
        currentDocument.value.data = {
          ...currentDocument.value.data,
          [result.modified_section || section]: result.updated_content,
        }
      }
      return result
    } catch (err) {
      error.value = err.message
      console.error('修改规划失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 重置会话
   */
  const resetSession = () => {
    sessionId.value = null
    mode.value = null
    stage.value = ''
    status.value = 'idle'
    currentDocument.value = null
    canResume.value = false
    detectedMode.value = null
    detectionConfidence.value = 0
    detectionMetrics.value = null
    clearSessionStorage()
  }

  /**
   * 清除错误
   */
  const clearError = () => {
    error.value = null
  }

  // 本地存储辅助函数
  const SESSION_STORAGE_KEY = 'flood_agent_session'

  const saveSessionToStorage = () => {
    const data = {
      session_id: sessionId.value,
      mode: mode.value,
      stage: stage.value,
      status: status.value,
      current_document: currentDocument.value,
      can_resume: canResume.value,
      saved_at: Date.now(),
    }
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(data))
  }

  const loadSessionFromStorage = () => {
    try {
      const data = localStorage.getItem(SESSION_STORAGE_KEY)
      if (data) {
        const parsed = JSON.parse(data)
        // 检查是否过期（24小时）
        if (Date.now() - parsed.saved_at < 24 * 60 * 60 * 1000) {
          return parsed
        }
      }
    } catch (e) {
      console.error('读取会话存储失败:', e)
    }
    return null
  }

  const clearSessionStorage = () => {
    localStorage.removeItem(SESSION_STORAGE_KEY)
  }

  return {
    // State
    sessionId,
    mode,
    stage,
    status,
    currentDocument,
    canResume,
    isLoading,
    error,
    detectedMode,
    detectionConfidence,
    detectionMetrics,
    // Getters
    isInPlanMode,
    isInSpecMode,
    isInSimpleMode,
    isProcessing,
    isAwaitingConfirmation,
    hasActiveSession,
    currentPlanId,
    currentSpecId,
    // Actions
    detectMode,
    setMode,
    startSession,
    updateSessionState,
    fetchSessionStatus,
    resumeSession,
    checkResumableSession,
    cancelTask,
    confirmPlanDocument,
    modifyPlanByInstruction,
    resetSession,
    clearError,
  }
})
