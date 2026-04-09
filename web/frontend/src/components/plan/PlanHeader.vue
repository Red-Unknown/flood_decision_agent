<template>
  <header class="plan-header">
    <div class="header-left">
      <el-button
        v-if="sidebarCollapsed"
        link
        class="expand-btn"
        @click="toggleSidebar"
      >
        <el-icon><Expand /></el-icon>
      </el-button>
      <div class="title-section">
        <h1 class="title">{{ title }}</h1>
        <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      </div>
    </div>

    <div class="header-actions">
      <template v-if="hasContent">
        <el-button
          type="primary"
          :loading="isGenerating"
          @click="handleGenerate"
        >
          <el-icon><MagicStick /></el-icon>
          <span>AI生成</span>
        </el-button>
        <el-button
          type="danger"
          link
          @click="handleDelete"
        >
          <el-icon><Delete /></el-icon>
          <span>删除</span>
        </el-button>
      </template>
      <el-button
        type="primary"
        plain
        @click="handleNewPlan"
      >
        <el-icon><Plus /></el-icon>
        <span>新建</span>
      </el-button>
    </div>
  </header>
</template>

<script setup>
import { ElMessageBox } from 'element-plus'

const props = defineProps({
  title: {
    type: String,
    default: '规划管理',
  },
  subtitle: {
    type: String,
    default: '',
  },
  sidebarCollapsed: {
    type: Boolean,
    default: false,
  },
  hasContent: {
    type: Boolean,
    default: false,
  },
  isGenerating: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['toggle-sidebar', 'generate', 'new-plan', 'delete'])

const toggleSidebar = () => {
  emit('toggle-sidebar')
}

const handleGenerate = () => {
  emit('generate')
}

const handleNewPlan = () => {
  emit('new-plan')
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这个规划吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    emit('delete')
  } catch (error) {
    // 用户取消
  }
}
</script>

<style scoped lang="scss">
.plan-header {
  height: 60px;
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

  .expand-btn {
    font-size: 20px;
    color: var(--text-secondary);

    &:hover {
      color: var(--text-primary);
    }
  }
}

.title-section {
  .title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .subtitle {
    font-size: 12px;
    color: var(--text-secondary);
    margin: 2px 0 0;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;

  .el-button {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}
</style>
