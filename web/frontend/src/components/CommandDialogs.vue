<template>
  <div class="command-dialogs">
    <!-- Plan 模式对话框 -->
    <el-dialog
      v-model="planDialogVisible"
      title="规划模式"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div class="mode-header">
        <el-alert
          title="您已进入规划模式。在此模式下，我可以帮您创建、编辑和管理规划文档。"
          type="info"
          :closable="false"
          show-icon
        />
      </div>

      <div class="plan-list" v-if="!currentPlan">
        <div class="list-header">
          <span>选择或创建规划</span>
          <el-button type="primary" size="small" @click="startCreatePlan">
            <el-icon><Plus /></el-icon>
            新建规划
          </el-button>
        </div>

        <el-scrollbar class="plans-scrollbar" v-if="plans.length > 0">
          <div
            v-for="plan in plans"
            :key="plan.id"
            class="plan-item"
            @click="selectPlan(plan)"
          >
            <el-icon class="plan-icon"><Document /></el-icon>
            <div class="plan-info">
              <div class="plan-title">{{ plan.title }}</div>
              <div class="plan-desc">{{ plan.description || '暂无描述' }}</div>
            </div>
            <el-tag size="small" :type="getStatusType(plan.metadata?.status)">
              {{ getStatusText(plan.metadata?.status) }}
            </el-tag>
          </div>
        </el-scrollbar>

        <el-empty v-else description="暂无规划，请创建新规划" />
      </div>

      <div class="plan-editor" v-else>
        <div class="editor-header">
          <el-button link @click="backToPlanList">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
          <span class="plan-title">{{ currentPlan.title }}</span>
          <el-button type="primary" size="small" @click="handleGeneratePlan">
            <el-icon><MagicStick /></el-icon>
            AI生成
          </el-button>
        </div>

        <el-tabs v-model="activePlanTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-form :model="planForm" label-width="80px">
              <el-form-item label="标题">
                <el-input v-model="planForm.title" />
              </el-form-item>
              <el-form-item label="描述">
                <el-input v-model="planForm.description" type="textarea" :rows="3" />
              </el-form-item>
            </el-form>
          </el-tab-pane>
          <el-tab-pane
            v-for="(content, section) in currentPlan.sections"
            :key="section"
            :label="section"
            :name="section"
          >
            <el-input
              v-model="planSections[section]"
              type="textarea"
              :rows="10"
              placeholder="请输入内容..."
            />
          </el-tab-pane>
        </el-tabs>

        <div class="editor-actions">
          <el-button @click="planDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="savePlan">保存</el-button>
        </div>
      </div>

      <!-- 创建规划表单 -->
      <el-form
        v-if="isCreatingPlan"
        :model="newPlanForm"
        label-width="80px"
        class="create-form"
      >
        <el-form-item label="标题" required>
          <el-input v-model="newPlanForm.title" placeholder="请输入规划标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="newPlanForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入规划描述"
          />
        </el-form-item>
        <el-form-item>
          <el-button @click="cancelCreatePlan">取消</el-button>
          <el-button type="primary" @click="confirmCreatePlan">创建</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- Spec 模式对话框 -->
    <el-dialog
      v-model="specDialogVisible"
      title="规格模式"
      width="900px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div class="mode-header">
        <el-alert
          title="您已进入规格模式。在此模式下，我可以帮您创建、编辑和管理规格文档套装。"
          type="info"
          :closable="false"
          show-icon
        />
      </div>

      <div class="spec-list" v-if="!currentSpec">
        <div class="list-header">
          <span>选择或创建规格</span>
          <el-button type="primary" size="small" @click="startCreateSpec">
            <el-icon><Plus /></el-icon>
            新建规格
          </el-button>
        </div>

        <el-scrollbar class="specs-scrollbar" v-if="specs.length > 0">
          <div
            v-for="spec in specs"
            :key="spec.feature_name"
            class="spec-item"
            @click="selectSpec(spec)"
          >
            <el-icon class="spec-icon"><DocumentChecked /></el-icon>
            <div class="spec-info">
              <div class="spec-title">{{ spec.title }}</div>
              <div class="spec-desc">{{ spec.description || '暂无描述' }}</div>
            </div>
            <el-tag size="small" :type="getStatusType(spec.metadata?.status)">
              {{ getStatusText(spec.metadata?.status) }}
            </el-tag>
          </div>
        </el-scrollbar>

        <el-empty v-else description="暂无规格，请创建新规格" />
      </div>

      <div class="spec-editor" v-else>
        <div class="editor-header">
          <el-button link @click="backToSpecList">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
          <span class="spec-title">{{ currentSpec.title }}</span>
          <div class="header-actions">
            <el-button type="success" size="small" :disabled="currentSpec.metadata?.status === 'approved'" @click="handleApproveSpec">
              <el-icon><CircleCheck /></el-icon>
              审批
            </el-button>
            <el-button type="primary" size="small" @click="handleGenerateSpec">
              <el-icon><MagicStick /></el-icon>
              AI生成
            </el-button>
          </div>
        </div>

        <div class="spec-layout">
          <div class="file-sidebar">
            <div
              v-for="file in specFiles"
              :key="file.name"
              class="file-item"
              :class="{ active: currentFile === file.name }"
              @click="selectFile(file.name)"
            >
              <el-icon><Document /></el-icon>
              <span>{{ getFileDisplayName(file.name) }}</span>
            </div>
          </div>

          <div class="file-content">
            <el-tabs v-model="activeSpecTab">
              <el-tab-pane
                v-for="(content, section) in fileSections"
                :key="section"
                :label="section"
                :name="section"
              >
                <el-input
                  v-model="fileSections[section]"
                  type="textarea"
                  :rows="12"
                  placeholder="请输入内容..."
                />
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>

        <div class="editor-actions">
          <el-button @click="specDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="saveSpec">保存</el-button>
        </div>
      </div>

      <!-- 创建规格表单 -->
      <el-form
        v-if="isCreatingSpec"
        :model="newSpecForm"
        label-width="100px"
        class="create-form"
      >
        <el-form-item label="功能名称" required>
          <el-input v-model="newSpecForm.feature_name" placeholder="请输入功能名称（英文标识）" />
        </el-form-item>
        <el-form-item label="标题" required>
          <el-input v-model="newSpecForm.title" placeholder="请输入规格标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="newSpecForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入规格描述"
          />
        </el-form-item>
        <el-form-item>
          <el-button @click="cancelCreateSpec">取消</el-button>
          <el-button type="primary" @click="confirmCreateSpec">创建</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { usePlanStore } from '@/stores/plan.js'
import { useSpecStore } from '@/stores/spec.js'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ type: null, visible: false }),
  },
})

const emit = defineEmits(['update:modelValue'])

const planStore = usePlanStore()
const specStore = useSpecStore()

// Plan 相关状态
const planDialogVisible = ref(false)
const currentPlan = ref(null)
const activePlanTab = ref('basic')
const isCreatingPlan = ref(false)
const planForm = reactive({
  title: '',
  description: '',
})
const planSections = reactive({})
const newPlanForm = reactive({
  title: '',
  description: '',
})

// Spec 相关状态
const specDialogVisible = ref(false)
const currentSpec = ref(null)
const currentFile = ref('spec.md')
const activeSpecTab = ref('概述')
const isCreatingSpec = ref(false)
const fileSections = reactive({})
const newSpecForm = reactive({
  feature_name: '',
  title: '',
  description: '',
})

const plans = computed(() => planStore.planList)
const specs = computed(() => specStore.specList)

const specFiles = computed(() => [
  { name: 'spec.md' },
  { name: 'tasks.md' },
  { name: 'checklist.md' },
])

const fileDisplayNames = {
  'spec.md': '规格文档',
  'tasks.md': '任务分解',
  'checklist.md': '检查清单',
}

watch(
  () => props.modelValue,
  (val) => {
    if (val.type === 'plan' && val.visible) {
      planDialogVisible.value = true
      planStore.loadPlans()
    } else if (val.type === 'spec' && val.visible) {
      specDialogVisible.value = true
      specStore.loadSpecs()
    }
  },
  { deep: true }
)

watch(planDialogVisible, (val) => {
  if (!val) {
    emit('update:modelValue', { type: null, visible: false })
    currentPlan.value = null
    isCreatingPlan.value = false
  }
})

watch(specDialogVisible, (val) => {
  if (!val) {
    emit('update:modelValue', { type: null, visible: false })
    currentSpec.value = null
    isCreatingSpec.value = false
  }
})

// Plan 方法
const startCreatePlan = () => {
  isCreatingPlan.value = true
  newPlanForm.title = ''
  newPlanForm.description = ''
}

const cancelCreatePlan = () => {
  isCreatingPlan.value = false
}

const confirmCreatePlan = async () => {
  if (!newPlanForm.title.trim()) {
    ElMessage.warning('请输入规划标题')
    return
  }
  try {
    const data = await planStore.createPlan({
      title: newPlanForm.title,
      description: newPlanForm.description,
    })
    isCreatingPlan.value = false
    selectPlan(data)
    ElMessage.success('规划创建成功')
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const selectPlan = (plan) => {
  currentPlan.value = plan
  planForm.title = plan.title
  planForm.description = plan.description || ''
  Object.keys(planSections).forEach(key => delete planSections[key])
  if (plan.sections) {
    Object.entries(plan.sections).forEach(([key, value]) => {
      planSections[key] = value
    })
  }
}

const backToPlanList = () => {
  currentPlan.value = null
}

const savePlan = async () => {
  try {
    await planStore.updatePlan(currentPlan.value.id, {
      title: planForm.title,
      description: planForm.description,
    })
    // 保存各个章节
    for (const [section, content] of Object.entries(planSections)) {
      await planStore.updateSection(currentPlan.value.id, section, content)
    }
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleGeneratePlan = async () => {
  try {
    await planStore.generateContent(currentPlan.value.id)
    ElMessage.success('内容生成成功')
    // 刷新当前规划
    await planStore.loadPlan(currentPlan.value.id)
    selectPlan(planStore.currentPlan)
  } catch (error) {
    ElMessage.error('生成失败')
  }
}

// Spec 方法
const startCreateSpec = () => {
  isCreatingSpec.value = true
  newSpecForm.feature_name = ''
  newSpecForm.title = ''
  newSpecForm.description = ''
}

const cancelCreateSpec = () => {
  isCreatingSpec.value = false
}

const confirmCreateSpec = async () => {
  if (!newSpecForm.feature_name.trim() || !newSpecForm.title.trim()) {
    ElMessage.warning('请输入功能名称和标题')
    return
  }
  try {
    const data = await specStore.createSpec({
      feature_name: newSpecForm.feature_name,
      title: newSpecForm.title,
      description: newSpecForm.description,
    })
    isCreatingSpec.value = false
    selectSpec(data)
    ElMessage.success('规格创建成功')
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const selectSpec = async (spec) => {
  currentSpec.value = spec
  await specStore.loadSpecFile(spec.feature_name, currentFile.value)
  parseFileContent(specStore.currentFileContent?.content || '')
}

const backToSpecList = () => {
  currentSpec.value = null
}

const selectFile = async (filename) => {
  currentFile.value = filename
  if (currentSpec.value) {
    await specStore.loadSpecFile(currentSpec.value.feature_name, filename)
    parseFileContent(specStore.currentFileContent?.content || '')
  }
}

const parseFileContent = (content) => {
  Object.keys(fileSections).forEach(key => delete fileSections[key])
  if (!content) return

  const lines = content.split('\n')
  let currentSection = '内容'
  let currentContent = []

  for (const line of lines) {
    if (line.startsWith('## ')) {
      if (currentContent.length > 0) {
        fileSections[currentSection] = currentContent.join('\n').trim()
      }
      currentSection = line.replace('## ', '').trim()
      currentContent = []
    } else {
      currentContent.push(line)
    }
  }

  if (currentContent.length > 0) {
    fileSections[currentSection] = currentContent.join('\n').trim()
  }

  // 设置默认选中的标签
  const sections = Object.keys(fileSections)
  if (sections.length > 0) {
    activeSpecTab.value = sections[0]
  }
}

const saveSpec = async () => {
  try {
    // 重新组装文件内容
    let content = ''
    for (const [section, sectionContent] of Object.entries(fileSections)) {
      content += `## ${section}\n\n${sectionContent}\n\n`
    }
    await specStore.updateFile(currentSpec.value.feature_name, currentFile.value, { content })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleGenerateSpec = async () => {
  try {
    await specStore.generateContent(currentSpec.value.feature_name)
    ElMessage.success('内容生成成功')
    // 刷新当前文件
    await specStore.loadSpecFile(currentSpec.value.feature_name, currentFile.value)
    parseFileContent(specStore.currentFileContent?.content || '')
  } catch (error) {
    ElMessage.error('生成失败')
  }
}

const handleApproveSpec = async () => {
  try {
    await specStore.approveSpec(currentSpec.value.feature_name)
    ElMessage.success('规格已审批通过')
    // 刷新当前规格
    await specStore.loadSpec(currentSpec.value.feature_name)
    currentSpec.value = specStore.currentSpec
  } catch (error) {
    ElMessage.error('审批失败')
  }
}

const getFileDisplayName = (filename) => {
  return fileDisplayNames[filename] || filename
}

const getStatusType = (status) => {
  const statusMap = {
    'draft': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'approved': 'success',
    'archived': '',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'in_progress': '进行中',
    'completed': '已完成',
    'approved': '已审批',
    'archived': '已归档',
  }
  return statusMap[status] || status
}
</script>

<style scoped lang="scss">
.mode-header {
  margin-bottom: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
}

.plans-scrollbar,
.specs-scrollbar {
  max-height: 400px;
}

.plan-item,
.spec-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    background: var(--message-user-bg);
  }

  .plan-icon,
  .spec-icon {
    font-size: 24px;
    color: var(--primary-color);
  }

  .plan-info,
  .spec-info {
    flex: 1;

    .plan-title,
    .spec-title {
      font-weight: 500;
      margin-bottom: 4px;
    }

    .plan-desc,
    .spec-desc {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);

  .plan-title,
  .spec-title {
    font-weight: 600;
    font-size: 16px;
  }

  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.spec-layout {
  display: flex;
  gap: 16px;
  min-height: 400px;
}

.file-sidebar {
  width: 140px;
  flex-shrink: 0;

  .file-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 4px;
    font-size: 13px;

    &:hover {
      background: var(--border-lighter);
    }

    &.active {
      background: var(--message-user-bg);
      color: var(--primary-color);
      font-weight: 500;
    }

    .el-icon {
      font-size: 16px;
    }
  }
}

.file-content {
  flex: 1;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

.create-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-light);
}
</style>
