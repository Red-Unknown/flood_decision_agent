# 水利智脑 Web端

AI工作流Web端界面，基于Vue 3 + FastAPI构建。

## 功能特性

- 💬 多轮对话，上下文保持
- 📝 对话历史管理
- 🚀 流式输出，实时响应
- 📱 响应式布局，支持移动端
- 🎨 美观的UI界面（参考千问布局）
- 🔧 组件化设计，易于扩展

## 技术栈

### 后端
- **框架**: FastAPI
- **WebSocket**: 原生支持
- **CORS**: 跨域支持

### 前端
- **框架**: Vue 3.4+ (Composition API)
- **构建工具**: Vite 5+
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **样式**: SCSS

## 环境要求

- Python >= 3.11
- Node.js >= 18
- Conda环境（推荐）
- KIMI_API_KEY 环境变量

## 快速开始

### 1. 配置环境变量

```powershell
# Windows PowerShell
$env:KIMI_API_KEY="your-api-key"
```

```bash
# Linux/Mac
export KIMI_API_KEY="your-api-key"
```

### 2. 一键启动

```powershell
# Windows
.\web\deploy\start.ps1
```

```bash
# Linux/Mac
chmod +x ./web/deploy/start.sh
./web/deploy/start.sh
```

启动后访问 http://localhost:8000

### 3. 手动启动（开发模式）

#### 安装前端依赖

```bash
cd web/frontend
npm install
```

#### 开发模式（前后端分离）

终端1 - 启动后端：
```bash
python -m web.backend.main
```

终端2 - 启动前端开发服务器：
```bash
cd web/frontend
npm run dev
```

访问 http://localhost:3000

#### 生产模式

```bash
cd web/frontend
npm run build
cd ../..
python -m web.backend.main
```

## 项目结构

```
web/
├── backend/              # FastAPI后端
│   ├── api/              # API路由
│   │   ├── chat.py       # 对话API
│   │   └── conversations.py  # 对话管理
│   ├── websocket/        # WebSocket服务
│   │   └── chat_ws.py
│   ├── static/           # 前端构建产物
│   └── main.py           # 入口文件
├── frontend/             # Vue 3前端
│   ├── src/
│   │   ├── components/   # 可复用组件
│   │   ├── views/        # 页面视图
│   │   ├── stores/       # Pinia状态管理
│   │   ├── api/          # API接口封装
│   │   └── styles/       # 全局样式
│   ├── package.json
│   └── vite.config.js
└── deploy/               # 部署脚本
    ├── start.ps1         # Windows启动脚本
    ├── start.sh          # Linux/Mac启动脚本
    └── check_env.py      # 环境检查脚本
```

## API接口

### REST API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/health | 健康检查 |
| GET | /api/conversations | 获取对话列表 |
| POST | /api/conversations | 创建新对话 |
| GET | /api/conversations/{id} | 获取对话详情 |
| DELETE | /api/conversations/{id} | 删除对话 |
| POST | /api/chat | 发送消息（流式） |
| GET | /api/conversations/{id}/messages | 获取消息历史 |

### WebSocket API

```
WS /ws/chat/{conversation_id}
```

消息格式：
```json
// 发送
{"type": "message", "content": "用户输入"}

// 接收
{"type": "chunk", "content": "片段内容", "accumulated": "累计内容"}
{"type": "complete", "content": "完整内容"}
{"type": "error", "content": "错误信息"}
```

## 常见问题

### 端口被占用

启动脚本会自动检测并切换到可用端口（8000-8010范围）。
如需指定其他端口：

```powershell
.\web\deploy\start.ps1 -Port 8080
```

### 前端依赖安装失败

尝试使用淘宝镜像：
```bash
cd web/frontend
npm config set registry https://registry.npmmirror.com
npm install
```

### 前端构建失败

检查Node.js版本：
```bash
node --version  # 需要 >= 18
```

### API Key配置问题

确保环境变量正确设置：
```powershell
$env:KIMI_API_KEY  # 查看当前值
```

### 浏览器无法访问

1. 检查防火墙设置
2. 确认服务已启动（查看控制台输出）
3. 尝试使用 http://127.0.0.1:8000 访问

## 开发指南

### 添加新组件

在 `web/frontend/src/components/` 目录下创建Vue组件，遵循以下规范：

1. 使用Composition API
2. 组件名使用PascalCase
3. 样式使用scoped + SCSS
4. 添加必要的props和emits定义

### 添加新API

在 `web/frontend/src/api/chat.js` 中添加API函数：

```javascript
export const newApi = async (params) => {
  const response = await apiClient.post('/api/new-endpoint', params)
  return response.data
}
```

### 状态管理

使用Pinia管理全局状态，参考 `web/frontend/src/stores/chat.js`。

## 许可证

MIT
