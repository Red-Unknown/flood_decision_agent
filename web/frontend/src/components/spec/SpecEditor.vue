<template>
  <div class="spec-editor">
    <!-- 基本信息 -->
    <el-card class="editor-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-tag :type="getStatusType(spec.metadata?.status)">
            {{ getStatusText(spec.metadata?.status) }}
          </el-tag>
        </div>
      </template>

      <div class="info-display">
        <div class="info-item">
          <label>功能名称：</label>
          <span>{{ spec.feature_name }}</span>
        </div>
        <div class="info-item">
          <label>标题：</label>
          <span>{{ spec.title }}</span>
        </div>
        <div class="info-item">
          <label>描述：</label>
          <span>{{ spec.description || '暂无描述' }}</span>
        </div>
        <div class="info-item">
          <label>版本：</label>
          <span>v{{ spec.metadata?.version || 1 }}</span>
        </div>
        <div class="info-item">
          <label>更新时间：</label>
          <span>{{ formatTime(spec.metadata?.updated_at) }}</span>
        </div>
        <div v-if="spec.metadata?.approved_by" class="info-item">
          <label>审批人：</label>
          <span>{{ spec.metadata.approved_by }}</span>
        </div>
        <div v-if="spec.metadata?.approved_at" class="info-item">
          <label>审批时间：</label>
          <span>{{ formatTime(spec.metadata.approved_at) }}</span>
        </div>
      </div>
    </el-card>

    <!-- 文件内容章节 -->
    <el-card
      v-for="(content, section) in fileContentSections"
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
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  spec: {
    type: Object,
    required: true,
  },
  fileContent: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update-file', 'update-section'])

const editingSection = ref(null)

const sectionForm = reactive({
  section: '',
  content: '',
})

// 解析文件内容为章节
const fileContentSections = computed(() => {
  if (!props.fileContent?.content) return {}

  const sections = {}
  const content = props.fileContent.content
  const lines = content.split('\n')
  let currentSection = '内容'
  let currentContent = []

  for (const line of lines) {
    if (line.startsWith('## ')) {
      if (currentContent.length > 0) {
        sections[currentSection] = currentContent.join('\n').trim()
      }
      currentSection = line.replace('## ', '').trim()
      currentContent = []
    } else {
      currentContent.push(line)
    }
  }

  if (currentContent.length > 0) {
    sections[currentSection] = currentContent.join('\n').trim()
  }

  return sections
})

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
.spec-editor {
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

  :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 16px;

    th, td {
      border: 1px solid var(--border-light);
      padding: 8px 12px;
      text-align: left;
    }

    th {
      background: var(--bg-color);
      font-weight: 600;
    }
  }

  .empty-content {
    color: var(--text-secondary);
    font-style: italic;
    text-align: center;
    padding: 20px;
  }
}
</style>
