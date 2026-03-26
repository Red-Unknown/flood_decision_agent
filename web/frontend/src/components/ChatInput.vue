<template>
  <div class="chat-input-area">
    <div class="input-container">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        :placeholder="placeholder"
        resize="none"
        :disabled="isStreaming"
        @keydown="handleKeydown"
      />
      <div class="input-actions">
        <div class="input-hints">
          <span class="hint">Enter 发送</span>
          <span class="hint">Shift + Enter 换行</span>
        </div>
        <el-button
          type="primary"
          :disabled="!canSend"
          :loading="isStreaming"
          @click="handleSend"
        >
          <el-icon v-if="!isStreaming"><Promotion /></el-icon>
          <span>{{ isStreaming ? '发送中...' : '发送' }}</span>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Promotion } from '@element-plus/icons-vue'

const props = defineProps({
  isStreaming: {
    type: Boolean,
    default: false,
  },
  placeholder: {
    type: String,
    default: '请输入您的问题...',
  },
})

const emit = defineEmits(['send'])

const inputMessage = ref('')

const canSend = computed(() => {
  return inputMessage.value.trim().length > 0 && !props.isStreaming
})

const handleSend = () => {
  if (!canSend.value) return

  const message = inputMessage.value.trim()
  emit('send', message)
  inputMessage.value = ''
}

const handleKeydown = (e) => {
  // Enter 发送，Shift + Enter 换行
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<style scoped lang="scss">
.chat-input-area {
  padding: 16px 20px;
  background: var(--bg-white);
  border-top: 1px solid var(--border-light);
}

.input-container {
  max-width: 900px;
  margin: 0 auto;
}

:deep(.el-textarea__inner) {
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  transition: all 0.2s ease;

  &:focus {
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
  }
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-hints {
  display: flex;
  gap: 16px;

  .hint {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.el-button {
  padding: 8px 20px;
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
