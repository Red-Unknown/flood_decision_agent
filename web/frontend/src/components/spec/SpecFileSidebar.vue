<template>
  <aside class="file-sidebar">
    <div class="file-list-header">
      <span>文件列表</span>
    </div>
    <div class="file-list">
      <div
        v-for="file in files"
        :key="file.name"
        class="file-item"
        :class="{ active: currentFile === file.name }"
        @click="handleSelectFile(file.name)"
      >
        <el-icon class="file-icon">
          <Document v-if="file.name.endsWith('.md')" />
          <List v-else-if="file.name.includes('task')" />
          <Check v-else />
        </el-icon>
        <span class="file-name">{{ getFileDisplayName(file.name) }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
const props = defineProps({
  files: {
    type: Array,
    default: () => [],
  },
  currentFile: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['select-file'])

const fileDisplayNames = {
  'spec.md': '规格文档',
  'tasks.md': '任务分解',
  'checklist.md': '检查清单',
}

const getFileDisplayName = (filename) => {
  return fileDisplayNames[filename] || filename
}

const handleSelectFile = (filename) => {
  emit('select-file', filename)
}
</script>

<style scoped lang="scss">
.file-sidebar {
  width: 180px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
}

.file-list-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.file-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 4px;

  &:hover {
    background: var(--border-lighter);
  }

  &.active {
    background: var(--message-user-bg);

    .file-name {
      color: var(--primary-color);
      font-weight: 500;
    }

    .file-icon {
      color: var(--primary-color);
    }
  }

  .file-icon {
    color: var(--text-secondary);
    font-size: 16px;
  }

  .file-name {
    font-size: 13px;
    color: var(--text-primary);
  }
}
</style>
