<template>
  <aside class="chat-sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <div class="logo">
        <el-icon :size="24" color="#409eff"><Watermelon /></el-icon>
        <span v-if="!isCollapsed" class="logo-text">水利智脑</span>
      </div>
      <el-button
        v-if="!isCollapsed"
        type="primary"
        class="new-chat-btn"
        @click="handleNewChat"
      >
        <el-icon><Plus /></el-icon>
        <span>新对话</span>
      </el-button>
      <el-button
        v-else
        type="primary"
        circle
        @click="handleNewChat"
      >
        <el-icon><Plus /></el-icon>
      </el-button>
    </div>

    <div class="conversations-list" v-if="!isCollapsed">
      <div class="list-header">
        <span class="list-title">历史对话</span>
        <el-button
          v-if="conversations.length > 0"
          type="danger"
          link
          size="small"
          @click="handleClearAll"
        >
          清空全部
        </el-button>
      </div>

      <el-scrollbar class="conversations-scrollbar">
        <div
          v-for="conversation in conversations"
          :key="conversation.id"
          class="conversation-item"
          :class="{ active: currentConversation?.id === conversation.id }"
          @click="handleSelectConversation(conversation.id)"
        >
          <el-icon class="conversation-icon"><ChatDotRound /></el-icon>
          <div class="conversation-info">
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-meta">
              <span>{{ formatTime(conversation.updated_at) }}</span>
              <span v-if="conversation.message_count > 0">
                {{ conversation.message_count }}条消息
              </span>
            </div>
          </div>
          <el-dropdown
            trigger="click"
            @command="(cmd) => handleCommand(cmd, conversation.id)"
            @click.stop
          >
            <el-button link class="more-btn">
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="rename">
                  <el-icon><Edit /></el-icon>重命名
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <el-icon><Delete /></el-icon>删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <el-empty
          v-if="conversations.length === 0 && !isLoading"
          description="暂无历史对话"
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

    <!-- 重命名对话框 -->
    <el-dialog
      v-model="renameDialogVisible"
      title="重命名对话"
      width="400px"
    >
      <el-input
        v-model="newTitle"
        placeholder="请输入新标题"
        maxlength="50"
        show-word-limit
      />
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确定</el-button>
      </template>
    </el-dialog>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'new-chat'])

const chatStore = useChatStore()
const isCollapsed = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const conversations = computed(() => chatStore.conversationList)
const currentConversation = computed(() => chatStore.currentConversation)
const isLoading = computed(() => chatStore.isLoading)

const renameDialogVisible = ref(false)
const newTitle = ref('')
const renamingConversationId = ref(null)

onMounted(() => {
  chatStore.loadConversations()
})

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleNewChat = () => {
  emit('new-chat')
}

const handleSelectConversation = (conversationId) => {
  chatStore.selectConversation(conversationId)
}

const handleCommand = (command, conversationId) => {
  if (command === 'delete') {
    handleDeleteConversation(conversationId)
  } else if (command === 'rename') {
    handleRenameConversation(conversationId)
  }
}

const handleDeleteConversation = async (conversationId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await chatStore.deleteConversation(conversationId)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleRenameConversation = (conversationId) => {
  const conversation = conversations.value.find(c => c.id === conversationId)
  if (conversation) {
    newTitle.value = conversation.title
    renamingConversationId.value = conversationId
    renameDialogVisible.value = true
  }
}

const confirmRename = () => {
  if (newTitle.value.trim()) {
    chatStore.updateConversationTitle(renamingConversationId.value, newTitle.value.trim())
    renameDialogVisible.value = false
    ElMessage.success('重命名成功')
  }
}

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有对话吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    // 逐个删除所有对话
    for (const conversation of [...conversations.value]) {
      await chatStore.deleteConversation(conversation.id)
    }
    ElMessage.success('已清空所有对话')
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

  // 小于1小时显示"X分钟前"
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return minutes < 1 ? '刚刚' : `${minutes}分钟前`
  }
  // 小于24小时显示"X小时前"
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }
  // 否则显示日期
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<style scoped lang="scss">
.chat-sidebar {
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

  .new-chat-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }
}

.conversations-list {
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

  .conversations-scrollbar {
    flex: 1;

    :deep(.el-scrollbar__wrap) {
      padding: 0 8px;
    }
  }
}

.conversation-item {
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

    .conversation-title {
      color: var(--primary-color);
      font-weight: 500;
    }
  }

  .conversation-icon {
    color: var(--text-secondary);
    font-size: 18px;
  }

  .conversation-info {
    flex: 1;
    min-width: 0;

    .conversation-title {
      font-size: 14px;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-bottom: 2px;
    }

    .conversation-meta {
      font-size: 12px;
      color: var(--text-secondary);
      display: flex;
      gap: 8px;
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
