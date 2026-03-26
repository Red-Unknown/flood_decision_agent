<template>
  <div class="chat-view">
    <ChatSidebar
      v-model="sidebarCollapsed"
      @new-chat="handleNewChat"
    />

    <div class="chat-main" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <ChatHeader
        :title="headerTitle"
        :subtitle="headerSubtitle"
        :sidebar-collapsed="sidebarCollapsed"
        :has-messages="hasMessages"
        :is-streaming="isStreaming"
        @toggle-sidebar="toggleSidebar"
        @clear="handleClear"
        @new-chat="handleNewChat"
      />

      <div class="chat-content">
        <template v-if="!hasMessages && !isStreaming">
          <EmptyState
            @action-click="handleQuickAction"
            @example-click="handleExampleClick"
          />
        </template>

        <template v-else>
          <el-scrollbar ref="messagesScrollbar" class="messages-container">
            <div class="messages-wrapper">
              <!-- 消息列表 -->
              <ChatMessage
                v-for="(message, index) in messages"
                :key="index"
                :message="message"
                :is-last-message="index === messages.length - 1 && message.role === 'assistant'"
                :streaming-content="streamingContent"
                :is-streaming="isStreaming && index === messages.length - 1 && message.role === 'assistant'"
              />

              <!-- 流式消息占位（当AI正在回复但还没有添加到messages时） -->
              <ChatMessage
                v-if="isStreaming && !hasStreamingMessage"
                :message="{ role: 'assistant', content: '', timestamp: Date.now() / 1000 }"
                :is-last-message="true"
                :streaming-content="streamingContent"
                :is-streaming="true"
              />

              <!-- 过程性事件时间线 -->
              <ProcessTimeline
                v-if="hasProcessEvents || isStreaming"
                :events="currentProcessEvents"
                :loading="isStreaming && processEvents.length === 0"
                @refresh="refreshProcessEvents"
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

      <ChatInput
        :is-streaming="isStreaming"
        @send="handleSend"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat.js'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatHeader from '@/components/ChatHeader.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/ChatInput.vue'
import EmptyState from '@/components/EmptyState.vue'
import ProcessTimeline from '@/components/ProcessTimeline.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

// 状态
const sidebarCollapsed = ref(false)
const messagesScrollbar = ref(null)

// 计算属性
const messages = computed(() => chatStore.currentMessages)
const hasMessages = computed(() => chatStore.hasMessages)
const isStreaming = computed(() => chatStore.isStreaming)
const streamingContent = computed(() => chatStore.streamingContent)
const currentConversation = computed(() => chatStore.currentConversation)
const currentProcessEvents = computed(() => chatStore.currentProcessEvents)
const hasProcessEvents = computed(() => chatStore.hasProcessEvents)
const error = computed(() => chatStore.error)

const hasStreamingMessage = computed(() => {
  const lastMessage = messages.value[messages.value.length - 1]
  return lastMessage && lastMessage.role === 'assistant' && isStreaming.value
})

const headerTitle = computed(() => {
  return currentConversation.value?.title || '水利智脑'
})

const headerSubtitle = computed(() => {
  if (isStreaming.value) {
    return '正在思考...'
  }
  return currentConversation.value ? '' : '开始新对话'
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleNewChat = async () => {
  await chatStore.createConversation()
  router.push('/')
}

const handleSend = async (message) => {
  if (!message.trim()) return

  await chatStore.sendMessage(message)

  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
  })
}

const handleClear = async () => {
  try {
    await chatStore.clearCurrentConversation()
    ElMessage.success('对话已清空')
  } catch (error) {
    ElMessage.error('清空失败')
  }
}

const handleQuickAction = (action) => {
  const actionMessages = {
    '洪水调度': '请帮我制定北江超标准洪水调度方案',
    '生成报告': '请生成一份洪水调度分析报告',
    '智能问答': '什么是洪水调度决策链？',
  }
  const message = actionMessages[action] || action
  handleSend(message)
}

const handleExampleClick = (example) => {
  handleSend(example)
}

const refreshProcessEvents = async () => {
  if (currentConversation.value) {
    await chatStore.selectConversation(currentConversation.value.id)
    ElMessage.success('已刷新')
  }
}

const clearError = () => {
  chatStore.error = null
}

const scrollToBottom = () => {
  if (messagesScrollbar.value) {
    const wrap = messagesScrollbar.value.wrapRef
    if (wrap) {
      wrap.scrollTop = wrap.scrollHeight
    }
  }
}

// 监听消息变化，自动滚动
watch(
  () => messages.value.length,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

// 监听流式内容变化，自动滚动
watch(
  () => streamingContent.value,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

// 监听过程性事件变化，自动滚动
watch(
  () => currentProcessEvents.value.length,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

// 监听路由参数，加载指定对话
watch(
  () => route.params.conversationId,
  async (conversationId) => {
    if (conversationId) {
      await chatStore.selectConversation(conversationId)
    }
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.chat-view {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-white);
  transition: margin-left 0.3s ease;
}

.chat-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
}

.messages-container {
  flex: 1;

  :deep(.el-scrollbar__wrap) {
    padding: 20px 0;
  }
}

.messages-wrapper {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  padding: 0 20px;
}

.error-alert {
  margin: 16px 0;
}
</style>
