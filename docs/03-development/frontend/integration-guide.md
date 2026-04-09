# Plan/Spec 模式前端集成指南

## 概述

本文档为前端工程师提供 Plan/Spec 模式增强功能的集成指南，包括界面设计建议、API 调用示例和状态管理方案。

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      前端应用                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  聊天界面   │  │  Plan编辑器 │  │  状态显示   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          │                                  │
│                   ┌──────┴──────┐                          │
│                   │  状态管理   │                          │
│                   │  (Pinia/   │                          │
│                   │   Redux)   │                          │
│                   └──────┬──────┘                          │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTP/WebSocket
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      后端 API                               │
└─────────────────────────────────────────────────────────────┘
```

## 核心功能集成

### 1. 模式识别与选择

**功能描述**: 根据用户输入自动推荐处理模式，同时允许用户手动选择。

**界面设计建议**:

```
┌─────────────────────────────────────┐
│  用户输入                            │
│  ┌─────────────────────────────┐   │
│  │ 设计一个洪水预警系统...      │   │
│  └─────────────────────────────┘   │
│                                     │
│  [推荐：Plan模式]  [模式选择 ▼]     │
│                    - 自动检测      │
│                    - 简单模式      │
│                    - Plan模式      │
│                    - Spec模式      │
└─────────────────────────────────────┘
```

**API 调用**:

```typescript
// 检测模式
async function detectMode(userInput: string) {
  const response = await fetch('/api/mode/detect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput })
  });
  return await response.json();
}

// 使用示例
const result = await detectMode("设计一个洪水预警系统");
console.log(result.recommended_mode);  // "plan"
console.log(result.confidence);        // 0.85
```

**状态管理**:

```typescript
// stores/modeStore.ts
import { defineStore } from 'pinia';

export const useModeStore = defineStore('mode', {
  state: () => ({
    recommendedMode: 'auto',
    selectedMode: 'auto',
    confidence: 0,
    metrics: null
  }),
  
  actions: {
    async detectMode(userInput: string) {
      const result = await detectMode(userInput);
      this.recommendedMode = result.recommended_mode;
      this.confidence = result.confidence;
      this.metrics = result.metrics;
    },
    
    setMode(mode: string) {
      this.selectedMode = mode;
    }
  }
});
```

### 2. 三种模式的界面流程

#### 普通模式 (Simple)

**流程**: 用户输入 → 直接返回答案

**界面**:

```
用户: 查询今天天气

系统: [正在思考...]

系统: 今天天气晴朗，气温 25-30°C，适合户外活动。
```

**特点**:

- 无需确认
- 快速响应
- 单轮交互

#### Plan 模式

**流程**: 用户输入 → 生成规划 → 用户编辑/确认 → 执行

**界面**:

```
用户: 设计一个洪水预警系统

系统: [正在生成规划...]

系统: 已为您生成规划文档，请查看和编辑：

┌─────────────────────────────────────┐
│  📋 洪水预警系统设计规划             │
│                                     │
│  [编辑] [确认] [取消]               │
│                                     │
│  ## 概述                            │
│  本规划旨在设计...                   │
│                                     │
│  ## 目标                            │
│  - 预警准确率≥95%                   │
│  - 响应时间≤5分钟                   │
│                                     │
│  [展开更多]                         │
└─────────────────────────────────────┘
```

**编辑器设计**:

```
┌─────────────────────────────────────────────────┐
│  编辑规划文档                     [保存] [取消]  │
├─────────────────────────────────────────────────┤
│  章节导航 │ 编辑器                              │
│  - 概述   │ ┌───────────────────────────────┐  │
│  - 目标   │ │ # 洪水预警系统设计规划        │  │
│  - 步骤   │ │                               │  │
│  - 标准   │ │ ## 概述                       │  │
│  - 风险   │ │ 本规划旨在...                 │  │
│  - 备注   │ │                               │  │
│           │ │ ## 目标                       │  │
│           │ │ - 准确率≥95%                 │  │
│           │ └───────────────────────────────┘  │
│           │                                    │
│           │ [预览]                             │
└─────────────────────────────────────────────────┘
```

**API 调用**:

```typescript
// 生成规划
async function generatePlan(userInput: string) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: userInput,
      preferred_mode: 'plan'
    })
  });
  return await response.json();
}

// 更新章节
async function updateSection(planId: string, section: string, content: string) {
  const response = await fetch(`/api/plans/${planId}/section`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ section, content })
  });
  return await response.json();
}

// 确认规划
async function confirmPlan(planId: string, action: 'proceed' | 'upgrade_to_spec') {
  const response = await fetch(`/api/plans/${planId}/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  });
  return await response.json();
}
```

#### Spec 模式

**流程**: 用户输入 → 生成规格套装 → 多轮确认 → 执行

**界面**:

```
系统: 已为您生成详细规格文档，请逐步确认：

┌─────────────────────────────────────┐
│  📑 洪水预警系统V2 - 规格文档        │
│                                     │
│  [1. 概述 ✓] [2. 功能需求 ●] [3. 技术方案] │
│  [4. 接口定义] [5. 验收标准]         │
│                                     │
│  ## 功能需求                        │
│  - 支持雷达、卫星、站点数据          │
│  - 预警准确率≥95%                   │
│                                     │
│  [修改] [确认并继续] [返回上一步]    │
└─────────────────────────────────────┘
```

### 3. 取消与恢复机制

**取消按钮位置**:

```
┌─────────────────────────────────────┐
│  当前任务: Plan模式 - 生成规划中    │
│                                     │
│  [进度条: ████████░░ 80%]           │
│                                     │
│                    [取消任务]       │
└─────────────────────────────────────┘
```

**取消确认对话框**:

```
┌─────────────────────────────────────┐
│  ⚠️  确认取消                        │
│                                     │
│  取消后，当前进度将被保存，您可以    │
│  稍后恢复继续。                      │
│                                     │
│  [取消并保存] [直接退出] [继续任务]  │
└─────────────────────────────────────┘
```

**断线恢复提示**:

```
┌─────────────────────────────────────┐
│  🔄 检测到未完成的任务               │
│                                     │
│  您有一个 Plan 模式的任务在 10 分钟  │
│  前被中断。                          │
│                                     │
│  [恢复任务] [放弃并新建]             │
└─────────────────────────────────────┘
```

**API 调用**:

```typescript
// 取消任务
async function cancelPlan(planId: string, reason: string) {
  const response = await fetch(`/api/plans/${planId}/cancel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason, preserve_state: true })
  });
  return await response.json();
}

// 恢复任务
async function resumeSession(sessionId: string) {
  const response = await fetch('/api/resume', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId })
  });
  return await response.json();
}

// 查询会话状态
async function getSessionStatus(sessionId: string) {
  const response = await fetch(`/api/sessions/${sessionId}/status`);
  return await response.json();
}
```

### 4. 状态显示

**模式标签**:

```
┌─────────────────────────────────────┐
│  💬 对话                             │
│  当前模式: [Plan模式 📝]            │
│  状态: [等待确认 ⏳]                 │
└─────────────────────────────────────┘
```

**进度指示器**:

```
普通模式: [直接回答 ✓]

Plan 模式:
[意图理解 ✓] → [生成规划 ✓] → [等待确认 ⏳] → [执行]

Spec 模式:
[意图理解 ✓] → [生成规格 ✓] → [确认需求 ⏳] → [确认技术方案] → [执行]
```

**状态颜色定义**:

| 状态   | 颜色    | 说明     |
| ---- | ----- | ------ |
| 处理中  | 🔵 蓝色 | 系统正在处理 |
| 等待确认 | 🟡 黄色 | 需要用户操作 |
| 已完成  | 🟢 绿色 | 任务完成   |
| 已取消  | 🔴 红色 | 任务被取消  |
| 可恢复  | 🟠 橙色 | 有断点可恢复 |

## 状态管理方案

### 全局状态设计

```typescript
// stores/sessionStore.ts
interface SessionState {
  sessionId: string | null;
  mode: 'simple' | 'plan' | 'spec' | null;
  stage: string;
  status: 'idle' | 'processing' | 'awaiting_confirmation' | 'completed' | 'cancelled';
  currentDocument: {
    type: 'plan' | 'spec';
    id: string;
    content?: string;
  } | null;
  canResume: boolean;
  messages: Message[];
}

export const useSessionStore = defineStore('session', {
  state: (): SessionState => ({
    sessionId: null,
    mode: null,
    stage: '',
    status: 'idle',
    currentDocument: null,
    canResume: false,
    messages: []
  }),
  
  actions: {
    async startChat(userInput: string, preferredMode: string = 'auto') {
      this.status = 'processing';
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userInput,
          preferred_mode: preferredMode
        })
      });
      
      const result = await response.json();
      
      this.sessionId = result.session_id;
      this.mode = result.mode;
      this.stage = result.stage;
      this.status = result.stage === 'awaiting_confirmation' 
        ? 'awaiting_confirmation' 
        : 'processing';
      
      if (result.data.plan) {
        this.currentDocument = {
          type: 'plan',
          id: result.data.plan.id,
          content: result.data.plan.content
        };
      }
      
      return result;
    },
    
    async cancelTask(reason: string = 'manual_cancel') {
      if (!this.currentDocument) return;
      
      await fetch(`/api/plans/${this.currentDocument.id}/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason, preserve_state: true })
      });
      
      this.status = 'cancelled';
      this.canResume = true;
    },
    
    async resumeTask() {
      if (!this.sessionId) return;
      
      const result = await resumeSession(this.sessionId);
      
      this.mode = result.resumed_from.mode;
      this.stage = result.resumed_from.stage;
      this.status = 'awaiting_confirmation';
      
      return result;
    },
    
    reset() {
      this.sessionId = null;
      this.mode = null;
      this.stage = '';
      this.status = 'idle';
      this.currentDocument = null;
      this.canResume = false;
    }
  }
});
```

## 错误处理

### Token 超限

```typescript
// 错误拦截器
async function apiCallWithErrorHandling(apiCall: Function) {
  try {
    return await apiCall();
  } catch (error: any) {
    if (error.code === 'TOKEN_LIMIT_EXCEEDED') {
      showNotification({
        type: 'warning',
        title: '请求过长',
        message: '您的请求内容过长，请简化问题或分步处理。',
        actions: [
          { label: '简化问题', handler: () => simplifyInput() },
          { label: '分步处理', handler: () => switchToPlanMode() }
        ]
      });
    }
    throw error;
  }
}
```

### 网络断联

```typescript
// 网络状态监听
window.addEventListener('online', () => {
  checkForResumableSessions();
});

async function checkForResumableSessions() {
  const sessions = await listResumableSessions();
  
  if (sessions.length > 0) {
    showRecoveryDialog(sessions[0]);
  }
}
```

## 组件示例

### 模式选择器组件

```vue
<!-- components/ModeSelector.vue -->
<template>
  <div class="mode-selector">
    <div v-if="recommendedMode !== 'auto'" class="recommendation">
      推荐: {{ modeLabels[recommendedMode] }}
      <span class="confidence">({{ Math.round(confidence * 100) }}%)</span>
    </div>
    
    <select v-model="selectedMode" @change="onModeChange">
      <option value="auto">自动检测</option>
      <option value="simple">简单模式</option>
      <option value="plan">Plan模式</option>
      <option value="spec">Spec模式</option>
    </select>
  </div>
</template>

<script setup>
import { useModeStore } from '@/stores/modeStore';

const modeStore = useModeStore();
const { recommendedMode, selectedMode, confidence } = storeToRefs(modeStore);

const modeLabels = {
  simple: '简单模式',
  plan: 'Plan模式',
  spec: 'Spec模式'
};

function onModeChange() {
  emit('modeChange', selectedMode.value);
}
</script>
```

### Plan 编辑器组件

```vue
<!-- components/PlanEditor.vue -->
<template>
  <div class="plan-editor">
    <div class="toolbar">
      <button @click="save">保存</button>
      <button @click="preview">预览</button>
      <button @click="confirm">确认</button>
      <button @click="cancel">取消</button>
    </div>
    
    <div class="editor-container">
      <div class="section-nav">
        <div 
          v-for="section in sections" 
          :key="section"
          :class="{ active: currentSection === section }"
          @click="selectSection(section)"
        >
          {{ section }}
        </div>
      </div>
      
      <textarea 
        v-model="content"
        class="editor"
        @input="onInput"
      />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  planId: String,
  initialContent: String
});

const content = ref(props.initialContent);
const currentSection = ref('概述');
const sections = ['概述', '目标', '实施步骤', '验收标准', '风险与应对', '备注'];

async function save() {
  await updateSection(props.planId, currentSection.value, content.value);
  showToast('保存成功');
}

async function confirm() {
  await confirmPlan(props.planId, 'proceed');
  emit('confirmed');
}

async function cancel() {
  await cancelPlan(props.planId, 'manual_cancel');
  emit('cancelled');
}
</script>
```

## 性能优化

### 1. 防抖处理

```typescript
// 用户输入防抖
const debouncedDetectMode = debounce(async (input: string) => {
  await modeStore.detectMode(input);
}, 300);
```

### 2. 虚拟滚动

```vue
<!-- 长文档使用虚拟滚动 -->
<VirtualList :items="sections" :item-height="40">
  <template #default="{ item }">
    <SectionItem :section="item" />
  </template>
</VirtualList>
```

### 3. 懒加载

```typescript
// 动态导入编辑器组件
const PlanEditor = defineAsyncComponent(() => 
  import('./components/PlanEditor.vue')
);
```

## 测试建议

### 单元测试

```typescript
// tests/modeStore.spec.ts
describe('Mode Store', () => {
  it('should detect mode correctly', async () => {
    const store = useModeStore();
    await store.detectMode('设计一个系统');
    expect(store.recommendedMode).toBe('plan');
  });
  
  it('should allow mode override', () => {
    const store = useModeStore();
    store.setMode('simple');
    expect(store.selectedMode).toBe('simple');
  });
});
```

### E2E 测试

```typescript
// e2e/plan-mode.spec.ts
test('Plan mode workflow', async ({ page }) => {
  await page.goto('/chat');
  
  // 输入并发送
  await page.fill('[data-testid="chat-input"]', '设计一个系统');
  await page.click('[data-testid="send-button"]');
  
  // 等待规划生成
  await page.waitForSelector('[data-testid="plan-document"]');
  
  // 编辑规划
  await page.click('[data-testid="edit-button"]');
  await page.fill('[data-testid="editor"]', '# 更新后的规划');
  await page.click('[data-testid="save-button"]');
  
  // 确认规划
  await page.click('[data-testid="confirm-button"]');
  
  // 验证进入执行阶段
  await page.waitForSelector('[data-testid="executing-indicator"]');
});
```

## 参考资源

- [API 文档](api/web_api.md)
- [开发者指南](developer_guide.md)
- [部署文档](deployment.md)
- [Vue3 文档](https://vuejs.org/)
- [Pinia 文档](https://pinia.vuejs.org/)

