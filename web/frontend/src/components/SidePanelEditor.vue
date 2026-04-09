<template>
  <div class="side-panel-editor" :class="{ 'is-visible': isVisible }">
    <div class="panel-header">
      <div class="header-title">
        <el-icon v-if="mode === 'plan'"><Document /></el-icon>
        <el-icon v-else-if="mode === 'spec'"><Files /></el-icon>
        <span>{{ getPanelTitle() }}</span>
      </div>
      <div class="header-actions">
        <el-button
          :type="isEditing ? 'default' : 'primary'"
          size="small"
          @click="isEditing = !isEditing"
        >
          {{ isEditing ? '预览' : '编辑' }}
        </el-button>
        <el-button type="primary" size="small" @click="handleConfirm">
          <el-icon><Check /></el-icon>
          确认
        </el-button>
        <el-button size="small" @click="handleCancel">
          <el-icon><Close /></el-icon>
          取消
        </el-button>
        <el-button text circle size="small" @click="handleClose">
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <div class="panel-content" :class="{ 'has-generating-status': isGenerating }">
      <!-- Spec 模式文件标签页 -->
      <div v-if="mode === 'spec' && documentData?.files" class="file-tabs">
        <el-tabs v-model="activeFile" type="border-card">
          <el-tab-pane
            v-for="(file, key) in documentData.files"
            :key="key"
            :label="file.title || key"
            :name="key"
          >
            <div class="content-wrapper">
              <!-- 编辑模式 -->
              <div v-if="isEditing" class="markdown-editor">
                <el-input
                  v-model="fileContent[key]"
                  type="textarea"
                  :rows="20"
                  resize="none"
                />
              </div>
              <!-- 预览模式 -->
              <div v-else class="markdown-preview" v-html="renderMarkdown(fileContent[key] || '')"></div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- Plan 模式或 Spec 单文件模式 -->
      <div v-else class="content-wrapper">
        <!-- 编辑模式 -->
        <div v-if="isEditing" class="markdown-editor">
          <el-input
            v-model="editedContent"
            type="textarea"
            :rows="20"
            resize="none"
          />
        </div>
        <!-- 预览模式 -->
        <div v-else class="markdown-preview" v-html="renderMarkdown(editedContent)"></div>
      </div>

      <!-- 生成中状态 -->
      <div v-if="isGenerating" class="generating-status">
        <el-progress
          :percentage="generationProgress"
          :stroke-width="8"
          striped
          striped-flow
        />
        <p class="generating-text">正在生成文档...</p>
      </div>
    </div>

    <!-- 底部修改输入框 -->
    <div class="panel-footer">
      <div class="modification-input">
        <el-input
          v-model="modificationRequest"
          placeholder="输入自然语言修改指令，如：请增加关于应急预案的章节"
          size="large"
        >
          <template #append>
            <el-button type="primary" @click="handleModify" :loading="isModifying">
              修改
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Document, Files, Check, Close, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false,
  },
  mode: {
    type: String,
    default: null, // 'plan' | 'spec'
  },
  documentData: {
    type: Object,
    default: null,
  },
  isGenerating: {
    type: Boolean,
    default: false,
  },
  generationProgress: {
    type: Number,
    default: 0,
  },
  isModifying: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'save', 'confirm', 'cancel', 'modify'])

// State
const editedContent = ref('')
const fileContent = ref({})
const activeFile = ref('spec')
const modificationRequest = ref('')
const isEditing = ref(false)

// 清理 Markdown 内容（移除代码块标记等）
const cleanMarkdown = (content) => {
  if (!content) return ''
  // 移除开头的 ```markdown 或 ```
  content = content.replace(/^```markdown\s*\n/i, '')
  content = content.replace(/^```\s*\n/, '')
  // 移除结尾的 ```
  content = content.replace(/\n```\s*$/g, '')
  content = content.replace(/```\s*$/g, '')
  return content.trim()
}

// Markdown 渲染
const renderMarkdown = (content) => {
  if (!content) return ''
  try {
    const cleaned = cleanMarkdown(content)
    return marked.parse(cleaned, { breaks: true })
  } catch (e) {
    console.error('Markdown 渲染失败:', e)
    return content
  }
}

// 获取当前内容（用于流式预览）
const getCurrentContent = () => {
  if (props.mode === 'plan') {
    return editedContent.value
  } else if (props.mode === 'spec') {
    return fileContent.value[activeFile.value] || ''
  }
  return ''
}

// 监听文档数据变化
watch(() => props.documentData, (newData) => {
  console.log('[SidePanelEditor] documentData 变化:', newData?.content?.length || 0)
  if (newData) {
    if (props.mode === 'plan') {
      const newContent = newData.content || ''
      if (newContent !== editedContent.value) {
        editedContent.value = newContent
        console.log('[SidePanelEditor] 更新 editedContent:', newContent.length)
      }
    } else if (props.mode === 'spec') {
      // 初始化文件内容
      if (newData.files) {
        Object.keys(newData.files).forEach(key => {
          fileContent.value[key] = newData.files[key].content || ''
        })
      } else if (newData.content) {
        fileContent.value['spec'] = newData.content
      }
    }
  }
}, { immediate: true, deep: true })

// 单独监听 content 字段的变化（用于流式更新）
watch(() => props.documentData?.content, (newContent) => {
  if (props.mode === 'plan' && newContent !== undefined && newContent !== editedContent.value) {
    editedContent.value = newContent
    console.log('[SidePanelEditor] content 字段变化，更新 editedContent:', newContent?.length || 0)
  }
}, { immediate: false })

// 监听 Spec 模式的 files 变化（用于流式更新）
watch(() => props.documentData?.files, (newFiles) => {
  if (props.mode === 'spec' && newFiles) {
    Object.keys(newFiles).forEach(key => {
      const newContent = newFiles[key]?.content
      if (newContent !== undefined && fileContent.value[key] !== newContent) {
        fileContent.value[key] = newContent
        console.log(`[SidePanelEditor] files.${key}.content 字段变化，更新:`, newContent?.length || 0)
      }
    })
  }
}, { immediate: false, deep: true })

// 方法
const getPanelTitle = () => {
  if (props.mode === 'plan') {
    return props.documentData?.title || '规划文档'
  } else if (props.mode === 'spec') {
    return props.documentData?.display_name || '规格文档'
  }
  return '文档编辑器'
}

const handleClose = () => {
  emit('close')
}

const handleSave = () => {
  if (props.mode === 'plan') {
    emit('save', {
      mode: 'plan',
      content: editedContent.value,
    })
  } else if (props.mode === 'spec') {
    emit('save', {
      mode: 'spec',
      activeFile: activeFile.value,
      fileContent: fileContent.value,
    })
  }
  ElMessage.success('文档已保存')
}

const handleConfirm = () => {
  // 先保存
  handleSave()
  // 然后确认
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}

const handleModify = () => {
  const instruction = modificationRequest.value.trim()
  if (!instruction) {
    ElMessage.warning('请输入修改指令')
    return
  }

  emit('modify', {
    instruction,
    section: null,
    file: activeFile.value,
  })

  // 清空输入
  modificationRequest.value = ''
}
</script>

<style scoped lang="scss">
.side-panel-editor {
  position: fixed;
  top: 0;
  right: -480px;
  width: 480px;
  height: 100vh;
  background: var(--bg-white);
  border-left: 1px solid var(--border-color);
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  transition: right 0.3s ease;
  z-index: 100;

  &.is-visible {
    right: 0;
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-color);

  .header-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 500;

    .el-icon {
      font-size: 20px;
      color: var(--el-color-primary);
    }
  }

  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.panel-content {
  flex: 1;
  overflow: hidden;
  position: relative;

  .file-tabs {
    height: 100%;

    :deep(.el-tabs) {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    :deep(.el-tabs__content) {
      flex: 1;
      overflow: auto;
    }
  }

  .markdown-editor {
    height: 100%;
    padding: 16px;

    :deep(.el-textarea__inner) {
      height: 100%;
      min-height: 400px;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 14px;
      line-height: 1.6;
    }
  }
}

.generating-status {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.98);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 12px 16px;
  gap: 8px;
  z-index: 10;
  border-bottom: 1px solid var(--border-color);

  .generating-text {
    color: var(--text-secondary);
    font-size: 14px;
    margin: 0;
  }
}

// 生成状态下给内容区域添加顶部边距
.has-generating-status {
  padding-top: 80px;
}

.content-wrapper {
  height: 100%;
  overflow: auto;
}

.markdown-preview {
  height: 100%;
  padding: 16px;
  overflow-y: auto;
  background: white;

  :deep(h1) {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 16px;
    color: var(--text-primary);
  }

  :deep(h2) {
    font-size: 20px;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 12px;
    color: var(--text-primary);
  }

  :deep(h3) {
    font-size: 18px;
    font-weight: 600;
    margin-top: 20px;
    margin-bottom: 10px;
    color: var(--text-primary);
  }

  :deep(p) {
    margin-bottom: 12px;
    line-height: 1.6;
    color: var(--text-regular);
  }

  :deep(ul), :deep(ol) {
    margin-bottom: 12px;
    padding-left: 24px;
  }

  :deep(li) {
    margin-bottom: 6px;
    line-height: 1.6;
  }

  :deep(code) {
    background: var(--bg-color);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 14px;
  }

  :deep(pre) {
    background: var(--bg-color);
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    margin-bottom: 16px;

    code {
      background: none;
      padding: 0;
    }
  }

  :deep(blockquote) {
    border-left: 4px solid var(--el-color-primary);
    padding-left: 16px;
    margin: 16px 0;
    color: var(--text-secondary);
  }

  :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 16px;

    th, td {
      border: 1px solid var(--border-color);
      padding: 8px 12px;
      text-align: left;
    }

    th {
      background: var(--bg-color);
      font-weight: 600;
    }
  }

  :deep(a) {
    color: var(--el-color-primary);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

.panel-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-color);

  .modification-input {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
    }
  }
}
</style>
