<template>
  <div class="plan-view">
    <PlanSidebar
      v-model="sidebarCollapsed"
      @new-plan="handleNewPlan"
    />

    <div class="plan-main" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <PlanHeader
        :title="headerTitle"
        :subtitle="headerSubtitle"
        :sidebar-collapsed="sidebarCollapsed"
        :has-content="hasContent"
        :is-generating="isGenerating"
        @toggle-sidebar="toggleSidebar"
        @generate="handleGenerate"
        @new-plan="handleNewPlan"
      />

      <div class="plan-content">
        <template v-if="!hasContent && !isLoading">
          <PlanEmptyState
            @create-click="handleNewPlan"
          />
        </template>

        <template v-else-if="isLoading">
          <div class="loading-container">
            <el-skeleton :rows="10" animated />
          </div>
        </template>

        <template v-else>
          <el-scrollbar ref="contentScrollbar" class="content-container">
            <div class="content-wrapper">
              <!-- 规划文档编辑器 -->
              <PlanEditor
                v-if="currentPlan"
                :plan="currentPlan"
                @update="handleUpdatePlan"
                @update-section="handleUpdateSection"
              />

              <!-- 错误提示 -->
              <el-alert
                v-if="error"
                :title="error"
                type="error"
                closable
                @close="clearError"
                class="error-alert"
              />
            </div>
          </el-scrollbar>
        </template>
      </div>

      <!-- 创建规划对话框 -->
      <el-dialog
        v-model="createDialogVisible"
        title="创建新规划"
        width="600px"
      >
        <el-form :model="newPlanForm" label-width="80px">
          <el-form-item label="标题" required>
            <el-input
              v-model="newPlanForm.title"
              placeholder="请输入规划标题"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="newPlanForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入规划描述"
            />
          </el-form-item>
          <el-form-item label="目标">
            <el-input
              v-model="newPlanForm.goals"
              type="textarea"
              :rows="3"
              placeholder="请输入规划目标（每行一个）"
            />
          </el-form-item>
          <el-form-item label="步骤">
            <el-input
              v-model="newPlanForm.steps"
              type="textarea"
              :rows="3"
              placeholder="请输入实施步骤（每行一个）"
            />
          </el-form-item>
          <el-form-item label="验收标准">
            <el-input
              v-model="newPlanForm.criteria"
              type="textarea"
              :rows="3"
              placeholder="请输入验收标准（每行一个）"
            />
          </el-form-item>
          <el-form-item label="备注">
            <el-input
              v-model="newPlanForm.notes"
              type="textarea"
              :rows="2"
              placeholder="请输入备注信息"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmCreatePlan" :loading="isCreating">
            创建
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePlanStore } from '@/stores/plan.js'
import PlanSidebar from '@/components/plan/PlanSidebar.vue'
import PlanHeader from '@/components/plan/PlanHeader.vue'
import PlanEditor from '@/components/plan/PlanEditor.vue'
import PlanEmptyState from '@/components/plan/PlanEmptyState.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const planStore = usePlanStore()

// 状态
const sidebarCollapsed = ref(false)
const contentScrollbar = ref(null)
const createDialogVisible = ref(false)
const isCreating = ref(false)

const newPlanForm = ref({
  title: '',
  description: '',
  goals: '',
  steps: '',
  criteria: '',
  notes: '',
})

// 计算属性
const currentPlan = computed(() => planStore.currentPlan)
const isLoading = computed(() => planStore.isLoading)
const isGenerating = computed(() => planStore.isLoading)
const error = computed(() => planStore.error)

const hasContent = computed(() => {
  return currentPlan.value !== null
})

const headerTitle = computed(() => {
  return currentPlan.value?.title || '规划管理'
})

const headerSubtitle = computed(() => {
  if (isGenerating.value) {
    return 'AI正在生成内容...'
  }
  return currentPlan.value ? '' : '创建或选择一个规划'
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleNewPlan = () => {
  newPlanForm.value = {
    title: '',
    description: '',
    goals: '',
    steps: '',
    criteria: '',
    notes: '',
  }
  createDialogVisible.value = true
}

const confirmCreatePlan = async () => {
  if (!newPlanForm.value.title.trim()) {
    ElMessage.warning('请输入规划标题')
    return
  }

  try {
    isCreating.value = true
    const planData = {
      ...newPlanForm.value,
      goals: newPlanForm.value.goals.split('\n').filter(g => g.trim()),
      steps: newPlanForm.value.steps.split('\n').filter(s => s.trim()),
      criteria: newPlanForm.value.criteria.split('\n').filter(c => c.trim()),
    }
    const data = await planStore.createPlan(planData)
    createDialogVisible.value = false
    router.push(`/plan/${data.id}`)
    ElMessage.success('规划创建成功')
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    isCreating.value = false
  }
}

const handleUpdatePlan = async (planData) => {
  try {
    await planStore.updatePlan(currentPlan.value.id, planData)
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleUpdateSection = async (section, content) => {
  try {
    await planStore.updateSection(currentPlan.value.id, section, content)
    ElMessage.success('章节更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleGenerate = async () => {
  if (!currentPlan.value) return
  try {
    await planStore.generateContent(currentPlan.value.id)
    ElMessage.success('内容生成成功')
  } catch (error) {
    ElMessage.error('生成失败')
  }
}

const clearError = () => {
  planStore.error = null
}

// 监听路由参数，加载指定规划
watch(
  () => route.params.planId,
  async (planId) => {
    if (planId) {
      await planStore.loadPlan(planId)
    }
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.plan-view {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.plan-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-white);
  transition: margin-left 0.3s ease;
}

.plan-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
}

.loading-container {
  flex: 1;
  padding: 40px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.content-container {
  flex: 1;

  :deep(.el-scrollbar__wrap) {
    padding: 20px 0;
  }
}

.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  padding: 0 20px;
}

.error-alert {
  margin: 16px 0;
}
</style>
