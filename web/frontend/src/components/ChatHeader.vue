<template>
  <header class="chat-header">
    <div class="header-left">
      <el-button
        v-if="showToggle"
        link
        @click="$emit('toggle-sidebar')"
      >
        <el-icon :size="20"><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
      </el-button>
      <div class="header-title">
        <h2>{{ title }}</h2>
        <span v-if="subtitle" class="subtitle">{{ subtitle }}</span>
      </div>
    </div>
    <div class="header-right">
      <el-tooltip content="清空当前对话" placement="bottom">
        <el-button
          link
          :disabled="!hasMessages || isStreaming"
          @click="$emit('clear')"
        >
          <el-icon><Delete /></el-icon>
        </el-button>
      </el-tooltip>
      <el-tooltip content="新对话" placement="bottom">
        <el-button
          link
          @click="$emit('new-chat')"
        >
          <el-icon><Plus /></el-icon>
        </el-button>
      </el-tooltip>
    </div>
  </header>
</template>

<script setup>
import { Fold, Expand, Delete, Plus } from '@element-plus/icons-vue'

defineProps({
  title: {
    type: String,
    default: '水利智脑',
  },
  subtitle: {
    type: String,
    default: '',
  },
  showToggle: {
    type: Boolean,
    default: true,
  },
  sidebarCollapsed: {
    type: Boolean,
    default: false,
  },
  hasMessages: {
    type: Boolean,
    default: false,
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle-sidebar', 'clear', 'new-chat'])
</script>

<style scoped lang="scss">
.chat-header {
  height: var(--header-height);
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-white);
  border-bottom: 1px solid var(--border-light);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  display: flex;
  align-items: baseline;
  gap: 8px;

  h2 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .subtitle {
    font-size: 13px;
    color: var(--text-secondary);
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px;

  .el-button {
    padding: 8px;
    color: var(--text-secondary);

    &:hover {
      color: var(--primary-color);
    }

    &:disabled {
      color: var(--text-placeholder);
    }
  }
}
</style>
