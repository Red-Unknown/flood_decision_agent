<template>
  <div class="plan-empty-state">
    <div class="empty-content">
      <el-icon :size="64" class="empty-icon"><Document /></el-icon>
      <h2 class="empty-title">开始创建规划</h2>
      <p class="empty-desc">
        创建规划文档来组织您的项目计划，支持AI辅助生成内容
      </p>
      <el-button type="primary" size="large" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建新规划
      </el-button>

      <div class="quick-actions">
        <h3 class="actions-title">快速开始</h3>
        <div class="action-buttons">
          <el-button
            v-for="action in quickActions"
            :key="action.key"
            class="action-btn"
            @click="handleActionClick(action.key)"
          >
            <el-icon :size="20"><component :is="action.icon" /></el-icon>
            <span>{{ action.label }}</span>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['create-click', 'action-click'])

const quickActions = [
  { key: 'flood', label: '洪水调度规划', icon: 'Watermelon' },
  { key: 'reservoir', label: '水库调度规划', icon: 'OfficeBuilding' },
  { key: 'emergency', label: '应急响应规划', icon: 'FirstAidKit' },
  { key: 'system', label: '系统升级规划', icon: 'Monitor' },
]

const handleCreate = () => {
  emit('create-click')
}

const handleActionClick = (action) => {
  emit('action-click', action)
}
</script>

<style scoped lang="scss">
.plan-empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.empty-content {
  text-align: center;
  max-width: 480px;
}

.empty-icon {
  color: var(--primary-color);
  margin-bottom: 24px;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 24px;
  line-height: 1.6;
}

.quick-actions {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid var(--border-light);
}

.actions-title {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 16px;
  font-weight: 500;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-btn {
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  background: var(--bg-white);
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    background: var(--message-user-bg);
  }

  span {
    font-size: 13px;
    color: var(--text-primary);
  }

  .el-icon {
    color: var(--primary-color);
  }
}
</style>
