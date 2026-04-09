<template>
  <div class="spec-view">
    <SpecSidebar
      v-model="sidebarCollapsed"
      @new-spec="handleNewSpec"
    />

    <div class="spec-main" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <SpecHeader
        :title="headerTitle"
        :subtitle="headerSubtitle"
        :sidebar-collapsed="sidebarCollapsed"
        :has-content="hasContent"
        :is-generating="isGenerating"
        :is-approved="isApproved"
        @toggle-sidebar="toggleSidebar"
        @generate="handleGenerate"
        @approve="handleApprove"
        @new-spec="handleNewSpec"
      />

      <div class="spec-content">
        <template v-if="!hasContent && !isLoading">
          <SpecEmptyState
            @create-click="handleNewSpec"
          />
        </template>

        <template v-else-if="isLoading">
          <div class="loading-container">
            <el-skeleton :rows="10" animated />
          </div>
        </template>

        <template v-else>
          <div class="spec-layout">
            <!-- 文件列表侧边栏 -->
            <SpecFileSidebar
              :files="currentFiles"
              :current-file="selectedFile"
              @select-file="handleSelectFile"
            />

            <!-- 文档编辑器 -->
            <el-scrollbar ref="contentScrollbar" class="content-container">
              <div class="content-wrapper">
                <SpecEditor
                  v-if="currentSpec && currentFileContent"
                  :spec="currentSpec"
                  :file-content="currentFileContent"
                  @update-file="handleUpdateFile"
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
          </div>
        </template>
      </div>

      <!-- 创建规格对话框 -->
      <el-dialog
        v-model="createDialogVisible"
        title="创建新规格"
        width="600px"
      >
        <el-form :model="newSpecForm" label-width="100px">
          <el-form-item label="功能名称" required>
            <el-input
              v-model="newSpecForm.feature_name"
              placeholder="请输入功能名称（英文标识）"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="标题" required>
            <el-input
              v-model="newSpecForm.title"
              placeholder="请输入规格标题"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="newSpecForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入规格描述"
            />
          </el-form-item>
          <el-form-item label="需求">
            <el-input
              v-model="newSpecForm.requirements"
              type="textarea"
              :rows="3"
              placeholder="请输入功能需求（每行一个）"
            />
          </el-form-item>
          <el-form-item label="技术设计">
            <el-input
              v-model="newSpecForm.technical_design"
              type="textarea"
              :rows="3"
              placeholder="请输入技术设计方案"
            />
          </el-form-item>
          <el-form-item label="接口定义">
            <el-input
              v-model="newSpecForm.interfaces"
              type="textarea"
              :rows="3"
              placeholder="请输入接口定义"
            />
          </el-form-item>
          <el-form-item label="验收标准">
            <el-input
              v-model="newSpecForm.acceptance_criteria"
              type="textarea"
              :rows="3"
              placeholder="请输入验收标准（每行一个）"
            />
          </el-form-item>
          <el-form-item label="任务">
            <el-input
              v-model="newSpecForm.tasks"
              type="textarea"
              :rows="3"
              placeholder="请输入任务列表（每行一个）"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmCreateSpec" :loading="isCreating">
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
import { useSpecStore } from '@/stores/spec.js'
import SpecSidebar from '@/components/spec/SpecSidebar.vue'
import SpecHeader from '@/components/spec/SpecHeader.vue'
import SpecEditor from '@/components/spec/SpecEditor.vue'
import SpecEmptyState from '@/components/spec/SpecEmptyState.vue'
import SpecFileSidebar from '@/components/spec/SpecFileSidebar.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const specStore = useSpecStore()

// 状态
const sidebarCollapsed = ref(false)
const contentScrollbar = ref(null)
const createDialogVisible = ref(false)
const isCreating = ref(false)
const selectedFile = ref('spec.md')

const newSpecForm = ref({
  feature_name: '',
  title: '',
  description: '',
  requirements: '',
  technical_design: '',
  interfaces: '',
  acceptance_criteria: '',
  tasks: '',
})

// 计算属性
const currentSpec = computed(() => specStore.currentSpec)
const currentFiles = computed(() => specStore.currentFiles)
const currentFileContent = computed(() => specStore.currentFileContent)
const isLoading = computed(() => specStore.isLoading)
const isGenerating = computed(() => specStore.isLoading)
const error = computed(() => specStore.error)

const hasContent = computed(() => {
  return currentSpec.value !== null
})

const isApproved = computed(() => {
  return currentSpec.value?.metadata?.status === 'approved'
})

const headerTitle = computed(() => {
  return currentSpec.value?.title || '规格管理'
})

const headerSubtitle = computed(() => {
  if (isGenerating.value) {
    return 'AI正在生成内容...'
  }
  if (isApproved.value) {
    return '已审批通过'
  }
  return currentSpec.value ? '' : '创建或选择一个规格'
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleNewSpec = () => {
  newSpecForm.value = {
    feature_name: '',
    title: '',
    description: '',
    requirements: '',
    technical_design: '',
    interfaces: '',
    acceptance_criteria: '',
    tasks: '',
  }
  createDialogVisible.value = true
}

const confirmCreateSpec = async () => {
  if (!newSpecForm.value.feature_name.trim()) {
    ElMessage.warning('请输入功能名称')
    return
  }
  if (!newSpecForm.value.title.trim()) {
    ElMessage.warning('请输入规格标题')
    return
  }

  try {
    isCreating.value = true
    const specData = {
      ...newSpecForm.value,
      requirements: newSpecForm.value.requirements.split('\n').filter(r => r.trim()),
      acceptance_criteria: newSpecForm.value.acceptance_criteria.split('\n').filter(c => c.trim()),
      tasks: newSpecForm.value.tasks.split('\n').filter(t => t.trim()),
    }
    const data = await specStore.createSpec(specData)
    createDialogVisible.value = false
    router.push(`/spec/${data.feature_name}`)
    ElMessage.success('规格创建成功')
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    isCreating.value = false
  }
}

const handleSelectFile = async (file) => {
  selectedFile.value = file
  if (currentSpec.value) {
    await specStore.loadSpecFile(currentSpec.value.feature_name, file)
  }
}

const handleUpdateFile = async (fileData) => {
  try {
    await specStore.updateFile(currentSpec.value.feature_name, selectedFile.value, fileData)
    ElMessage.success('文件更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleUpdateSection = async (section, content) => {
  try {
    await specStore.updateSection(currentSpec.value.feature_name, selectedFile.value, section, content)
    ElMessage.success('章节更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleGenerate = async () => {
  if (!currentSpec.value) return
  try {
    await specStore.generateContent(currentSpec.value.feature_name)
    ElMessage.success('内容生成成功')
  } catch (error) {
    ElMessage.error('生成失败')
  }
}

const handleApprove = async () => {
  if (!currentSpec.value) return
  try {
    await specStore.approveSpec(currentSpec.value.feature_name)
    ElMessage.success('规格已审批通过')
  } catch (error) {
    ElMessage.error('审批失败')
  }
}

const clearError = () => {
  specStore.error = null
}

// 监听路由参数，加载指定规格
watch(
  () => route.params.featureName,
  async (featureName) => {
    if (featureName) {
      await specStore.loadSpec(featureName)
      await specStore.loadSpecFiles(featureName)
      await specStore.loadSpecFile(featureName, selectedFile.value)
    }
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.spec-view {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.spec-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-white);
  transition: margin-left 0.3s ease;
}

.spec-content {
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

.spec-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.content-container {
  flex: 1;
  overflow: hidden;

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
