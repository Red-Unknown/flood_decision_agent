<template>
  <aside class="spec-sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <div class="logo">
        <el-icon :size="24" color="#409eff"><Files /></el-icon>
        <span v-if="!isCollapsed" class="logo-text">规格管理</span>
      </div>
      <el-button
        v-if="!isCollapsed"
        type="primary"
        class="new-spec-btn"
        @click="handleNewSpec"
      >
        <el-icon><Plus /></el-icon>
        <span>新规格</span>
      </el-button>
      <el-button
        v-else
        type="primary"
        circle
        @click="handleNewSpec"
      >
        <el-icon><Plus /></el-icon>
      </el-button>
    </div>

    <div class="specs-list" v-if="!isCollapsed">
      <div class="list-header">
        <span class="list-title">规格列表</span>
        <el-button
          v-if="specs.length > 0"
          type="danger"
          link
          size="small"
          @click="handleClearAll"
        >
          清空全部
        </el-button>
      </div>

      <el-scrollbar class="specs-scrollbar">
        <div
          v-for="spec in specs"
          :key="spec.feature_name"
          class="spec-item"
          :class="{ active: currentSpec?.feature_name === spec.feature_name }"
          @click="handleSelectSpec(spec.feature_name)"
        >
          <el-icon class="spec-icon"><DocumentChecked /></el-icon>
          <div class="spec-info">
            <div class="spec-title">{{ spec.title }}</div>
            <div class="spec-meta">
              <span>{{ formatTime(spec.metadata?.updated_at) }}</span>
              <el-tag
                v-if="spec.metadata?.status"
                size="small"
                :type="getStatusType(spec.metadata.status)"
              >
                {{ getStatusText(spec.metadata.status) }}
              </el-tag>
            </div>
          </div>
          <el-dropdown
            trigger="click"
            @command="(cmd) => handleCommand(cmd, spec.feature_name)"
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
                <el-dropdown-item command="approve" :disabled="spec.metadata?.status === 'approved'">
                  <el-icon><CircleCheck /></el-icon>审批通过
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <el-icon><Delete /></el-icon>删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <el-empty
          v-if="specs.length === 0 && !isLoading"
          description="暂无规格"
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
import { useSpecStore } from '@/stores/spec.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'new-spec'])

const router = useRouter()
const specStore = useSpecStore()
const isCollapsed = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const specs = computed(() => specStore.specList)
const currentSpec = computed(() => specStore.currentSpec)
const isLoading = computed(() => specStore.isLoading)

onMounted(() => {
  specStore.loadSpecs()
})

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleNewSpec = () => {
  emit('new-spec')
}

const handleSelectSpec = (featureName) => {
  router.push(`/spec/${featureName}`)
}

const handleCommand = async (command, featureName) => {
  if (command === 'delete') {
    handleDeleteSpec(featureName)
  } else if (command === 'generate') {
    try {
      await specStore.generateContent(featureName)
      ElMessage.success('内容生成成功')
    } catch (error) {
      ElMessage.error('生成失败')
    }
  } else if (command === 'approve') {
    try {
      await specStore.approveSpec(featureName)
      ElMessage.success('规格已审批通过')
    } catch (error) {
      ElMessage.error('审批失败')
    }
  }
}

const handleDeleteSpec = async (featureName) => {
  try {
    await ElMessageBox.confirm('确定要删除这个规格吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await specStore.deleteSpec(featureName)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有规格吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    for (const spec of [...specs.value]) {
      await specStore.deleteSpec(spec.feature_name)
    }
    ElMessage.success('已清空所有规格')
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
    'approved': 'success',
    'archived': '',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'in_progress': '进行中',
    'approved': '已审批',
    'archived': '已归档',
  }
  return statusMap[status] || status
}
</script>

<style scoped lang="scss">
.spec-sidebar {
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

  .new-spec-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }
}

.specs-list {
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

  .specs-scrollbar {
    flex: 1;

    :deep(.el-scrollbar__wrap) {
      padding: 0 8px;
    }
  }
}

.spec-item {
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

    .spec-title {
      color: var(--primary-color);
      font-weight: 500;
    }
  }

  .spec-icon {
    color: var(--text-secondary);
    font-size: 18px;
  }

  .spec-info {
    flex: 1;
    min-width: 0;

    .spec-title {
      font-size: 14px;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-bottom: 2px;
    }

    .spec-meta {
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
