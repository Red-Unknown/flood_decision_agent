import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 决策链执行状态管理 Store
 * 
 * 根据 chain-generation-api.md 定义，管理决策链生成和执行的状态
 */
export const useChainExecutionStore = defineStore('chainExecution', () => {
  // ==================== State ====================
  
  /** 当前执行状态 */
  const executionState = ref({
    executionId: null,
    generationId: null,
    mode: null, // 'normal' | 'plan' | 'spec'
    status: 'idle', // 'idle' | 'generating' | 'executing' | 'completed' | 'failed' | 'cancelled'
    currentProgress: 0,
    currentStage: null,
    stageMessage: '',
  })

  /** 任务列表 */
  const tasks = ref([])

  /** 执行错误信息 */
  const error = ref(null)

  /** 是否正在生成决策链 */
  const isGenerating = ref(false)

  /** 是否正在执行 */
  const isExecuting = ref(false)

  // ==================== Getters ====================

  /** 是否有正在进行的执行 */
  const hasActiveExecution = computed(() => {
    return executionState.value.status === 'generating' || 
           executionState.value.status === 'executing'
  })

  /** 执行是否完成 */
  const isCompleted = computed(() => {
    return executionState.value.status === 'completed'
  })

  /** 执行是否失败 */
  const isFailed = computed(() => {
    return executionState.value.status === 'failed'
  })

  /** 待处理任务数 */
  const pendingTasksCount = computed(() => {
    return tasks.value.filter(t => t.status === 'pending').length
  })

  /** 运行中任务数 */
  const runningTasksCount = computed(() => {
    return tasks.value.filter(t => t.status === 'running').length
  })

  /** 已完成任务数 */
  const completedTasksCount = computed(() => {
    return tasks.value.filter(t => t.status === 'completed').length
  })

  /** 失败任务数 */
  const failedTasksCount = computed(() => {
    return tasks.value.filter(t => t.status === 'failed').length
  })

  /** 当前运行的任务 */
  const currentRunningTask = computed(() => {
    return tasks.value.find(t => t.status === 'running')
  })

  // ==================== Actions ====================

  /**
   * 重置执行状态
   */
  const resetExecution = () => {
    executionState.value = {
      executionId: null,
      generationId: null,
      mode: null,
      status: 'idle',
      currentProgress: 0,
      currentStage: null,
      stageMessage: '',
    }
    tasks.value = []
    error.value = null
    isGenerating.value = false
    isExecuting.value = false
  }

  /**
   * 开始决策链生成
   * @param {string} mode - 生成模式: 'normal' | 'plan' | 'spec'
   * @param {string} generationId - 生成任务ID
   */
  const startGeneration = (mode, generationId) => {
    executionState.value.mode = mode
    executionState.value.generationId = generationId
    executionState.value.status = 'generating'
    executionState.value.currentProgress = 0
    isGenerating.value = true
    error.value = null
  }

  /**
   * 更新生成阶段
   * @param {Object} stageData - 阶段数据
   */
  const updateGenerationStage = (stageData) => {
    executionState.value.currentStage = stageData.stage
    executionState.value.stageMessage = stageData.message
    executionState.value.currentProgress = stageData.progress
  }

  /**
   * 任务图生成完成
   * @param {Object} data - 任务图数据
   */
  const setTaskGraphGenerated = (data) => {
    executionState.value.generationId = data.generation_id
    executionState.value.currentProgress = 1.0
    
    // 初始化任务列表
    tasks.value = data.tasks.map(task => ({
      ...task,
      detail: null,
      result: null,
      durationMs: null,
    }))
    
    isGenerating.value = false
  }

  /**
   * 决策链生成完成
   * @param {Object} data - 生成完成数据
   */
  const setChainGenerated = (data) => {
    executionState.value.generationId = data.generation_id
    isGenerating.value = false
  }

  /**
   * 开始执行
   * @param {Object} data - 执行开始数据
   */
  const startExecution = (data) => {
    executionState.value.executionId = data.execution_id
    executionState.value.status = 'executing'
    executionState.value.currentProgress = 0
    isExecuting.value = true
  }

  /**
   * 更新任务状态
   * @param {Object} data - 任务更新数据
   */
  const updateTaskStatus = (data) => {
    const taskIndex = tasks.value.findIndex(t => t.task_id === data.task_id)
    
    if (taskIndex !== -1) {
      tasks.value[taskIndex] = {
        ...tasks.value[taskIndex],
        status: data.status,
        durationMs: data.duration_ms,
        result: data.result,
        detail: data.detail,
      }
    }
  }

  /**
   * 更新执行进度
   * @param {Object} data - 进度数据
   */
  const updateExecutionProgress = (data) => {
    executionState.value.currentProgress = data.progress
  }

  /**
   * 执行完成
   * @param {Object} data - 执行完成数据
   */
  const setExecutionComplete = (data) => {
    executionState.value.status = data.success ? 'completed' : 'failed'
    executionState.value.currentProgress = 1.0
    isExecuting.value = false
  }

  /**
   * 执行错误
   * @param {Object} errorData - 错误数据
   */
  const setExecutionError = (errorData) => {
    executionState.value.status = 'failed'
    error.value = errorData
    isExecuting.value = false
    isGenerating.value = false
  }

  /**
   * 操作取消
   */
  const setOperationCancelled = () => {
    executionState.value.status = 'cancelled'
    isExecuting.value = false
    isGenerating.value = false
  }

  /**
   * 清除错误
   */
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    executionState,
    tasks,
    error,
    isGenerating,
    isExecuting,
    
    // Getters
    hasActiveExecution,
    isCompleted,
    isFailed,
    pendingTasksCount,
    runningTasksCount,
    completedTasksCount,
    failedTasksCount,
    currentRunningTask,
    
    // Actions
    resetExecution,
    startGeneration,
    updateGenerationStage,
    setTaskGraphGenerated,
    setChainGenerated,
    startExecution,
    updateTaskStatus,
    updateExecutionProgress,
    setExecutionComplete,
    setExecutionError,
    setOperationCancelled,
    clearError,
  }
})
