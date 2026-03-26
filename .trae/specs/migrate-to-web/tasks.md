# Web端迁移任务列表 (Vue 3 版本)

## Task 1: Web后端服务开发
- [ ] 创建FastAPI项目结构
  - [ ] 创建 `web/backend/` 目录结构
  - [ ] 创建 `main.py` FastAPI入口文件
  - [ ] 创建 `api/` 子模块
  - [ ] 创建 `websocket/` 子模块
- [ ] 实现健康检查API
  - [ ] 实现 `GET /api/health` 接口
  - [ ] 返回服务状态和版本信息
- [ ] 实现对话管理API
  - [ ] 实现 `GET /api/conversations` 获取对话列表
  - [ ] 实现 `POST /api/conversations` 创建新对话
  - [ ] 实现 `GET /api/conversations/{id}` 获取对话详情
  - [ ] 实现 `DELETE /api/conversations/{id}` 删除对话
- [ ] 实现流式对话API (SSE)
  - [ ] 实现 `POST /api/chat` SSE流式接口
  - [ ] 集成现有Pipeline执行逻辑
  - [ ] 实现流式输出转换
- [ ] 实现WebSocket通信
  - [ ] 实现 `WS /ws/chat/{conversation_id}` 端点
  - [ ] 实现消息接收和流式响应发送
- [ ] 集成KIMI_API_KEY门控
  - [ ] 服务启动时检查环境变量
  - [ ] 未配置时输出 `需要kimi_api_key` 并退出

## Task 2: Vue 3 前端项目搭建
- [ ] 初始化Vue 3项目
  - [ ] 使用Vite创建项目 `npm create vite@latest frontend -- --template vue`
  - [ ] 配置项目基础结构
  - [ ] 安装基础依赖
- [ ] 配置Element Plus UI库
  - [ ] 安装Element Plus `npm install element-plus`
  - [ ] 配置按需导入或全量导入
  - [ ] 安装Element Plus Icons
- [ ] 配置Pinia状态管理
  - [ ] 安装Pinia `npm install pinia`
  - [ ] 创建store目录结构
  - [ ] 配置Pinia主入口
- [ ] 配置Vue Router
  - [ ] 安装Vue Router `npm install vue-router@4`
  - [ ] 创建路由配置文件
  - [ ] 配置路由守卫
- [ ] 配置Axios和工具函数
  - [ ] 安装Axios `npm install axios`
  - [ ] 创建API封装模块
  - [ ] 创建WebSocket工具类
- [ ] 配置SCSS样式
  - [ ] 安装Sass `npm install -D sass`
  - [ ] 配置全局样式变量
  - [ ] 配置Element Plus主题定制

## Task 3: Vue 组件开发
- [ ] 开发ChatSidebar组件 (侧边栏)
  - [ ] 实现对话列表展示
  - [ ] 实现新对话按钮
  - [ ] 实现对话切换功能
  - [ ] 实现对话删除功能
  - [ ] 添加样式和动画效果
- [ ] 开发ChatMessage组件 (消息项)
  - [ ] 实现用户消息样式（右侧）
  - [ ] 实现AI消息样式（左侧）
  - [ ] 实现消息时间戳显示
  - [ ] 支持Markdown渲染
  - [ ] 添加复制功能
- [ ] 开发ChatInput组件 (输入框)
  - [ ] 实现多行文本输入
  - [ ] 实现发送按钮
  - [ ] 实现Enter快捷键发送
  - [ ] 实现输入状态管理
  - [ ] 添加发送动画效果
- [ ] 开发ChatHeader组件 (顶部栏)
  - [ ] 实现标题显示
  - [ ] 实现当前对话信息
  - [ ] 实现设置入口（预留）
  - [ ] 添加样式美化
- [ ] 开发StreamText组件 (流式文本)
  - [ ] 实现逐字显示效果
  - [ ] 实现光标闪烁动画
  - [ ] 支持内容实时更新
  - [ ] 优化性能避免重渲染
- [ ] 开发ConversationItem组件 (对话项)
  - [ ] 实现对话标题显示
  - [ ] 实现时间显示
  - [ ] 实现选中状态样式
  - [ ] 实现删除按钮
- [ ] 开发EmptyState组件 (空状态)
  - [ ] 实现欢迎界面
  - [ ] 实现快捷功能入口
  - [ ] 添加动画效果

## Task 4: Vue 页面和状态管理开发
- [ ] 开发ChatView主页面
  - [ ] 整合Sidebar、Header、MessageList、Input组件
  - [ ] 实现页面布局（参考千问布局）
  - [ ] 实现响应式适配
  - [ ] 添加页面切换动画
- [ ] 实现Pinia状态管理 (chat store)
  - [ ] 定义state：conversations、currentConversation、messages等
  - [ ] 实现createConversation action
  - [ ] 实现selectConversation action
  - [ ] 实现sendMessage action
  - [ ] 实现appendStreamChunk action
  - [ ] 实现WebSocket连接管理
- [ ] 实现API接口封装
  - [ ] 封装对话管理API
  - [ ] 封装流式对话API
  - [ ] 封装WebSocket连接
- [ ] 实现WebSocket通信逻辑
  - [ ] 实现连接建立和断开
  - [ ] 实现消息发送
  - [ ] 实现流式响应接收
  - [ ] 实现重连机制

## Task 5: 前端构建和部署配置
- [ ] 配置Vite生产构建
  - [ ] 配置build输出目录到backend/static
  - [ ] 配置环境变量
  - [ ] 优化打包体积
- [ ] 配置开发环境代理
  - [ ] 配置API代理到后端
  - [ ] 配置WebSocket代理
- [ ] 配置TypeScript支持（可选）
  - [ ] 安装TypeScript依赖
  - [ ] 配置tsconfig.json
  - [ ] 迁移关键文件到TS

## Task 6: 部署脚本开发
- [ ] 实现环境检查脚本
  - [ ] 检查Python版本(>=3.11)
  - [ ] 检查Node.js版本(>=18)
  - [ ] 检查Conda环境
  - [ ] 检查Python依赖包安装状态
  - [ ] 检查Node依赖包安装状态
  - [ ] 检查KIMI_API_KEY环境变量
- [ ] 实现端口检测与避让
  - [ ] 检测默认端口(8000)是否可用
  - [ ] 自动选择可用端口(8001-8010)
  - [ ] 正确输出实际使用端口
- [ ] 实现Windows启动脚本
  - [ ] 创建 `web/deploy/start.ps1`
  - [ ] 检查并安装Node依赖
  - [ ] 构建前端项目
  - [ ] 激活Conda环境
  - [ ] 启动FastAPI服务
  - [ ] 自动打开浏览器
- [ ] 实现Linux/Mac启动脚本
  - [ ] 创建 `web/deploy/start.sh`
  - [ ] 检查并安装Node依赖
  - [ ] 构建前端项目
  - [ ] 激活Conda环境
  - [ ] 启动FastAPI服务
  - [ ] 输出访问地址

## Task 7: 部署文档编写
- [ ] 编写README.md
  - [ ] 项目简介
  - [ ] 功能特性列表
  - [ ] 技术栈说明
  - [ ] 界面预览说明
- [ ] 编写环境依赖说明
  - [ ] Python版本要求
  - [ ] Node.js版本要求
  - [ ] Conda环境配置
  - [ ] Python依赖包列表
  - [ ] Node依赖包说明
  - [ ] 环境变量配置
- [ ] 编写配置步骤
  - [ ] 代码准备步骤
  - [ ] Python依赖安装
  - [ ] Node依赖安装
  - [ ] 环境变量配置
  - [ ] 启动命令
- [ ] 编写常见问题解决方案
  - [ ] 端口占用问题
  - [ ] Python依赖安装失败
  - [ ] Node依赖安装失败
  - [ ] 前端构建失败
  - [ ] API Key配置问题
  - [ ] 浏览器访问问题

## Task 8: 功能测试与验证
- [ ] 编写API测试
  - [ ] 测试健康检查接口
  - [ ] 测试对话管理接口
  - [ ] 测试流式对话接口
- [ ] 编写前端组件测试（可选）
  - [ ] 测试关键组件渲染
  - [ ] 测试组件交互
- [ ] 编写集成测试
  - [ ] 测试完整对话流程
  - [ ] 测试多轮对话上下文
  - [ ] 测试并发请求处理
- [ ] 功能一致性验证
  - [ ] 对比Web端与控制台输出
  - [ ] 验证调度结果一致性
  - [ ] 验证流式输出效果
- [ ] 性能测试
  - [ ] 测试首字节响应时间
  - [ ] 测试并发处理能力
  - [ ] 测试内存占用情况
  - [ ] 测试前端首屏加载时间

# 任务依赖关系

```
Task 1 (后端服务)
    │
    ├──► Task 2 (Vue项目搭建) ──► Task 3 (组件开发) ──► Task 4 (页面和状态)
    │                                                              │
    │                                                              ▼
    ├──► Task 5 (构建配置) ◄───────────────────────────────────────┘
    │
    ├──► Task 6 (部署脚本)
    │
    └──► Task 7 (部署文档) ──► Task 8 (测试验证)
```

# 并行开发建议

- **可并行**: Task 1 (后端) 和 Task 2 (Vue项目搭建) 可以并行
- **可并行**: Task 3 (组件) 和 Task 6 (部署脚本) 可以并行
- **可并行**: Task 4 (页面) 和 Task 7 (文档) 可以并行
- **必须串行**: Task 3 依赖 Task 2
- **必须串行**: Task 4 依赖 Task 3
- **必须串行**: Task 5 依赖 Task 4
- **必须串行**: Task 8 依赖所有前置任务
