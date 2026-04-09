<template>
  <div class="plan-editor">
    <!-- 基本信息 -->
    <el-card class="editor-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-button
            v-if="!isEditingBasic"
            link
            type="primary"
            @click="startEditBasic"
          >
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <template v-else>
            <el-button link @click="cancelEditBasic">取消</el-button>
            <el-button link type="primary" @click="saveBasic">保存</el-button>
          </template>
        </div>
      </template>

      <div v-if="!isEditingBasic" class="info-display">
        <div class="info-item">
          <label>标题：</label>
          <span>{{ plan.title }}</span>
        </div>
        <div class="info-item">
          <label>描述：</label>
          <span>{{ plan.description || '暂无描述' }}</span>
        </div>
        <div class="info-item">
          <label>状态：</label>
          <el-tag :type="getStatusType(plan.metadata?.status)">
            {{ getStatusText(plan.metadata?.status) }}
          </el-tag>
        </div>
        <div class="info-item">
          <label>版本：</label>
          <span>v{{ plan.metadata?.version || 1 }}</span>
        </div>
        <div class="info-item">
          <label>更新时间：</label>
          <span>{{ formatTime(plan.metadata?.updated_at) }}</span>
        </div>
      </div>

      <el-form v-else :model="basicForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="basicForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="basicForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 规划内容章节 -->
    <el-card
      v-for="(content, section) in plan.sections"
      :key="section"
      class="editor-card"
      shadow="hover"
    >
      <template #header>
        <div class="card-header">
          <span>{{ section }}</span>
          <el-button
            v-if="editingSection !== section"
            link
            type="primary"
            @click="startEditSection(section, content)"
          >
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <template v-else>
            <el-button link @click="cancelEditSection">取消</el-button>
            <el-button link type="primary" @click="saveSection">保存</el-button>
          </template>
        </div>
      </template>

      <div v-if="editingSection !== section" class="section-content markdown-body" v-html="renderMarkdown(content)"></div>
      <el-input
        v-else
        v-model="sectionForm.content"
        type="textarea"
        :rows="10"
        placeholder="请输入内容..."
      />
    </el-card>

    <!-- 添加章节按钮 -->
    <div class="add-section">
      <el-button type="primary" plain @click="showAddSection = true">
        <el-icon><Plus /></el-icon>
        添加章节
      </el-button>
    </div>

    <!-- 添加章节对话框 -->
    <el-dialog v-model="showAddSection" title="添加章节" width="500px">
      <el-form :model="newSectionForm" label-width="80px">
        <el-form-item label="章节名称">
          <el-input v-model="newSectionForm.name" placeholder="请输入章节名称" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="newSectionForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入章节内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddSection = false">取消</el-button>
        <el-button type="primary" @click="addSection">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  plan: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update', 'update-section'])

const isEditingBasic = ref(false)
const editingSection = ref(null)
const showAddSection = ref(false)

const basicForm = reactive({
  title: '',
  description: '',
})

const sectionForm = reactive({
  section: '',
  content: '',
})

const newSectionForm = reactive({
  name: '',
  content: '',
})

const startEditBasic = () => {
  basicForm.title = props.plan.title
  basicForm.description = props.plan.description || ''
  isEditingBasic.value = true
}

const cancelEditBasic = () => {
  isEditingBasic.value = false
}

const saveBasic = () => {
  emit('update', {
    title: basicForm.title,
    description: basicForm.description,
  })
  isEditingBasic.value = false
}

const startEditSection = (section, content) => {
  sectionForm.section = section
  sectionForm.content = content
  editingSection.value = section
}

const cancelEditSection = () => {
  editingSection.value = null
}

const saveSection = () => {
  emit('update-section', sectionForm.section, sectionForm.content)
  editingSection.value = null
}

const addSection = () => {
  if (!newSectionForm.name.trim()) return
  emit('update-section', newSectionForm.name, newSectionForm.content)
  showAddSection.value = false
  newSectionForm.name = ''
  newSectionForm.content = ''
}

const renderMarkdown = (content) => {
  if (!content) return '<p class="empty-content">暂无内容</p>'
  return marked(content)
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
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
.plan-editor {
  padding: 20px 0;
}

.editor-card {
  margin-bottom: 20px;

  :deep(.el-card__header) {
    padding: 12px 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.info-display {
  .info-item {
    display: flex;
    margin-bottom: 12px;
    line-height: 1.6;

    &:last-child {
      margin-bottom: 0;
    }

    label {
      width: 100px;
      color: var(--text-secondary);
      flex-shrink: 0;
    }

    span {
      flex: 1;
      color: var(--text-primary);
    }
  }
}

.section-content {
  line-height: 1.8;

  :deep(h1), :deep(h2), :deep(h3), :deep(h4) {
    margin-top: 16px;
    margin-bottom: 12px;
    color: var(--text-primary);
  }

  :deep(p) {
    margin-bottom: 12px;
    color: var(--text-primary);
  }

  :deep(ul), :deep(ol) {
    margin-bottom: 12px;
    padding-left: 24px;
  }

  :deep(li) {
    margin-bottom: 6px;
  }

  :deep(code) {
    background: var(--bg-color);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
  }

  :deep(pre) {
    background: var(--bg-color);
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;

    code {
      background: none;
      padding: 0;
    }
  }

  :deep(blockquote) {
    border-left: 4px solid var(--primary-color);
    padding-left: 16px;
    margin: 12px 0;
    color: var(--text-secondary);
  }

  .empty-content {
    color: var(--text-secondary);
    font-style: italic;
    text-align: center;
    padding: 20px;
  }
}

.add-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}
</style>
