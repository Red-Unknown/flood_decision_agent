<template>
  <div class="task-execution-list" :class="{ 'is-collapsed': isCollapsed }">
    <!-- 头部摘要信息 -->
    <div class="execution-header" @click="toggleCollapse">
      <div class="header-left">
        <el-icon class="collapse-icon">
          <ArrowDown v-if="isCollapsed" />
          <ArrowUp v-else />
        </el-icon>
        <span class="header-title">任务执行过程</span>
        <el-tag
          :type="getStatusType(executionState.status)"
          size="small"
          class="status-tag"
        >
          {{ getStatusLabel(executionState.status) }}
        </el-tag>
      </div>
      <div class="header-right">
        <span class="progress-text">
          {{ completedTasksCount }}/{{ tasks.length }}
        </span>
        <el-progress
          :percentage="Math.round(executionState.currentProgress * 100)"
          :stroke-width="6"
          :show-text="false"
          class="header-progress"
          :status="getProgressStatus()"
        />
      </div>
    </div>

    <!-- 任务列表 -->
    <div v-show="!isCollapsed" class="tasks-container">
      <!-- 生成阶段指示器 -->
      <div v-if="isGenerating" class="generation-stage">
        <el-steps :active="getStageStep()" finish-status="success" simple>
          <el-step title="意图理解" />
          <el-step title="任务分解" />
          <el-step title="链路优化" />
          <el-step title="构建任务图" />
        </el-steps>
        <p v-if="executionState.stageMessage" class="stage-message">
          <el-icon><Loading /></el-icon>
          {{ executionState.stageMessage }}
        </p>
      </div>

      <!-- 任务列表 -->
      <div v-if="tasks.length > 0" class="tasks-list">
        <div
          v-for="task in tasks"
          :key="task.task_id"
          class="task-item"
          :class="getTaskItemClass(task)"
          @click="toggleTaskDetail(task.task_id)"
        >
          <!-- 任务基本信息 -->
          <div class="task-main">
            <div class="task-status-icon">
              <el-icon v-if="task.status === 'completed'" class="status-success"><CircleCheck /></el-icon>
              <el-icon v-else-if="task.status === 'failed'" class="status-error"><CircleClose /></el-icon>
              <el-icon v-else-if="task.status === 'running'" class="status-running"><Loading /></el-icon>
              <el-icon v-else class="status-pending"><Timer /></el-icon>
            </div>
            <div class="task-info">
              <span class="task-name">{{ task.task_name }}</span>
              <span class="task-type">{{ getTaskTypeLabel(task.task_type) }}</span>
            </div>
            <div class="task-meta">
              <span v-if="task.durationMs" class="task-duration">
                {{ formatDuration(task.durationMs) }}
              </span>
              <el-icon class="expand-icon">
                <ArrowDown v-if="expandedTasks.includes(task.task_id)" />
                <ArrowRight v-else />
              </el-icon>
            </div>
          </div>

          <!-- 任务详情（展开时显示） -->
          <div
            v-if="expandedTasks.includes(task.task_id)"
            class="task-detail"
          >
            <!-- 任务依赖 -->
            <div v-if="task.dependencies && task.dependencies.length > 0" class="detail-section">
              <span class="detail-label">依赖任务:</span>
              <el-tag
                v-for="dep in task.dependencies"
                :key="dep"
                size="small"
                class="dependency-tag"
              >
                {{ getTaskNameById(dep) }}
              </el-tag>
            </div>

            <!-- 执行详情（detail 字段） -->
            <div v-if="task.detail" class="detail-section">
              <div v-if="task.detail.message" class="detail-message">
                <el-icon><InfoFilled /></el-icon>
                {{ task.detail.message }}
              </div>
              <el-progress
                v-if="task.detail.progress !== undefined"
                :percentage="Math.round(task.detail.progress * 100)"
                :stroke-width="4"
                class="detail-progress"
              />

              <!-- 多模态内容预留 -->
              <div v-if="task.detail.modalities" class="modalities-content">
                <!-- 文本模态 -->
                <div
                  v-if="task.detail.modalities.text?.content"
                  class="modality-text"
                >
                  <pre>{{ task.detail.modalities.text.content }}</pre>
                </div>
                <!-- 图片模态（预留） -->
                <div
                  v-if="task.detail.modalities.image"
                  class="modality-image"
                >
                  <el-image
                    :src="task.detail.modalities.image.url"
                    :preview-src-list="[task.detail.modalities.image.url]"
                    fit="contain"
                  />
                  <p class="image-description">
                    {{ task.detail.modalities.image.description }}
                  </p>
                </div>
                <!-- 图表模态（预留） -->
                <div
                  v-if="task.detail.modalities.chart"
                  class="modality-chart"
                >
                  <p>图表类型: {{ task.detail.modalities.chart.type }}</p>
                </div>
                <!-- 表格模态（预留） -->
                <div
                  v-if="task.detail.modalities.table"
                  class="modality-table"
                >
                  <el-table
                    :data="task.detail.modalities.table.rows"
                    border
                    size="small"
                  >
                    <el-table-column
                      v-for="(header, index) in task.detail.modalities.table.headers"
                      :key="index"
                      :prop="index.toString()"
                      :label="header"
                    />
                  </el-table>
                </div>
              </div>
            </div>

            <!-- 任务结果 -->
            <div v-if="task.result" class="detail-section result-section">
              <!-- 成功状态 -->
              <div v-if="task.result.status === 'success'" class="result-success">
                <div class="result-summary">
                  <el-icon><SuccessFilled /></el-icon>
                  <span>任务执行成功</span>
                  <span v-if="task.result.metrics" class="result-metrics">
                    ({{ formatDuration(task.result.metrics.elapsed_time_ms) }})
                  </span>
                </div>
                <!-- 工具调用输出 -->
                <div v-if="task.result.output" class="result-output">
                  <div class="output-label">工具调用结果:</div>
                  <pre class="output-content">{{ formatOutput(task.result.output) }}</pre>
                </div>
                <!-- 使用的工具列表 -->
                <div v-if="task.result.metrics?.tools_used" class="tools-used">
                  <span class="tools-label">使用工具:</span>
                  <el-tag
                    v-for="tool in task.result.metrics.tools_used"
                    :key="tool"
                    size="small"
                    class="tool-tag"
                  >
                    {{ tool }}
                  </el-tag>
                </div>
              </div>
              <!-- 失败状态 -->
              <div v-else-if="task.result.status === 'error' || task.result.error" class="result-error">
                <div class="result-summary">
                  <el-icon><CircleClose /></el-icon>
                  <span>任务执行失败</span>
                </div>
                <div v-if="task.result.error" class="error-message">
                  {{ task.result.error }}
                </div>
              </div>
              <!-- 旧格式兼容 -->
              <div v-else-if="task.result.summary" class="result-legacy">
                <div class="result-summary">
                  <el-icon><SuccessFilled /></el-icon>
                  {{ task.result.summary }}
                </div>
                <div v-if="task.result.output_preview" class="result-preview">
                  <pre>{{ task.result.output_preview }}</pre>
                </div>
              </div>
              <!-- 原始数据展示 -->
              <div v-else class="result-raw">
                <div class="output-label">执行结果:</div>
                <pre class="output-content">{{ formatOutput(task.result) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!isGenerating" class="empty-tasks">
        <el-empty description="暂无任务" />
      </div>
    </div>

    <!-- 执行统计 -->
    <div v-if="!isCollapsed && tasks.length > 0" class="execution-summary">
      <div class="summary-item">
        <span class="summary-label">待处理:</span>
        <el-tag size="small">{{ pendingTasksCount }}</el-tag>
      </div>
      <div class="summary-item">
        <span class="summary-label">运行中:</span>
        <el-tag type="warning" size="small">{{ runningTasksCount }}</el-tag>
      </div>
      <div class="summary-item">
        <span class="summary-label">已完成:</span>
        <el-tag type="success" size="small">{{ completedTasksCount }}</el-tag>
      </div>
      <div v-if="failedTasksCount > 0" class="summary-item">
        <span class="summary-label">失败:</span>
        <el-tag type="danger" size="small">{{ failedTasksCount }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  ArrowDown,
  ArrowUp,
  ArrowRight,
  Loading,
  CircleCheck,
  CircleClose,
  Timer,
  InfoFilled,
  SuccessFilled,
} from '@element-plus/icons-vue'

const props = defineProps({
  /** 执行状态 */
  executionState: {
    type: Object,
    required: true,
    default: () => ({
      status: 'idle',
      currentProgress: 0,
      currentStage: null,
      stageMessage: '',
    }),
  },
  /** 任务列表 */
  tasks: {
    type: Array,
    default: () => [],
  },
  /** 是否正在生成 */
  isGenerating: {
    type: Boolean,
    default: false,
  },
  /** 是否正在执行 */
  isExecuting: {
    type: Boolean,
    default: false,
  },
  /** 待处理任务数 */
  pendingTasksCount: {
    type: Number,
    default: 0,
  },
  /** 运行中任务数 */
  runningTasksCount: {
    type: Number,
    default: 0,
  },
  /** 已完成任务数 */
  completedTasksCount: {
    type: Number,
    default: 0,
  },
  /** 失败任务数 */
  failedTasksCount: {
    type: Number,
    default: 0,
  },
  /** 默认是否折叠 */
  defaultCollapsed: {
    type: Boolean,
    default: false,
  },
})

// State
const isCollapsed = ref(props.defaultCollapsed)
const expandedTasks = ref([])

// Methods
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleTaskDetail = (taskId) => {
  const index = expandedTasks.value.indexOf(taskId)
  if (index > -1) {
    expandedTasks.value.splice(index, 1)
  } else {
    expandedTasks.value.push(taskId)
  }
}

const getStatusType = (status) => {
  const statusMap = {
    idle: 'info',
    generating: 'warning',
    executing: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  }
  return statusMap[status] || 'info'
}

const getStatusLabel = (status) => {
  const labelMap = {
    idle: '空闲',
    generating: '生成中',
    executing: '执行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  }
  return labelMap[status] || status
}

const getProgressStatus = () => {
  if (props.executionState.status === 'failed') return 'exception'
  if (props.executionState.status === 'completed') return 'success'
  return ''
}

const getTaskItemClass = (task) => {
  return {
    'is-pending': task.status === 'pending',
    'is-running': task.status === 'running',
    'is-completed': task.status === 'completed',
    'is-failed': task.status === 'failed',
    'is-cancelled': task.status === 'cancelled',
  }
}

const getTaskTypeLabel = (type) => {
  const typeMap = {
    data_collection: '数据采集',
    analysis: '分析',
    calculation: '计算',
    prediction: '预测',
    report_generation: '报告生成',
    visualization: '可视化',
    decision: '决策',
  }
  return typeMap[type] || type
}

const getTaskNameById = (taskId) => {
  const task = props.tasks.find(t => t.task_id === taskId)
  return task ? task.task_name : taskId
}

const formatDuration = (ms) => {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${(ms / 60000).toFixed(1)}m`
}

const formatOutput = (output) => {
  if (output === null || output === undefined) return ''
  if (typeof output === 'string') return output
  try {
    return JSON.stringify(output, null, 2)
  } catch (e) {
    return String(output)
  }
}

const getStageStep = () => {
  const stageMap = {
    intent_understanding: 0,
    task_decomposition: 1,
    chain_optimization: 2,
    task_graph_building: 3,
  }
  return stageMap[props.executionState.currentStage] || 0
}
</script>

<style scoped lang="scss">
.task-execution-list {
  background: var(--bg-white);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  margin: 16px 0;
}

.execution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-color);
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: var(--el-color-primary-light-9);
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;

    .collapse-icon {
      font-size: 14px;
      color: var(--text-secondary);
    }

    .header-title {
      font-weight: 500;
      font-size: 14px;
    }

    .status-tag {
      margin-left: 8px;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;

    .progress-text {
      font-size: 12px;
      color: var(--text-secondary);
    }

    .header-progress {
      width: 100px;
    }
  }
}

.tasks-container {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.generation-stage {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--border-color);

  .stage-message {
    margin-top: 12px;
    color: var(--text-secondary);
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 6px;

    .el-icon {
      animation: rotate 1s linear infinite;
    }
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
  transition: all 0.2s;

  &:hover {
    border-color: var(--el-color-primary-light-5);
  }

  &.is-running {
    border-color: var(--el-color-warning);
    background: var(--el-color-warning-light-9);
  }

  &.is-completed {
    border-color: var(--el-color-success-light-5);
  }

  &.is-failed {
    border-color: var(--el-color-danger);
    background: var(--el-color-danger-light-9);
  }
}

.task-main {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  gap: 12px;
}

.task-status-icon {
  font-size: 18px;

  .status-success {
    color: var(--el-color-success);
  }

  .status-error {
    color: var(--el-color-danger);
  }

  .status-running {
    color: var(--el-color-warning);
    animation: rotate 1s linear infinite;
  }

  .status-pending {
    color: var(--text-secondary);
  }
}

.task-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;

  .task-name {
    font-weight: 500;
    font-size: 14px;
  }

  .task-type {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;

  .task-duration {
    font-size: 12px;
    color: var(--text-secondary);
  }

  .expand-icon {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.task-detail {
  padding: 12px 16px;
  background: var(--bg-color);
  border-top: 1px solid var(--border-color);
}

.detail-section {
  margin-bottom: 12px;

  &:last-child {
    margin-bottom: 0;
  }
}

.detail-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-right: 8px;
}

.dependency-tag {
  margin-right: 4px;
}

.detail-message {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-regular);
  margin-bottom: 8px;

  .el-icon {
    color: var(--el-color-primary);
  }
}

.detail-progress {
  margin-top: 8px;
}

.modalities-content {
  margin-top: 12px;

  .modality-text {
    pre {
      background: var(--bg-white);
      padding: 12px;
      border-radius: 4px;
      font-size: 13px;
      overflow-x: auto;
      max-height: 200px;
      overflow-y: auto;
    }
  }

  .modality-image {
    .el-image {
      max-width: 100%;
      border-radius: 4px;
    }

    .image-description {
      margin-top: 8px;
      font-size: 12px;
      color: var(--text-secondary);
    }
  }

  .modality-table {
    margin-top: 8px;
  }
}

.result-section {
  padding-top: 12px;
  border-top: 1px dashed var(--border-color);

  .result-summary {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--el-color-success);
    margin-bottom: 8px;

    .el-icon {
      font-size: 16px;
    }
  }

  .result-preview {
    pre {
      background: var(--bg-white);
      padding: 12px;
      border-radius: 4px;
      font-size: 12px;
      overflow-x: auto;
      max-height: 150px;
      overflow-y: auto;
    }
  }

  // 成功结果样式
  .result-success {
    .result-summary {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: var(--el-color-success);
      margin-bottom: 8px;

      .el-icon {
        font-size: 16px;
      }

      .result-metrics {
        color: var(--text-secondary);
        font-size: 12px;
        margin-left: auto;
      }
    }

    .result-output {
      margin-bottom: 12px;

      .output-label {
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 4px;
      }

      .output-content {
        background: var(--bg-white);
        padding: 12px;
        border-radius: 4px;
        font-size: 12px;
        overflow-x: auto;
        max-height: 200px;
        overflow-y: auto;
        margin: 0;
        white-space: pre-wrap;
        word-break: break-word;
      }
    }

    .tools-used {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;

      .tools-label {
        font-size: 12px;
        color: var(--text-secondary);
      }

      .tool-tag {
        margin-right: 4px;
      }
    }
  }

  // 失败结果样式
  .result-error {
    .result-summary {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: var(--el-color-danger);
      margin-bottom: 8px;

      .el-icon {
        font-size: 16px;
      }
    }

    .error-message {
      background: var(--el-color-danger-light-9);
      border: 1px solid var(--el-color-danger-light-5);
      border-radius: 4px;
      padding: 8px 12px;
      font-size: 12px;
      color: var(--el-color-danger);
    }
  }

  // 原始数据样式
  .result-raw {
    .output-label {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }

    .output-content {
      background: var(--bg-white);
      padding: 12px;
      border-radius: 4px;
      font-size: 12px;
      overflow-x: auto;
      max-height: 200px;
      overflow-y: auto;
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
    }
  }
}

.empty-tasks {
  padding: 24px 0;
}

.execution-summary {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 12px 16px;
  background: var(--bg-color);
  border-top: 1px solid var(--border-color);

  .summary-item {
    display: flex;
    align-items: center;
    gap: 6px;

    .summary-label {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}
</style>
