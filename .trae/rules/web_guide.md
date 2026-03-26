---
alwaysApply: false
description: 涉及前端任务，需要改动前端文件时
---

-----------------------------

# 水利智脑 Web端项目指南

## 项目结构

```
web/
├── backend/              # FastAPI后端服务
│   ├── api/              # RESTful API路由
│   │   ├── chat.py       # 对话聊天API（流式SSE）
│   │   └── conversations.py  # 对话管理API
│   ├── websocket/        # WebSocket服务
│   │   └── chat_ws.py    # 实时双向通信
│   ├── static/           # 前端构建产物（自动部署）
│   └── main.py           # FastAPI入口文件
│
├── frontend/             # Vue 3前端项目
│   ├── src/
│   │   ├── components/   # 可复用Vue组件
│   │   │   ├── ChatSidebar.vue      # 侧边栏（对话列表）
│   │   │   ├── ChatMessage.vue      # 消息展示组件
│   │   │   ├── ChatInput.vue        # 输入框组件
│   │   │   ├── ChatHeader.vue       # 顶部栏组件
│   │   │   └── EmptyState.vue       # 空状态欢迎页
│   │   ├── views/        # 页面视图
│   │   │   └── ChatView.vue         # 聊天主页面
│   │   ├── stores/       # Pinia状态管理
│   │   │   └── chat.js                # 对话状态管理
│   │   ├── api/          # API接口封装
│   │   │   └── chat.js                # 聊天相关API
│   │   └── styles/       # 全局SCSS样式
│   ├── package.json      # Node依赖配置
│   └── vite.config.js    # Vite构建配置
│
└── deploy/               # 部署脚本
    ├── start.ps1         # Windows一键启动脚本
    ├── start.sh          # Linux/Mac启动脚本
    └── check_env.py      # 环境检查脚本
```


## 常见问题

### 端口被占用

启动脚本会自动检测并切换到8001-8010范围内的可用端口。



