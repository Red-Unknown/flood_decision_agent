<template>
  <aside class="plan-sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <div class="logo">
        <el-icon :size="24" color="#409eff"><Document /></el-icon>
        <span v-if="!isCollapsed" class="logo-text">规划管理</span>
      </div>
      <el-button
        v-if="!isCollapsed"
        type="primary"
        class="new-plan-btn"
        @click="handleNewPlan"
      >
        <el-icon><Plus /></el-icon>
        <span>新规划</span>
      </el-button>
      <el-button
        v-else
        type="primary"
        circle
        @click="handleNewPlan"
      >
        <el-icon><Plus /></el-icon>
      </el-button>
    </div>

    <div class="plans-list" v-if="!isCollapsed">
      <div class="list-header">
        <span class="list-title">规划列表</span>
        <el-button
          v-if="plans.length > 0"
          type="danger"
          link
          size="small"
          @click="handleClearAll"
        >
          清空全部
        </el-button>
      </div>

      <el-scrollbar class="plans-scrollbar">
        <div
          v-for="plan in plans"
          :key="plan.id"
          class="plan-item"
          :class="{ active: currentPlan?.id === plan.id }"
          @click="handleSelectPlan(plan.id)"
        >
          <el-icon class="plan-icon"><Document /></el-icon>
          <div class="plan-info">
            <div class="plan-title">{{ plan.title }}</div>
            <div class="plan-meta">
              <span>{{ formatTime(plan.metadata?.updated_at) }}</span>
              <el-tag v-if="plan.metadata?.status" size="small" :type="getStatusType(plan.metadata.status)">
                {{ getStatusText(plan.metadata.status) }}
              </el-tag>
            </div>
          </div>
          <el-dropdown
            trigger="click"
            @command="(cmd) => handleCommand(cmd, plan.id)"
            @click.stop
          >
            <el-button link class="more-btn">
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="generate">
                  <el-icon><MagicStick /></el-icon>AI生成
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <el-icon><Delete /></el-icon>删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <el-empty
          v-if="plans.length === 0 && !isLoading"
          description="暂无规划"
          :image-size="80"
        />
      </el-scrollbar>
    </div>

    <div class="sidebar-footer" v-if="!isCollapsed">
      <el-button link @click="toggleCollapse">
        <el-icon><Fold /></el-icon>
        <span>收起侧边栏</span>
      </el-button>
    </div>
    <div class="sidebar-footer collapsed" v-else>
      <el-button link @click="toggleCollapse">
        <el-icon><Expand /></el-icon>
      </el-button>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlanStore } from '@/stores/plan.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'new-plan'])

const router = useRouter()
const planStore = usePlanStore()
const isCollapsed = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const plans = computed(() => planStore.planList)
const currentPlan = computed(() => planStore.currentPlan)
const isLoading = computed(() => planStore.isLoading)

onMounted(() => {
  planStore.loadPlans()
})

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleNewPlan = () => {
  emit('new-plan')
}

const handleSelectPlan = (planId) => {
  router.push(`/plan/${planId}`)
}

const handleCommand = async (command, planId) => {
  if (command === 'delete') {
    handleDeletePlan(planId)
  } else if (command === 'generate') {
    try {
      await planStore.generateContent(planId)
      ElMessage.success('内容生成成功')
    } catch (error) {
      ElMessage.error('生成失败')
    }
  }
}

const handleDeletePlan = async (planId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个规划吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await planStore.deletePlan(planId)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有规划吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    for (const plan of [...plans.value]) {
      await planStore.deletePlan(plan.id)
    }
    ElMessage.success('已清空所有规划')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败')
    }
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now - date

  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return minutes < 1 ? '刚刚' : `${minutes}分钟前`
  }
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const getStatusType = (status) => {
  const statusMap = {
    'draft': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'archived': '',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'in_progress': '进行中',
    'completed': '已完成',
    'archived': '已归档',
  }
  return statusMap[status] || status
}
</script>

<style scoped lang="scss">
.plan-sidebar {
  width: var(--sidebar-width);
  height: 100%;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;

  &.collapsed {
    width: 60px;
  }
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-light);

  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;

    .logo-text {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }

  .new-plan-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }
}

.plans-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .list-header {
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .list-title {
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 500;
    }
  }

  .plans-scrollbar {
    flex: 1;

    :deep(.el-scrollbar__wrap) {
      padding: 0 8px;
    }
  }
}

.plan-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--border-lighter);

    .more-btn {
      opacity: 1;
    }
  }

  &.active {
    background: var(--message-user-bg);

    .plan-title {
      color: var(--primary-color);
      font-weight: 500;
    }
  }

  .plan-icon {
    color: var(--text-secondary);
    font-size: 18px;
  }

  .plan-info {
    flex: 1;
    min-width: 0;

    .plan-title {
      font-size: 14px;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-bottom: 2px;
    }

    .plan-meta {
      font-size: 12px;
      color: var(--text-secondary);
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }

  .more-btn {
    opacity: 0;
    transition: opacity 0.2s ease;
    padding: 4px;
  }
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border-light);

  .el-button {
    width: 100%;
    justify-content: flex-start;
    gap: 8px;
    color: var(--text-secondary);

    &:hover {
      color: var(--text-primary);
    }
  }

  &.collapsed {
    .el-button {
      justify-content: center;
    }
  }
}

:deep(.el-empty) {
  padding: 40px 0;
}
</style>
