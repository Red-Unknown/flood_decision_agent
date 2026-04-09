<template>
  <div class="smart-chat-input">
    <!-- 模式检测提示 -->
    <div v-if="showModeSuggestion" class="mode-suggestion">
      <el-alert
        :title="`检测到${getModeLabel(suggestedMode)}可能更适合您的问题`"
        type="info"
        :closable="false"
        show-icon
      >
        <template #default>
          <div class="suggestion-actions">
            <el-button type="primary" size="small" @click="acceptSuggestion">切换</el-button>
            <el-button size="small" @click="dismissSuggestion">保持当前</el-button>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 输入框区域 -->
    <div class="input-wrapper" :class="{ 'has-suggestion': showModeSuggestion }">
      <div class="mode-indicator" :class="currentMode">
        {{ getModeLabel(currentMode) }}
      </div>
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        :placeholder="getPlaceholder()"
        resize="none"
        @keydown.enter.prevent="handleEnter"
        @input="handleInput"
      />
      <div class="input-actions">
        <el-button
          type="primary"
          :disabled="!canSend || !inputMessage.trim()"
          :loading="isStreaming"
          @click="handleSend"
        >
          <el-icon><Promotion /></el-icon>
          发送
        </el-button>
      </div>
    </div>

    <!-- 命令提示 -->
    <div v-if="showCommandHint" class="command-hint">
      <el-tag size="small" type="info">/plan</el-tag>
      <el-tag size="small" type="info">/spec</el-tag>
      <span class="hint-text">输入命令切换模式</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Promotion } from '@element-plus/icons-vue'
import { detectMode } from '@/api/mode.js'
import { ElMessage } from 'element-plus'

const props = defineProps({
  isStreaming: {
    type: Boolean,
    default: false,
  },
  currentMode: {
    type: String,
    default: 'simple',
  },
})

const emit = defineEmits(['send', 'mode-change'])

// State
const inputMessage = ref('')
const showCommandHint = ref(false)
const showModeSuggestion = ref(false)
const suggestedMode = ref(null)
const detectionConfidence = ref(0)
const debounceTimer = ref(null)

// Computed
const canSend = computed(() => !props.isStreaming)

// 监听输入变化，检测命令
watch(inputMessage, (newVal) => {
  // 显示命令提示
  showCommandHint.value = newVal.startsWith('/')

  // 清除之前的定时器
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
  }

  // 自动检测模式（输入超过10个字符且不是命令）
  if (newVal.length > 10 && !newVal.startsWith('/')) {
    debounceTimer.value = setTimeout(() => {
      checkModeSuggestion(newVal)
    }, 1000)
  }
})

// 方法
const getPlaceholder = () => {
  const placeholders = {
    simple: '输入消息开始对话，输入 /plan 或 /spec 切换模式',
    plan: 'Plan 模式：描述您的规划需求',
    spec: 'Spec 模式：描述您的规格设计需求',
  }
  return placeholders[props.currentMode] || placeholders.simple
}

const getModeLabel = (mode) => {
  const labels = {
    simple: '简单模式',
    plan: 'Plan 模式',
    spec: 'Spec 模式',
  }
  return labels[mode] || mode
}

const handleEnter = (e) => {
  // Shift+Enter 换行，Enter 发送
  if (!e.shiftKey) {
    handleSend()
  }
}

const handleInput = () => {
  // 隐藏模式建议当用户继续输入
  if (showModeSuggestion.value) {
    showModeSuggestion.value = false
  }
}

const checkModeSuggestion = async (input) => {
  try {
    const result = await detectMode(input)
    if (result.recommended_mode !== props.currentMode && result.confidence > 0.7) {
      suggestedMode.value = result.recommended_mode
      detectionConfidence.value = result.confidence
      showModeSuggestion.value = true
    }
  } catch (error) {
    console.error('模式检测失败:', error)
  }
}

const acceptSuggestion = () => {
  emit('mode-change', suggestedMode.value)
  showModeSuggestion.value = false
  ElMessage.success(`已切换到${getModeLabel(suggestedMode.value)}`)
}

const dismissSuggestion = () => {
  showModeSuggestion.value = false
}

const handleSend = () => {
  const message = inputMessage.value.trim()
  if (!message || props.isStreaming) return

  // 解析命令
  let mode = props.currentMode
  let content = message

  if (message.startsWith('/plan ')) {
    mode = 'plan'
    content = message.slice(6)
  } else if (message === '/plan') {
    mode = 'plan'
    content = ''
  } else if (message.startsWith('/spec ')) {
    mode = 'spec'
    content = message.slice(6)
  } else if (message === '/spec') {
    mode = 'spec'
    content = ''
  }

  // 发送消息
  emit('send', content, mode)

  // 清空输入
  inputMessage.value = ''
  showModeSuggestion.value = false
}
</script>

<style scoped lang="scss">
.smart-chat-input {
  padding: 16px 20px;
  background: var(--bg-white);
  border-top: 1px solid var(--border-color);
}

.mode-suggestion {
  margin-bottom: 12px;

  .suggestion-actions {
    margin-top: 8px;
    display: flex;
    gap: 8px;
  }
}

.input-wrapper {
  position: relative;
  display: flex;
  gap: 12px;
  align-items: flex-end;

  &.has-suggestion {
    margin-top: 8px;
  }
}

.mode-indicator {
  position: absolute;
  top: -24px;
  left: 0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;

  &.simple {
    background: var(--el-color-info-light-9);
    color: var(--el-color-info);
  }

  &.plan {
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
  }

  &.spec {
    background: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }
}

:deep(.el-textarea__inner) {
  min-height: 80px !important;
  padding: 12px;
  font-size: 14px;
  line-height: 1.6;
  border-radius: 8px;
  resize: none;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .el-button {
    height: 40px;
    padding: 0 20px;
  }
}

.command-hint {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;

  .hint-text {
    font-size: 12px;
    color: var(--text-secondary);
  }
}
</style>
