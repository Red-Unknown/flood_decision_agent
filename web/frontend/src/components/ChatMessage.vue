<template>
  <div
    class="chat-message"
    :class="{ 'message-user': isUser, 'message-ai': !isUser, 'message-error': message.isError }"
  >
    <div class="message-avatar">
      <el-avatar
        :size="36"
        :icon="isUser ? UserFilled : Cpu"
        :class="{ 'user-avatar': isUser, 'ai-avatar': !isUser }"
      />
    </div>
    <div class="message-content">
      <div class="message-header">
        <span class="message-role">{{ roleText }}</span>
        <span class="message-time">{{ formatTime(message.timestamp) }}</span>
      </div>
      <div class="message-body">
        <!-- 流式输出中 -->
        <div v-if="isStreaming && isLastMessage" class="streaming-text markdown-body">
          <div v-html="renderedStreamingContent"></div>
          <span class="cursor"></span>
        </div>
        <!-- 完整消息 -->
        <div v-else class="message-text markdown-body" v-html="renderedContent"></div>
      </div>
    </div>
    <div class="message-actions" v-if="!isStreaming">
      <el-button
        link
        size="small"
        @click="handleCopy"
        :title="'复制'"
      >
        <el-icon><CopyDocument /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { UserFilled, Cpu, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
  isLastMessage: {
    type: Boolean,
    default: false,
  },
  streamingContent: {
    type: String,
    default: '',
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
})

const isUser = computed(() => props.message.role === 'user')

const roleText = computed(() => {
  return isUser.value ? '我' : 'AI助手'
})

/**
 * 简单的Markdown渲染
 * 支持：标题、粗体、列表、代码块
 */
const renderMarkdown = (text) => {
  if (!text) return ''

  let html = text

  // 转义HTML特殊字符
  html = html.replace(/&/g, '&amp;')
             .replace(/</g, '&lt;')
             .replace(/>/g, '&gt;')

  // 代码块 ```code```
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre class="code-block"><code>${code}</code></pre>`
  })

  // 行内代码 `code`
  html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')

  // 标题 ## 
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')

  // 粗体 **text**
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

  // 列表项 - 
  html = html.replace(/^- (.*$)/gim, '<li>$1</li>')

  // 将连续的<li>包装在<ul>中
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
    return `<ul>${match}</ul>`
  })

  // 换行符转换为<br>
  html = html.replace(/\n/g, '<br>')

  return html
}

const renderedContent = computed(() => {
  return renderMarkdown(props.message.content || '')
})

const renderedStreamingContent = computed(() => {
  return renderMarkdown(props.streamingContent || '')
})

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    ElMessage.success('已复制到剪贴板')
  } catch (err) {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = props.message.content
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    ElMessage.success('已复制到剪贴板')
  }
}
</script>

<style scoped lang="scss">
.chat-message {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: var(--bg-color);

    .message-actions {
      opacity: 1;
    }
  }

  &.message-user {
    flex-direction: row-reverse;

    .message-content {
      align-items: flex-end;
    }

    .message-body {
      background: var(--message-user-bg);
      border-radius: 12px 12px 2px 12px;
    }

    .message-header {
      flex-direction: row-reverse;
    }
  }

  &.message-ai {
    .message-body {
      background: var(--bg-white);
      border: 1px solid var(--border-light);
      border-radius: 12px 12px 12px 2px;
    }
  }

  &.message-error {
    .message-body {
      background: #fef0f0;
      border: 1px solid #fde2e2;
    }
  }
}

.message-avatar {
  flex-shrink: 0;

  .user-avatar {
    background: var(--primary-color);
  }

  .ai-avatar {
    background: #67c23a;
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: calc(100% - 100px);
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;

  .message-role {
    color: var(--text-primary);
    font-weight: 500;
  }

  .message-time {
    color: var(--text-secondary);
  }
}

.message-body {
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  word-wrap: break-word;
}

.streaming-text {
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  background: var(--bg-white);
  border: 1px solid var(--border-light);
  border-radius: 12px 12px 12px 2px;
  white-space: pre-wrap;
  word-wrap: break-word;

  .cursor {
    display: inline-block;
    width: 2px;
    height: 1.2em;
    background: var(--primary-color);
    margin-left: 2px;
    animation: blink 1s infinite;
    vertical-align: text-bottom;
  }
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

.message-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
  align-self: flex-end;
  padding-bottom: 8px;

  .el-button {
    color: var(--text-secondary);

    &:hover {
      color: var(--primary-color);
    }
  }
}

// Markdown样式
.markdown-body {
  :deep(h1) {
    font-size: 20px;
    font-weight: 600;
    margin: 16px 0 12px;
    color: var(--text-primary);
  }

  :deep(h2) {
    font-size: 18px;
    font-weight: 600;
    margin: 14px 0 10px;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border-light);
    padding-bottom: 6px;
  }

  :deep(h3) {
    font-size: 16px;
    font-weight: 600;
    margin: 12px 0 8px;
    color: var(--text-primary);
  }

  :deep(strong) {
    font-weight: 600;
    color: var(--text-primary);
  }

  :deep(ul) {
    margin: 8px 0;
    padding-left: 20px;
  }

  :deep(li) {
    margin: 4px 0;
    line-height: 1.6;
  }

  :deep(.code-block) {
    background: #f6f8fa;
    border: 1px solid var(--border-light);
    border-radius: 6px;
    padding: 12px 16px;
    margin: 12px 0;
    overflow-x: auto;

    code {
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 13px;
      line-height: 1.5;
      color: var(--text-primary);
      background: transparent;
      padding: 0;
    }
  }

  :deep(.inline-code) {
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 13px;
    background: #f6f8fa;
    padding: 2px 6px;
    border-radius: 4px;
    color: #d73a49;
  }

  :deep(br) {
    display: block;
    content: "";
    margin-top: 4px;
  }
}
</style>
