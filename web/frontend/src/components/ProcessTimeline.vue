<template>
  <div class="process-timeline">
    <div class="timeline-header">
      <span class="timeline-title">🔄 任务执行过程</span>
      <div class="timeline-actions">
        <el-button
          v-if="hasExpandableEvents"
          link
          size="small"
          @click="toggleAll"
        >
          {{ allExpanded ? '全部折叠' : '全部展开' }}
        </el-button>
        <el-button link size="small" @click="refreshEvents">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="timeline-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="events.length === 0" class="timeline-empty">
      <el-empty description="暂无过程性数据" :image-size="60" />
    </div>

    <div v-else class="timeline-content">
      <div
        v-for="(event, index) in sortedEvents"
        :key="index"
        class="timeline-item"
        :class="{ expanded: expandedEvents[index] }"
      >
        <div class="timeline-marker" :class="getStageClass(event.stage)">
          <el-icon :size="16">
            <component :is="getStageIcon(event.stage)" />
          </el-icon>
        </div>

        <div class="timeline-card" @click="toggleEvent(index)">
          <div class="timeline-card-header">
            <span class="event-message">{{ event.data.message }}</span>
            <span class="event-time">{{ formatTime(event.timestamp) }}</span>
            <el-icon class="expand-icon" :class="{ rotated: expandedEvents[index] }">
              <ArrowDown />
            </el-icon>
          </div>

          <div v-if="expandedEvents[index]" class="timeline-card-body">
            <!-- 任务列表 -->
            <div v-if="event.data.tasks" class="event-tasks">
              <div class="section-title">任务列表 ({{ event.data.total_count }}个)</div>
              <div class="task-list">
                <div
                  v-for="task in event.data.tasks"
                  :key="task.task_id"
                  class="task-item"
                >
                  <span class="task-status" :class="task.status">●</span>
                  <span class="task-name">{{ task.task_name }}</span>
                  <span class="task-type">({{ task.task_type }})</span>
                  <span v-if="task.dependencies.length" class="task-deps">
                    依赖: {{ task.dependencies.join(', ') }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Agent调用 -->
            <div v-if="event.stage === 'agent_called'" class="event-agent-call">
              <div class="agent-flow">
                <span class="agent caller">{{ event.data.caller_agent }}</span>
                <el-icon class="flow-arrow"><Right /></el-icon>
                <span class="agent callee">{{ event.data.callee_agent }}</span>
              </div>
              <div v-if="event.data.input_summary" class="agent-input">
                输入: {{ event.data.input_summary }}
              </div>
              <div v-if="event.data.output_summary" class="agent-output">
                输出: {{ event.data.output_summary }}
              </div>
            </div>

            <!-- 节点执行详情 -->
            <div v-if="event.stage === 'node_completed' || event.stage === 'node_failed'" class="event-node-details">
              <div class="detail-row">
                <span class="detail-label">任务ID:</span>
                <span class="detail-value">{{ event.data.node_id }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">执行Agent:</span>
                <span class="detail-value">{{ event.data.agent_id }}</span>
              </div>
              <div v-if="event.data.duration_ms" class="detail-row">
                <span class="detail-label">耗时:</span>
                <span class="detail-value">{{ formatDuration(event.data.duration_ms) }}</span>
              </div>
              <div v-if="event.data.output_summary" class="detail-row">
                <span class="detail-label">输出:</span>
                <span class="detail-value">{{ event.data.output_summary }}</span>
              </div>
              <div v-if="event.data.error_message" class="detail-row error">
                <span class="detail-label">错误:</span>
                <span class="detail-value">{{ event.data.error_message }}</span>
              </div>
            </div>

            <!-- 执行统计 -->
            <div v-if="event.data.execution_summary" class="event-summary">
              <div class="section-title">执行统计</div>
              <div class="summary-stats">
                <div class="stat-item">
                  <span class="stat-label">总任务:</span>
                  <span class="stat-value">{{ event.data.execution_summary.total_tasks }}</span>
                </div>
                <div class="stat-item success">
                  <span class="stat-label">成功:</span>
                  <span class="stat-value">{{ event.data.execution_summary.completed_tasks }}</span>
                </div>
                <div v-if="event.data.execution_summary.failed_tasks > 0" class="stat-item error">
                  <span class="stat-label">失败:</span>
                  <span class="stat-value">{{ event.data.execution_summary.failed_tasks }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总耗时:</span>
                  <span class="stat-value">{{ formatDuration(event.data.execution_summary.total_duration_ms) }}</span>
                </div>
              </div>
            </div>

            <!-- 原始数据（调试用，可折叠） -->
            <div class="raw-data-section">
              <el-button link size="small" @click.stop="showRawData[index] = !showRawData[index]">
                {{ showRawData[index] ? '隐藏' : '显示' }}原始数据
              </el-button>
              <pre v-if="showRawData[index]" class="raw-data">{{ JSON.stringify(event.data, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  Refresh, ArrowDown, Right, CircleCheck, CircleClose,
  Loading, InfoFilled, List, Connection, Timer
} from '@element-plus/icons-vue'

const props = defineProps({
  events: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const expandedEvents = ref({})
const showRawData = ref({})

// 按时间排序的事件
const sortedEvents = computed(() => {
  return [...props.events].sort((a, b) => a.timestamp - b.timestamp)
})

// 是否有可展开的事件
const hasExpandableEvents = computed(() => {
  return props.events.some(e =>
    e.data.tasks ||
    e.data.execution_summary ||
    e.stage === 'agent_called' ||
    e.stage === 'node_completed' ||
    e.stage === 'node_failed'
  )
})

// 是否全部展开
const allExpanded = computed(() => {
  const expandableIndices = sortedEvents.value
    .map((e, i) => hasExpandableContent(e) ? i : -1)
    .filter(i => i !== -1)
  return expandableIndices.every(i => expandedEvents.value[i])
})

// 判断事件是否有可展开的内容
const hasExpandableContent = (event) => {
  return event.data.tasks ||
    event.data.execution_summary ||
    event.stage === 'agent_called' ||
    event.stage === 'node_completed' ||
    event.stage === 'node_failed'
}

// 获取阶段样式类
const getStageClass = (stage) => {
  const classMap = {
    'task_accepted': 'info',
    'task_list_generated': 'info',
    'node_started': 'warning',
    'node_completed': 'success',
    'node_failed': 'error',
    'agent_called': 'info',
    'pipeline_completed': 'success'
  }
  return classMap[stage] || 'info'
}

// 获取阶段图标
const getStageIcon = (stage) => {
  const iconMap = {
    'task_accepted': InfoFilled,
    'task_list_generated': List,
    'node_started': Timer,
    'node_completed': CircleCheck,
    'node_failed': CircleClose,
    'agent_called': Connection,
    'pipeline_completed': CircleCheck
  }
  return iconMap[stage] || InfoFilled
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// 格式化耗时
const formatDuration = (ms) => {
  if (!ms) return '-'
  if (ms < 1000) return `${ms.toFixed(0)}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

// 切换事件展开/折叠
const toggleEvent = (index) => {
  if (hasExpandableContent(sortedEvents.value[index])) {
    expandedEvents.value[index] = !expandedEvents.value[index]
  }
}

// 全部展开/折叠
const toggleAll = () => {
  const newValue = !allExpanded.value
  sortedEvents.value.forEach((event, index) => {
    if (hasExpandableContent(event)) {
      expandedEvents.value[index] = newValue
    }
  })
}

// 刷新事件
const refreshEvents = () => {
  emit('refresh')
}

const emit = defineEmits(['refresh'])

// 监听事件变化，自动展开最新的任务列表事件
watch(() => props.events, (newEvents, oldEvents) => {
  if (newEvents.length > (oldEvents?.length || 0)) {
    // 找到最新的任务列表生成事件并展开
    const lastTaskListIndex = sortedEvents.value
      .map((e, i) => e.stage === 'task_list_generated' ? i : -1)
      .filter(i => i !== -1)
      .pop()
    if (lastTaskListIndex !== undefined) {
      expandedEvents.value[lastTaskListIndex] = true
    }
  }
}, { deep: true })
</script>

<style scoped lang="scss">
.process-timeline {
  background: var(--bg-white);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 16px;
  margin: 12px 0;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.timeline-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.timeline-actions {
  display: flex;
  gap: 8px;
}

.timeline-loading {
  padding: 20px 0;
}

.timeline-empty {
  padding: 20px 0;
}

.timeline-content {
  position: relative;
}

.timeline-item {
  display: flex;
  gap: 12px;
  padding: 8px 0;
  position: relative;

  &:not(:last-child)::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 36px;
    bottom: -8px;
    width: 2px;
    background: var(--border-light);
  }
}

.timeline-marker {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 1;

  &.info {
    background: #e6f7ff;
    color: #1890ff;
  }

  &.success {
    background: #f6ffed;
    color: #52c41a;
  }

  &.warning {
    background: #fffbe6;
    color: #faad14;
  }

  &.error {
    background: #fff2f0;
    color: #ff4d4f;
  }
}

.timeline-card {
  flex: 1;
  background: var(--bg-color);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--border-lighter);
  }
}

.timeline-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.event-message {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.event-time {
  font-size: 12px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.expand-icon {
  font-size: 12px;
  color: var(--text-secondary);
  transition: transform 0.2s ease;

  &.rotated {
    transform: rotate(180deg);
  }
}

.timeline-card-body {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

// 任务列表样式
.task-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg-white);
  border-radius: 4px;
  font-size: 13px;
}

.task-status {
  font-size: 10px;

  &.pending { color: var(--text-secondary); }
  &.running { color: #faad14; }
  &.completed { color: #52c41a; }
  &.failed { color: #ff4d4f; }
}

.task-name {
  font-weight: 500;
  color: var(--text-primary);
}

.task-type {
  color: var(--text-secondary);
  font-size: 12px;
}

.task-deps {
  color: var(--text-secondary);
  font-size: 11px;
  margin-left: auto;
}

// Agent调用样式
.agent-flow {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: var(--bg-white);
  border-radius: 4px;
  margin-bottom: 8px;
}

.agent {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;

  &.caller {
    background: #e6f7ff;
    color: #1890ff;
  }

  &.callee {
    background: #f6ffed;
    color: #52c41a;
  }
}

.flow-arrow {
  color: var(--text-secondary);
}

.agent-input, .agent-output {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 4px 8px;
  margin-top: 4px;
}

// 节点详情样式
.detail-row {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;

  &.error {
    color: #ff4d4f;
  }
}

.detail-label {
  color: var(--text-secondary);
  flex-shrink: 0;
  width: 80px;
}

.detail-value {
  color: var(--text-primary);
  word-break: break-all;
}

// 统计样式
.summary-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px;
  background: var(--bg-white);
  border-radius: 4px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;

  &.success .stat-value {
    color: #52c41a;
    font-weight: 600;
  }

  &.error .stat-value {
    color: #ff4d4f;
    font-weight: 600;
  }
}

.stat-label {
  color: var(--text-secondary);
}

.stat-value {
  color: var(--text-primary);
  font-weight: 500;
}

// 原始数据样式
.raw-data-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed var(--border-light);
}

.raw-data {
  margin-top: 8px;
  padding: 12px;
  background: #f6f8fa;
  border-radius: 4px;
  font-family: 'SFMono-Regular', Consolas, monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}
</style>
