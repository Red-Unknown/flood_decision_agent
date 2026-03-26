# AI工作流Web端迁移规格说明

## 背景与目标

### Why
当前AI工作流（flood_decision_agent）以控制台交互为主，用户体验受限，不利于推广使用。迁移至Web端可以提供更友好的用户界面、支持多设备访问、便于功能扩展和集成。

### 参考设计
参考通义千问Web端布局：
- 左侧边栏：对话历史列表、新对话按钮
- 中央区域：聊天界面、输入框、功能快捷入口
- 顶部：模型选择、设置入口
- 支持流式输出、多轮对话、上下文保持

## What Changes

### 新增组件
1. **Web后端服务** (FastAPI)
   - RESTful API 设计
   - WebSocket 支持实时通信
   - 对话状态管理
   - 与现有Pipeline集成

2. **Web前端界面** (Vue 3 + Vite)
   - 基于Vue 3 Composition API开发
   - 组件化设计，便于复用
   - 响应式布局设计
   - 现代化UI组件库(Element Plus)
   - 流式消息展示

3. **部署脚本**
   - 端口自动检测与避让
   - 环境检查与自动配置
   - 一键启动/停止服务

4. **部署文档**
   - 环境依赖说明
   - 配置步骤
   - 常见问题解决方案

### 修改组件
- 无破坏性修改，保持现有控制台功能兼容

## 影响范围

### 受影响模块
- `src/flood_decision_agent/app/` - 新增Web服务集成
- `examples/` - 新增Web启动示例
- `scripts/` - 新增部署脚本
- `docs/` - 新增部署文档

### 新增模块
- `web/` - Web服务根目录
  - `backend/` - FastAPI后端
  - `frontend/` - Vue3前端项目
  - `deploy/` - 部署脚本

## 需求规格

### Requirement 1: Web后端服务

#### Scenario 1.1: 对话API
- **GIVEN** 用户通过Web界面发送消息
- **WHEN** 调用 `/api/chat` 接口
- **THEN** 返回流式响应，支持SSE (Server-Sent Events)

#### Scenario 1.2: 对话历史管理
- **GIVEN** 用户有历史对话
- **WHEN** 调用 `/api/conversations` 接口
- **THEN** 返回对话列表，支持分页

#### Scenario 1.3: WebSocket实时通信
- **GIVEN** 用户建立WebSocket连接
- **WHEN** 发送消息
- **THEN** 实时接收流式响应

#### Scenario 1.4: KIMI_API_KEY 门控
- **GIVEN** 服务启动时
- **WHEN** 未配置 KIMI_API_KEY 环境变量
- **THEN** 输出 `需要kimi_api_key` 并以退出码 1 结束

### Requirement 2: Web前端界面 (Vue 3)

#### Scenario 2.1: 主界面布局
- **GIVEN** 用户访问Web应用
- **WHEN** 页面加载完成
- **THEN** 显示类似千问的布局：左侧对话列表、中央聊天区域

#### Scenario 2.2: 新对话
- **GIVEN** 用户点击"新对话"按钮
- **WHEN** 触发点击事件
- **THEN** 清空当前对话，创建新会话

#### Scenario 2.3: 历史对话列表
- **GIVEN** 用户有多个历史对话
- **WHEN** 查看左侧边栏
- **THEN** 显示对话标题列表，支持点击切换

#### Scenario 2.4: 流式消息展示
- **GIVEN** AI正在生成回复
- **WHEN** 接收流式数据
- **THEN** 实时更新消息内容，显示打字效果

#### Scenario 2.5: 多轮对话支持
- **GIVEN** 用户正在进行对话
- **WHEN** 发送追问或补充
- **THEN** 保持上下文，正确识别追问/新话题

#### Scenario 2.6: Vue组件复用
- **GIVEN** 需要开发新功能
- **WHEN** 使用现有组件
- **THEN** 组件可复用，减少重复代码

### Requirement 3: 部署脚本

#### Scenario 3.1: 端口自动检测
- **GIVEN** 默认端口(8000)被占用
- **WHEN** 运行部署脚本
- **THEN** 自动检测并选择可用端口(8001-8010范围)

#### Scenario 3.2: 环境检查
- **GIVEN** 运行部署脚本
- **WHEN** 检查环境依赖
- **THEN** 验证Python版本、依赖包、环境变量、Node.js版本

#### Scenario 3.3: 一键启动
- **GIVEN** 环境配置正确
- **WHEN** 运行启动脚本
- **THEN** 同时启动前后端服务，输出访问地址

### Requirement 4: 部署文档

#### Scenario 4.1: 环境依赖说明
- **GIVEN** 用户阅读部署文档
- **WHEN** 查看环境要求章节
- **THEN** 清晰了解Python版本、Node.js版本、系统要求、依赖包

#### Scenario 4.2: 配置步骤
- **GIVEN** 用户按照文档部署
- **WHEN** 执行配置步骤
- **THEN** 能够成功启动Web服务

#### Scenario 4.3: 常见问题
- **GIVEN** 用户遇到部署问题
- **WHEN** 查看常见问题章节
- **THEN** 找到对应问题的解决方案

### Requirement 5: 功能完整性验证

#### Scenario 5.1: 与控制台功能一致
- **GIVEN** Web端发送调度请求
- **WHEN** 执行Pipeline
- **THEN** 输出结果与控制台版本一致

#### Scenario 5.2: 性能表现
- **GIVEN** 并发用户访问
- **WHEN** 同时发起多个请求
- **THEN** 响应时间在可接受范围内(<5s首字节)

## 技术选型

### 后端
- **框架**: FastAPI (异步支持、自动API文档)
- **WebSocket**: 原生支持
- **CORS**: 跨域支持

### 前端
- **框架**: Vue 3.4+ (Composition API)
- **构建工具**: Vite 5+
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **样式**: SCSS + Element Plus主题定制
- **图标**: Element Plus Icons

### 部署
- **后端服务器**: Uvicorn (ASGI)
- **前端构建**: Vite生产构建
- **脚本**: PowerShell (Windows) + Bash (Linux/Mac)

## 接口设计

### REST API

```
GET  /api/health          - 健康检查
GET  /api/conversations   - 获取对话列表
POST /api/conversations   - 创建新对话
GET  /api/conversations/{id} - 获取对话详情
POST /api/chat            - 发送消息 (SSE流式返回)
DELETE /api/conversations/{id} - 删除对话
```

### WebSocket API

```
WS /ws/chat/{conversation_id}
  - 发送: {"message": "用户输入"}
  - 接收: {"type": "chunk", "content": "..."}
  - 接收: {"type": "complete", "result": {...}}
```

## 目录结构

```
web/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI入口
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py          # 对话API
│   │   └── conversations.py # 对话管理API
│   ├── websocket/
│   │   └── chat_ws.py       # WebSocket处理
│   └── static/              # 前端构建产物
│
├── frontend/                # Vue 3项目
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.js          # 入口文件
│   │   ├── App.vue          # 根组件
│   │   ├── router/
│   │   │   └── index.js     # 路由配置
│   │   ├── stores/
│   │   │   └── chat.js      # Pinia状态管理
│   │   ├── components/      # 可复用组件
│   │   │   ├── ChatSidebar.vue      # 侧边栏组件
│   │   │   ├── ChatMessage.vue      # 消息组件
│   │   │   ├── ChatInput.vue        # 输入框组件
│   │   │   ├── ChatHeader.vue       # 顶部栏组件
│   │   │   ├── StreamText.vue       # 流式文本组件
│   │   │   └── ConversationItem.vue # 对话项组件
│   │   ├── views/           # 页面视图
│   │   │   └── ChatView.vue # 聊天主页面
│   │   ├── api/             # API接口封装
│   │   │   └── chat.js
│   │   └── utils/           # 工具函数
│   │       └── websocket.js
│   └── public/              # 静态资源
│
├── deploy/
│   ├── start.ps1            # Windows启动脚本
│   ├── start.sh             # Linux/Mac启动脚本
│   └── check_env.py         # 环境检查脚本
│
└── README.md                # 部署文档
```

## Vue组件设计

### 组件清单

| 组件名 | 用途 | 复用性 |
|--------|------|--------|
| ChatSidebar | 左侧边栏，包含对话列表和新对话按钮 | 中 |
| ChatMessage | 单条消息展示（用户/AI） | 高 |
| ChatInput | 消息输入框，支持多行和发送 | 高 |
| ChatHeader | 顶部标题栏 | 中 |
| StreamText | 流式文本展示组件 | 高 |
| ConversationItem | 对话列表单项 | 高 |
| LoadingIndicator | 加载状态指示器 | 高 |
| EmptyState | 空状态提示 | 高 |

### 状态管理 (Pinia)

```javascript
// stores/chat.js
export const useChatStore = defineStore('chat', {
  state: () => ({
    conversations: [],      // 对话列表
    currentConversation: null,  // 当前对话
    messages: [],           // 当前对话消息
    isStreaming: false,     // 是否正在流式输出
    isConnected: false,     // WebSocket连接状态
  }),
  actions: {
    createConversation(),   // 创建新对话
    selectConversation(),   // 选择对话
    sendMessage(),          // 发送消息
    appendStreamChunk(),    // 追加流式内容
  }
})
```
