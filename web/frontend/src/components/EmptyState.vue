<template>
  <div class="empty-state">
    <div class="empty-content">
      <div class="welcome-icon">
        <el-icon :size="64" color="#409eff"><Watermelon /></el-icon>
      </div>
      <h1 class="welcome-title">{{ title }}</h1>
      <p class="welcome-desc">{{ description }}</p>

      <div class="quick-actions" v-if="actions.length > 0">
        <div class="actions-title">快捷功能</div>
        <div class="actions-grid">
          <div
            v-for="action in actions"
            :key="action.text"
            class="action-card"
            @click="$emit('action-click', action.text)"
          >
            <el-icon :size="24" :color="action.color || '#409eff'">
              <component :is="action.icon" />
            </el-icon>
            <span class="action-text">{{ action.text }}</span>
          </div>
        </div>
      </div>

      <div class="example-questions" v-if="examples.length > 0">
        <div class="examples-title">试试这样问</div>
        <div class="examples-list">
          <el-tag
            v-for="example in examples"
            :key="example"
            class="example-tag"
            effect="plain"
            @click="$emit('example-click', example)"
          >
            {{ example }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Watermelon, DataLine, Document, ChatLineRound } from '@element-plus/icons-vue'

defineProps({
  title: {
    type: String,
    default: '你好，我是水利智脑',
  },
  description: {
    type: String,
    default: '我可以帮助您进行洪水调度决策、水文分析等工作。请输入您的问题开始对话。',
  },
  actions: {
    type: Array,
    default: () => [
      { icon: 'DataLine', text: '洪水调度', color: '#409eff' },
      { icon: 'Document', text: '生成报告', color: '#67c23a' },
      { icon: 'ChatLineRound', text: '智能问答', color: '#e6a23c' },
    ],
  },
  examples: {
    type: Array,
    default: () => [
      '北江超标准洪水调度方案',
      '分析当前降雨情况',
      '生成调度指令文本',
      '评估水库泄洪影响',
    ],
  },
})

defineEmits(['action-click', 'example-click'])
</script>

<style scoped lang="scss">
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.empty-content {
  text-align: center;
  max-width: 600px;
}

.welcome-icon {
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.welcome-desc {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 40px;
}

.quick-actions {
  margin-bottom: 32px;

  .actions-title {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 16px;
  }
}

.actions-grid {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 24px;
  background: var(--bg-white);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px;

  &:hover {
    border-color: var(--primary-color);
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
    transform: translateY(-2px);
  }

  .action-text {
    font-size: 13px;
    color: var(--text-primary);
    font-weight: 500;
  }
}

.example-questions {
  .examples-title {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 16px;
  }
}

.examples-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.example-tag {
  cursor: pointer;
  padding: 8px 16px;
  font-size: 13px;
  transition: all 0.2s ease;

  &:hover {
    color: var(--primary-color);
    border-color: var(--primary-color);
    background: var(--message-user-bg);
  }
}
</style>
